# tests/test_state_manager.py
import unittest

import streamlit as st

from state_machine import AnalysisStage
from state_manager import get_state, initialize_state, reset_session


class TestStateManager(unittest.TestCase):
    def setUp(self):
        """Limpa session_state antes de cada teste"""
        st.session_state.clear()
    
    def test_initialize_state_cria_state_machine(self):
        """Valida que initialize_state cria AnalysisState"""
        initialize_state()
        
        state = get_state()
        self.assertEqual(state.stage, AnalysisStage.INITIAL)
        self.assertEqual(state.user_story, "")
        self.assertIsNone(state.analysis_data)
    
    def test_reset_session_limpa_estado(self):
        """Valida que reset_session limpa o estado"""
        initialize_state()
        state = get_state()
        state.user_story = "Teste"
        state.stage = AnalysisStage.ANALYZING
        
        reset_session()
        
        # Verifica que foi resetado
        new_state = get_state()
        self.assertEqual(new_state.stage, AnalysisStage.INITIAL)
        self.assertEqual(new_state.user_story, "")


def test_reset_session_ignora_chaves_internas():
    """Garante que reset_session não deleta chaves internas do Streamlit."""
    st.session_state.clear()
    st.session_state["FormSubmitter:123"] = "valor"
    
    initialize_state()
    reset_session()
    
    # FormSubmitter deve ser preservado
    assert "FormSubmitter:123" in st.session_state