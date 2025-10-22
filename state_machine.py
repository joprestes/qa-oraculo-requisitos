# ==========================================================
# state_machine.py — Máquina de Estados do QA Oráculo
# ==========================================================
# 📘 Define o ciclo de vida completo de uma análise de User Story
#    usando enums e dataclasses para garantir transições seguras.
#
# 🎯 Princípios:
#   • Estado único e previsível
#   • Transições explícitas e validadas
#   • Imutabilidade onde possível
#   • Fácil debug e testabilidade
# ==========================================================

from dataclasses import dataclass, field
from enum import Enum, auto

import pandas as pd


# ==========================================================
# 🎭 Estados Possíveis da Análise
# ==========================================================
class AnalysisStage(Enum):
    """
    Estados válidos do fluxo de análise.

    Transições válidas:
    INITIAL → ANALYZING → EDITING_ANALYSIS → GENERATING_PLAN → COMPLETED

    Qualquer estado pode ir para ERROR em caso de falha.
    """

    INITIAL = auto()  # Estado inicial (formulário vazio)
    ANALYZING = auto()  # IA está analisando a User Story
    EDITING_ANALYSIS = auto()  # Usuário está revisando/editando análise
    GENERATING_PLAN = auto()  # IA está gerando plano de testes
    COMPLETED = auto()  # Análise concluída (pronta para exportar)
    ERROR = auto()  # Erro crítico (permite retry)


