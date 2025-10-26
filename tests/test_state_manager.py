# =========================================================
# tests/test_state_manager.py
# =========================================================
import unittest

import streamlit as st

from state_manager import initialize_state, reset_session


class TestStateManager(unittest.TestCase):

    def setUp(self):
        # Garante que o session_state começa limpo antes de cada teste
        st.session_state.clear()

    def test_initialize_state_cria_chaves(self):
        initialize_state()
        # Todas as chaves padrão devem existir
        expected_keys = {
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
        for key, value in expected_keys.items():
            self.assertIn(key, st.session_state)
            self.assertEqual(st.session_state[key], value)

    def test_initialize_state_nao_sobrescreve(self):
        st.session_state["jira_priority"] = "High"
        initialize_state()
        self.assertEqual(st.session_state["jira_priority"], "High")

    def test_reset_session(self):
        st.session_state["analysis_finished"] = True
        st.session_state["user_story_input"] = "Teste"
        reset_session()
        self.assertNotIn("analysis_finished", st.session_state)
        self.assertNotIn("user_story_input", st.session_state)


if __name__ == "__main__":
    unittest.main()


def test_reset_session_ignora_chaves_internas(monkeypatch):
    """Garante que reset_session não deleta chaves internas do Streamlit."""
    st.session_state.clear()
    st.session_state["FormSubmitter:123"] = "valor"
    st.session_state["normal_key"] = "apagar"
    reset_session()
    assert "FormSubmitter:123" in st.session_state
    assert "normal_key" not in st.session_state
