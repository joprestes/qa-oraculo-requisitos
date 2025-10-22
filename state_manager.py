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


def set_streamlit_module(st_module):
    """Permite injetar um módulo/objeto compatível com streamlit.

    Essa função mantém compatibilidade com os testes que patcham ``app.st``
    diretamente. Sem esse ajuste, o ``state_manager`` continuaria utilizando o
    módulo original do Streamlit, ignorando o mock e causando inconsistências
    entre o estado da aplicação e o que os testes esperam observar.
    """

    global st
    st = st_module


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
    legacy_keys = {
        "analysis_state",
        "test_plan_report",
        "test_plan_df",
        "pdf_report_bytes",
        "analysis_finished",
        "user_story_input",
    }

    should_migrate = any(key in st.session_state for key in legacy_keys)

    if _STATE_KEY not in st.session_state:
        st.session_state[_STATE_KEY] = AnalysisState()
        print("🆕 Estado inicializado com valores padrão")

    if should_migrate:
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

    # Remove flags legadas se existirem
    legacy_keys = [
        "analysis_finished",
        "show_generate_plan_button",
        "history_saved",
        "last_saved_id",
        "confirm_delete_id",
        "confirm_clear_all",
    ]

    for key in legacy_keys:
        if key in st.session_state:
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

    # Detecta flags legadas
    analysis_state = st.session_state.get("analysis_state")
    if isinstance(analysis_state, dict):
        meaningful_analysis = any(
            bool(analysis_state.get(field))
            for field in ("relatorio_analise_inicial", "analise_da_us")
        )
        if not meaningful_analysis:
            analysis_state = None

    user_story = st.session_state.get("user_story_input", "").strip()
    test_plan_report = st.session_state.get("test_plan_report")
    if isinstance(test_plan_report, str) and not test_plan_report.strip():
        test_plan_report = None

    legacy_data = {
        "user_story": user_story,
        "analysis_state": analysis_state,
        "test_plan_report": test_plan_report,
        "test_plan_df": st.session_state.get("test_plan_df"),
        "pdf_report_bytes": st.session_state.get("pdf_report_bytes"),
        "analysis_finished": st.session_state.get("analysis_finished", False),
    }

    # Se não há dados legados, não faz nada
    if not any(legacy_data.values()):
        return

    print("🔄 Migrando estado legado para novo formato...")

    state = st.session_state.get(_STATE_KEY, AnalysisState())

    if legacy_data["user_story"]:
        state.user_story = legacy_data["user_story"].strip()

    if legacy_data["analysis_state"]:
        analysis_state = legacy_data["analysis_state"]

        raw_analysis_data = analysis_state.get("analise_da_us")
        if raw_analysis_data is None:
            raw_analysis_data = {}

        state.analysis_data = raw_analysis_data
        state.analysis_report = analysis_state.get("relatorio_analise_inicial", "") or ""

        # Mesmo que a análise ainda não tenha sido refinada, manter o
        # estágio em EDITING_ANALYSIS garante compatibilidade com o fluxo
        # legado, que permitia acionar a geração do plano imediatamente
        # após a migração. Sem esse ajuste, ``start_plan_generation``
        # dispararia ValueError por entender que ainda estamos em INITIAL.
        if state.stage == AnalysisStage.INITIAL:
            state.stage = AnalysisStage.EDITING_ANALYSIS

    has_test_plan = legacy_data["test_plan_df"] is not None

    if has_test_plan:
        state.test_plan_report = legacy_data["test_plan_report"] or ""
        state.test_plan_df = legacy_data["test_plan_df"]
        state.pdf_bytes = legacy_data["pdf_report_bytes"]
        state.stage = AnalysisStage.COMPLETED

    if legacy_data["analysis_finished"] and has_test_plan:
        state.stage = AnalysisStage.COMPLETED

    # Se chegamos aqui sem plano de testes, mas com análise disponível,
    # garantimos que o estágio reflita o fluxo de edição.
    if (
        state.stage in (AnalysisStage.INITIAL, AnalysisStage.ANALYZING)
        and (state.analysis_report or state.analysis_data)
    ):
        state.stage = AnalysisStage.EDITING_ANALYSIS

    st.session_state[_STATE_KEY] = state
    print("✅ Migração concluída!")

    if (not state.analysis_data or state.analysis_data == {}) and state.test_plan_df is None:
        state.stage = AnalysisStage.INITIAL


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
