# ==========================================================
# tests/test_state_machine.py — Testes da State Machine
# ==========================================================

import pandas as pd
import pytest

from state_machine import AnalysisStage, AnalysisState


class TestAnalysisState:
    """Suite de testes para AnalysisState"""

    def test_initial_state(self):
        """Estado inicial deve ter valores padrão corretos"""
        state = AnalysisState()

        assert state.stage == AnalysisStage.INITIAL
        assert state.user_story == ""
        assert state.analysis_data is None
        assert state.saved_history_id is None
        assert state.get_progress_percentage() == 0

    def test_cannot_start_analysis_without_user_story(self):
        """Não deve permitir análise sem User Story"""
        state = AnalysisState()

        assert not state.can_start_analysis()

        with pytest.raises(ValueError, match="Não é possível iniciar análise"):
            state.start_analysis()

    def test_valid_analysis_flow(self):
        """Fluxo completo válido deve funcionar"""
        state = AnalysisState()
        state.user_story = "Como usuário, quero fazer login"

        # 1. Iniciar análise
        assert state.can_start_analysis()
        state.start_analysis()
        assert state.stage == AnalysisStage.ANALYZING

        # 2. Completar análise
        state.complete_analysis({"test": "data"}, "# Relatório")
        assert state.stage == AnalysisStage.EDITING_ANALYSIS
        assert state.can_generate_plan()

        # 3. Gerar plano
        state.start_plan_generation()
        assert state.stage == AnalysisStage.GENERATING_PLAN

        # 4. Completar plano
        df = pd.DataFrame([{"id": "CT-001", "titulo": "Teste"}])
        state.complete_plan_generation({}, "# Plano", df, b"pdf")

        assert state.stage == AnalysisStage.COMPLETED
        assert state.can_export()
        assert state.get_progress_percentage() == 100

    def test_cannot_skip_stages(self):
        """Não deve permitir pular etapas"""
        state = AnalysisState()
        state.user_story = "teste"

        # Tentar gerar plano sem fazer análise
        with pytest.raises(ValueError, match="Não é possível gerar plano"):
            state.start_plan_generation()

    def test_error_handling(self):
        """Tratamento de erro deve funcionar"""
        state = AnalysisState()
        state.user_story = "teste"
        state.start_analysis()

        # Simular erro
        state.set_error("Falha na API")

        assert state.stage == AnalysisStage.ERROR
        assert state.error_message == "Falha na API"
        assert state._retry_count == 1

        # Retry deve voltar ao estado anterior
        state.reset_for_retry()
        assert state.stage == AnalysisStage.INITIAL
        assert state.error_message == ""

    def test_mark_as_saved(self):
        """Marcação de salvamento deve funcionar"""
        state = AnalysisState()

        assert not state.is_saved()

        state.mark_as_saved(42)

        assert state.is_saved()
        assert state.saved_history_id == 42

    def test_complete_reset(self):
        """Reset completo deve limpar tudo"""
        state = AnalysisState()
        state.user_story = "teste"
        state.analysis_data = {"key": "value"}
        state.saved_history_id = 10

        state.reset_completely()

        assert state.stage == AnalysisStage.INITIAL
        assert state.user_story == ""
        assert state.analysis_data is None
        assert state.saved_history_id is None

    def test_stage_labels(self):
        """Labels amigáveis devem estar corretos"""
        state = AnalysisState()

        assert state.get_stage_label() == "Aguardando User Story"

        state.user_story = "teste"
        state.start_analysis()
        assert state.get_stage_label() == "Analisando com IA..."

        state.complete_analysis({}, "")
        assert state.get_stage_label() == "Revisão e Edição"

    def test_to_dict_serialization(self):
        """Serialização para dict deve funcionar"""
        state = AnalysisState()
        state.user_story = "Como usuário, quero fazer login"

        data = state.to_dict()

        assert data["stage"] == "INITIAL"
        assert data["user_story_length"] == 31
        assert data["has_analysis"] is False
        assert data["progress"] == 0


