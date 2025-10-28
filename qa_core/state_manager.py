# ====================
# state_manager.py
# state_manager.py
# Gerenciamento do estado da aplicação Streamlit
# ====================


import streamlit as st


def initialize_state():
    """
    Inicializa o session_state com valores padrão se eles não existirem.
    Útil para garantir que todas as chaves necessárias estejam presentes.
    Atualmente, o app usa .get() que torna isso opcional, mas é uma boa prática.
    """
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
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session():
    """
    Limpa todas as variáveis da sessão para iniciar uma nova análise.
    Isso força um estado limpo para a próxima execução.
    """
    keys_to_reset = list(st.session_state.keys())
    for key in keys_to_reset:
        # Evita deletar chaves internas do Streamlit ou widgets persistentes se necessário
        if not key.startswith("FormSubmitter:"):
            del st.session_state[key]
