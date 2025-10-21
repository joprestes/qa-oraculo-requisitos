# ==========================================================
# state_manager.py — Gerenciamento de Estado do Streamlit
# ==========================================================
# 📘 Integra a State Machine com o session_state do Streamlit
#    Versão 2.0 - Refatorado para usar AnalysisState
# ==========================================================

import streamlit as st

from state_machine import AnalysisStage, AnalysisState

# ==========================================================
# 🔑 Chave do estado global no session_state
# ==========================================================
_STATE_KEY = "qa_oraculo_state"


# ==========================================================
# 🚀 Funções Públicas de Acesso ao Estado
# ==========================================================


def initialize_state():
    """
    Inicializa o estado global da aplicação.

    IMPORTANTE: Deve ser chamado SEMPRE no início do app.py
    (antes de qualquer acesso ao estado).

    Se o estado já existe, não faz nada (idempotente).
    """
    if _STATE_KEY not in st.session_state:
        st.session_state[_STATE_KEY] = AnalysisState()
        print("🆕 Estado inicializado com valores padrão")

    defaults = {
        "analysis_finished": False,
        "analysis_state": None,
        "test_plan_report": None,
        "test_plan_df": None,
        "pdf_report_bytes": None,
        "show_generate_plan_button": False,
        "user_story_input": "",
        "area_path_input": "",
        "assigned_to_input": "",
        "jira_priority": "Medium",
        "jira_labels": "QA-Oraculo",
        "jira_description": "Caso de teste gerado pelo QA Oráculo.",
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    # Migração de estados legados (compatibilidade retroativa)
    _migrate_legacy_state()


def get_state() -> AnalysisState:
    """
    Retorna o estado global atual.

    Raises:
        RuntimeError: Se o estado não foi inicializado (dev error)

    Returns:
        AnalysisState: Instância única do estado da sessão
    """
    if _STATE_KEY not in st.session_state:
        raise RuntimeError(
            "Estado não inicializado! Chame initialize_state() no início do app."
        )

    return st.session_state[_STATE_KEY]


def reset_session():
    """
    Limpa COMPLETAMENTE o estado da sessão.

    ⚠️ ATENÇÃO: Esta ação é irreversível e remove:
    - Estado da análise atual
    - Flags de controle
    - Dados temporários

    Use para:
    - Botão "Nova Análise"
    - Reset após erro crítico
    """
    if _STATE_KEY in st.session_state:
        st.session_state[_STATE_KEY].reset_completely()
        print("🔄 Estado resetado para nova análise")

    preserved_prefixes = ("FormSubmitter:",)

    for key in list(st.session_state.keys()):
        if key == _STATE_KEY:
            continue
        if any(key.startswith(prefix) for prefix in preserved_prefixes):
            continue
        del st.session_state[key]


def update_user_story(user_story: str):
    """Atualiza a User Story no estado (helper de conveniência)"""
    state = get_state()
    state.user_story = user_story.strip()


def is_analysis_in_progress() -> bool:
    """Verifica se há uma análise em andamento"""
    state = get_state()
    return state.stage not in [
        AnalysisStage.INITIAL,
        AnalysisStage.COMPLETED,
        AnalysisStage.ERROR,
    ]


# ==========================================================
# 🔧 Funções Internas (Migração e Debug)
# ==========================================================


def _migrate_legacy_state():
    """
    Migra dados de versões antigas do app para o novo formato.

    CONTEXTO: Versões antigas usavam múltiplas flags soltas no session_state.
    Esta função detecta e converte automaticamente para AnalysisState.

    Pode ser removida após 100% dos usuários migrarem.
    """
    # Se já tem estado novo, não precisa migrar
    if _STATE_KEY in st.session_state:
        return

    # Detecta flags legadas
    legacy_data = {
        "user_story": st.session_state.get("user_story_input", ""),
        "analysis_state": st.session_state.get("analysis_state"),
        "test_plan_report": st.session_state.get("test_plan_report"),
        "test_plan_df": st.session_state.get("test_plan_df"),
        "pdf_report_bytes": st.session_state.get("pdf_report_bytes"),
        "analysis_finished": st.session_state.get("analysis_finished", False),
    }

    # Se não há dados legados, não faz nada
    if not any(legacy_data.values()):
        return

    print("🔄 Migrando estado legado para novo formato...")

    # Cria novo estado a partir dos dados antigos
    new_state = AnalysisState()
    new_state.user_story = legacy_data["user_story"]

    if legacy_data["analysis_state"]:
        new_state.analysis_data = legacy_data["analysis_state"].get("analise_da_us")
        new_state.analysis_report = legacy_data["analysis_state"].get(
            "relatorio_analise_inicial", ""
        )
        new_state.stage = AnalysisStage.EDITING_ANALYSIS

    if legacy_data["test_plan_df"] is not None:
        new_state.test_plan_report = legacy_data["test_plan_report"] or ""
        new_state.test_plan_df = legacy_data["test_plan_df"]
        new_state.pdf_bytes = legacy_data["pdf_report_bytes"]
        new_state.stage = AnalysisStage.COMPLETED

    st.session_state[_STATE_KEY] = new_state
    print("✅ Migração concluída!")


def debug_state():
    """
    Imprime o estado atual no console (útil para debug).

    Exemplo de uso:
        from state_manager import debug_state
        debug_state()  # No terminal do Streamlit
    """
    state = get_state()
    print("\n" + "=" * 60)
    print("🔍 DEBUG: Estado Atual do QA Oráculo")
    print("=" * 60)
    print(f"Estágio: {state.stage.name} ({state.get_stage_label()})")
    print(f"Progresso: {state.get_progress_percentage()}%")
    print(f"User Story: {len(state.user_story)} caracteres")
    print(f"Análise gerada: {'Sim' if state.analysis_data else 'Não'}")
    print(f"Plano gerado: {'Sim' if state.test_plan_df is not None else 'Não'}")
    print(
        f"Salvo no histórico: {f'Sim (ID {state.saved_history_id})' if state.is_saved() else 'Não'}"
    )

    if state.stage == AnalysisStage.ERROR:
        print(f"⚠️ ERRO: {state.error_message}")

    print("=" * 60 + "\n")


# ==========================================================
# 🧪 Testes de Integração com Streamlit
# ==========================================================
if __name__ == "__main__":
    print("⚠️ Este módulo deve ser executado dentro do Streamlit!")
    print("Execute: streamlit run app.py")