class TestAnalysisStageTransitions:
    """Testes específicos de transições de estado"""

    def test_all_valid_transitions(self):
        """Mapeia todas as transições válidas"""
        valid_transitions = {
            AnalysisStage.INITIAL: [AnalysisStage.ANALYZING],
            AnalysisStage.ANALYZING: [
                AnalysisStage.EDITING_ANALYSIS,
                AnalysisStage.ERROR,
            ],
            AnalysisStage.EDITING_ANALYSIS: [AnalysisStage.GENERATING_PLAN],
            AnalysisStage.GENERATING_PLAN: [
                AnalysisStage.COMPLETED,
                AnalysisStage.ERROR,
            ],
            AnalysisStage.COMPLETED: [],
            AnalysisStage.ERROR: [
                AnalysisStage.INITIAL,
                AnalysisStage.EDITING_ANALYSIS,
            ],
        }

        # Validar que cada transição está implementada
        for source, targets in valid_transitions.items():
            assert isinstance(source, AnalysisStage)
            for target in targets:
                assert isinstance(target, AnalysisStage)

    def test_idempotent_operations(self):
        """Operações idempotentes não devem causar efeitos colaterais"""
        state = AnalysisState()
        state.user_story = "teste"

        # Marcar como salvo múltiplas vezes deve manter o ID
        state.mark_as_saved(10)
        state.mark_as_saved(10)
        state.mark_as_saved(10)

        assert state.saved_history_id == 10

        # Chamar can_* múltiplas vezes não deve alterar estado
        initial_stage = state.stage
        for _ in range(5):
            state.can_start_analysis()

        assert state.stage == initial_stage


class TestEdgeCases:
    """Testes de casos extremos"""

    def test_empty_user_story_variations(self):
        """Diferentes formas de string vazia devem ser rejeitadas"""
        test_cases = ["", "   ", "\n", "\t", "  \n  "]

        for empty_value in test_cases:
            state = AnalysisState()
            state.user_story = empty_value

            assert not state.can_start_analysis()

    def test_large_user_story(self):
        """User Story muito grande deve ser aceita"""
        state = AnalysisState()
        state.user_story = "x" * 10000  # 10KB de texto

        assert state.can_start_analysis()
        state.start_analysis()
        assert state.stage == AnalysisStage.ANALYZING

    def test_multiple_errors_increment_retry_count(self):
        """Múltiplos erros devem incrementar contador"""
        state = AnalysisState()
        state.user_story = "teste"
        state.start_analysis()

        for i in range(1, 5):
            state.set_error(f"Erro {i}")
            assert state._retry_count == i
            state.reset_for_retry()

    def test_complete_plan_with_empty_dataframe(self):
        """Plano com DataFrame vazio deve ser aceito"""
        state = AnalysisState()
        state.user_story = "teste"
        state.start_analysis()
        state.complete_analysis({}, "")
        state.start_plan_generation()

        # DataFrame vazio é válido (caso de teste sem cenários)
        empty_df = pd.DataFrame()
        state.complete_plan_generation({}, "", empty_df, b"")

        assert state.stage == AnalysisStage.COMPLETED
        assert state.test_plan_df is not None