# ==========================================================
# 📦 Estado Global da Análise
# ==========================================================
@dataclass
class AnalysisState:
    """
    Representa o estado completo de uma análise em andamento.

    Attributes:
        stage: Estágio atual do fluxo
        user_story: Texto da User Story original
        analysis_data: Dados estruturados da análise (JSON da IA)
        analysis_report: Relatório formatado em Markdown
        test_plan_data: Casos de teste estruturados (lista de dicts)
        test_plan_report: Plano de testes em Markdown
        test_plan_df: DataFrame com casos de teste editáveis
        pdf_bytes: PDF gerado (bytes)
        saved_history_id: ID do registro no banco (None se não salvo)
        error_message: Mensagem de erro (se stage == ERROR)
    """

    stage: AnalysisStage = AnalysisStage.INITIAL
    user_story: str = ""
    analysis_data: dict | None = None
    analysis_report: str = ""
    test_plan_data: dict | None = None
    test_plan_report: str = ""
    test_plan_df: pd.DataFrame | None = None
    pdf_bytes: bytes | None = None
    saved_history_id: int | None = None
    error_message: str = ""

    # Metadados internos (não expostos na UI)
    _retry_count: int = field(default=0, repr=False)
    _last_updated: str | None = field(default=None, repr=False)

    # ==========================================================
    # 🔒 Validações de Transição
    # ==========================================================

    def can_start_analysis(self) -> bool:
        """Valida se pode iniciar análise (tem US e está no estado correto)"""
        return self.stage == AnalysisStage.INITIAL and self.user_story.strip() != ""

    def can_edit_analysis(self) -> bool:
        """Valida se pode editar análise (análise já foi gerada)"""
        return self.stage == AnalysisStage.ANALYZING and self.analysis_data is not None

    def can_generate_plan(self) -> bool:
        """Valida se pode gerar plano de testes (análise foi confirmada)"""
        return (
            self.stage == AnalysisStage.EDITING_ANALYSIS
            and self.analysis_data is not None
        )

    def can_export(self) -> bool:
        """Valida se pode exportar (análise está completa)"""
        return self.stage == AnalysisStage.COMPLETED

    def is_saved(self) -> bool:
        """Verifica se a análise já foi salva no histórico"""
        return self.saved_history_id is not None

    # ==========================================================
    # 🔄 Transições de Estado
    # ==========================================================

    def start_analysis(self):
        """Inicia análise da User Story"""
        if not self.can_start_analysis():
            raise ValueError(
                f"Não é possível iniciar análise no estado {self.stage.name}"
            )
        self.stage = AnalysisStage.ANALYZING
        self.error_message = ""

    def complete_analysis(self, analysis_data: dict, analysis_report: str):
        """Marca análise como concluída e pronta para edição"""
        if self.stage != AnalysisStage.ANALYZING:
            raise ValueError(
                f"Não é possível completar análise no estado {self.stage.name}"
            )

        self.analysis_data = analysis_data
        self.analysis_report = analysis_report
        self.stage = AnalysisStage.EDITING_ANALYSIS

    def confirm_analysis_edits(self):
        """Confirma edições da análise (mantém no mesmo estado)"""
        if not self.can_generate_plan():
            raise ValueError(
                f"Não é possível confirmar edições no estado {self.stage.name}"
            )
        # Estado permanece EDITING_ANALYSIS até usuário pedir plano

    def start_plan_generation(self):
        """Inicia geração do plano de testes"""
        if not self.can_generate_plan():
            raise ValueError(f"Não é possível gerar plano no estado {self.stage.name}")
        self.stage = AnalysisStage.GENERATING_PLAN

    def complete_plan_generation(
        self,
        test_plan_data: dict,
        test_plan_report: str,
        test_plan_df: pd.DataFrame,
        pdf_bytes: bytes,
    ):
        """Marca plano como concluído"""
        if self.stage != AnalysisStage.GENERATING_PLAN:
            raise ValueError(
                f"Não é possível completar plano no estado {self.stage.name}"
            )

        self.test_plan_data = test_plan_data
        self.test_plan_report = test_plan_report
        self.test_plan_df = test_plan_df
        self.pdf_bytes = pdf_bytes
        self.stage = AnalysisStage.COMPLETED

    def mark_as_saved(self, history_id: int):
        """Registra ID do histórico após salvamento"""
        self.saved_history_id = history_id

    def set_error(self, error_message: str):
        """Marca estado como erro"""
        self.stage = AnalysisStage.ERROR
        self.error_message = error_message
        self._retry_count += 1

    def reset_for_retry(self):
        """Reseta para o estado anterior ao erro (permite retry)"""
        if self.stage != AnalysisStage.ERROR:
            raise ValueError("Só é possível fazer retry após erro")

        # Volta para o último estado válido
        if self.analysis_data is None:
            self.stage = AnalysisStage.INITIAL
        elif self.test_plan_df is None:
            self.stage = AnalysisStage.EDITING_ANALYSIS
        else:
            self.stage = AnalysisStage.COMPLETED

        self.error_message = ""

    def reset_completely(self):
        """Reseta tudo para começar nova análise"""
        self.__init__()  # Reinicializa com valores padrão

    # ==========================================================
    # 🔍 Helpers de Inspeção
    # ==========================================================

    def get_progress_percentage(self) -> int:
        """Retorna progresso da análise (0-100%)"""
        progress_map = {
            AnalysisStage.INITIAL: 0,
            AnalysisStage.ANALYZING: 25,
            AnalysisStage.EDITING_ANALYSIS: 50,
            AnalysisStage.GENERATING_PLAN: 75,
            AnalysisStage.COMPLETED: 100,
            AnalysisStage.ERROR: 0,
        }
        return progress_map[self.stage]

    def get_stage_label(self) -> str:
        """Retorna label amigável do estágio atual"""
        labels = {
            AnalysisStage.INITIAL: "Aguardando User Story",
            AnalysisStage.ANALYZING: "Analisando com IA...",
            AnalysisStage.EDITING_ANALYSIS: "Revisão e Edição",
            AnalysisStage.GENERATING_PLAN: "Gerando Plano de Testes...",
            AnalysisStage.COMPLETED: "Análise Concluída",
            AnalysisStage.ERROR: "Erro na Execução",
        }
        return labels[self.stage]

    def to_dict(self) -> dict:
        """Serializa estado para dicionário (útil para debug/logs)"""
        return {
            "stage": self.stage.name,
            "user_story_length": len(self.user_story),
            "has_analysis": self.analysis_data is not None,
            "has_plan": self.test_plan_df is not None,
            "is_saved": self.is_saved(),
            "progress": self.get_progress_percentage(),
        }


# ==========================================================
# 🧪 Testes de Validação (executar com: python state_machine.py)
# ==========================================================
if __name__ == "__main__":
    print("🧪 Testando State Machine...\n")

    # Teste 1: Fluxo completo válido
    state = AnalysisState()
    state.user_story = "Como usuário, quero fazer login"

    assert state.can_start_analysis()
    state.start_analysis()
    assert state.stage == AnalysisStage.ANALYZING

    state.complete_analysis({"test": "data"}, "# Relatório")
    assert state.can_generate_plan()

    state.start_plan_generation()
    state.complete_plan_generation({}, "", pd.DataFrame(), b"pdf")
    assert state.can_export()

    print("✅ Teste 1: Fluxo completo válido - PASSOU")

    # Teste 2: Transição inválida deve falhar
    state2 = AnalysisState()
    try:
        state2.start_plan_generation()  # Sem análise
        print("❌ Teste 2: FALHOU - Permitiu transição inválida")
    except ValueError:
        print("✅ Teste 2: Validação de transição - PASSOU")

    # Teste 3: Reset completo
    state.reset_completely()
    assert state.stage == AnalysisStage.INITIAL
    assert state.user_story == ""
    print("✅ Teste 3: Reset completo - PASSOU")

    print("\n🎉 Todos os testes passaram!")