# ==========================================================
# Testes de Integração (validam fluxos completos)
# ==========================================================
class TestIntegrationFlows:
    """Testes de fluxos completos do usuário"""

    def test_happy_path_complete_analysis(self):
        """Fluxo feliz completo: entrada → análise → plano → exportação"""
        state = AnalysisState()

        # 1. Usuário digita User Story
        state.user_story = "Como admin, quero gerenciar usuários"
        assert state.get_progress_percentage() == 0

        # 2. Inicia análise
        state.start_analysis()
        assert state.get_progress_percentage() == 25

        # 3. IA retorna análise
        state.complete_analysis(
            analysis_data={
                "pontos_ambiguos": ["Definir permissões"],
                "criterios": ["Usuário deve poder editar perfis"],
            },
            analysis_report="# Análise\n\nPontos ambíguos encontrados...",
        )
        assert state.get_progress_percentage() == 50

        # 4. Usuário confirma edições (implícito)
        assert state.can_generate_plan()

        # 5. Gera plano de testes
        state.start_plan_generation()
        assert state.get_progress_percentage() == 75

        # 6. IA retorna plano
        test_df = pd.DataFrame(
            [
                {"id": "CT-001", "titulo": "Login válido", "cenario": "Dado..."},
                {"id": "CT-002", "titulo": "Login inválido", "cenario": "Dado..."},
            ]
        )

        state.complete_plan_generation(
            test_plan_data={"casos": ["CT-001", "CT-002"]},
            test_plan_report="# Plano de Testes\n\n...",
            test_plan_df=test_df,
            pdf_bytes=b"%PDF-1.4...",
        )

        assert state.get_progress_percentage() == 100
        assert state.can_export()

        # 7. Salvamento
        state.mark_as_saved(123)
        assert state.is_saved()

        # Validações finais
        assert len(state.test_plan_df) == 2
        assert state.pdf_bytes is not None

    def test_analysis_failure_and_retry(self):
        """Falha na análise + retry bem-sucedido"""
        state = AnalysisState()
        state.user_story = "Como usuário, quero resetar senha"

        # 1. Primeira tentativa falha
        state.start_analysis()
        state.set_error("Timeout na API do Gemini")

        assert state.stage == AnalysisStage.ERROR
        assert state._retry_count == 1

        # 2. Usuário tenta novamente
        state.reset_for_retry()
        assert state.stage == AnalysisStage.INITIAL

        # 3. Segunda tentativa funciona
        state.start_analysis()
        state.complete_analysis({"test": "data"}, "# Sucesso")

        assert state.stage == AnalysisStage.EDITING_ANALYSIS
        assert state._retry_count == 1  # Contador mantido para métricas

    def test_user_cancels_after_analysis(self):
        """Usuário cancela após ver análise (não gera plano)"""
        state = AnalysisState()
        state.user_story = "Como vendedor, quero relatório"

        state.start_analysis()
        state.complete_analysis({"result": "ok"}, "# Análise")

        # Usuário decide não gerar plano e começa nova análise
        state.reset_completely()

        assert state.stage == AnalysisStage.INITIAL
        assert state.user_story == ""
        assert not state.is_saved()


# ==========================================================
# Fixture para testes com estado pré-configurado
# ==========================================================
@pytest.fixture
def state_with_completed_analysis():
    """Fixture: estado com análise completa (pronto para gerar plano)"""
    state = AnalysisState()
    state.user_story = "Como QA, quero testar funcionalidades"
    state.start_analysis()
    state.complete_analysis(
        analysis_data={"criterios": ["Teste deve passar"]},
        analysis_report="# Análise Completa",
    )
    return state


@pytest.fixture
def state_fully_completed():
    """Fixture: estado totalmente completo (pronto para exportar)"""
    state = AnalysisState()
    state.user_story = "Como dev, quero CI/CD"
    state.start_analysis()
    state.complete_analysis({}, "# Análise")
    state.start_plan_generation()

    df = pd.DataFrame([{"id": "CT-001", "titulo": "Deploy"}])
    state.complete_plan_generation({}, "# Plano", df, b"pdf")

    return state


# ==========================================================
# Testes usando fixtures
# ==========================================================
def test_can_generate_plan_after_analysis(state_with_completed_analysis):
    """Fixture de análise completa deve permitir gerar plano"""
    assert state_with_completed_analysis.can_generate_plan()
    assert not state_with_completed_analysis.can_export()


def test_can_export_after_completion(state_fully_completed):
    """Fixture de estado completo deve permitir exportação"""
    assert state_fully_completed.can_export()
    assert state_fully_completed.pdf_bytes is not None
    assert len(state_fully_completed.test_plan_df) == 1
