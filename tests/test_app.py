import pytest
from unittest.mock import patch, MagicMock
import app


# --- TESTES DAS FUNÇÕES WRAPPER ---
def test_run_analysis_graph():
    with patch("app.grafo_analise") as mock_grafo:
        mock_grafo.invoke.return_value = {"ok": True}
        result = app.run_analysis_graph("US Teste")
        assert result == {"ok": True}
        mock_grafo.invoke.assert_called_once_with({"user_story": "US Teste"})


def test_run_test_plan_graph():
    with patch("app.grafo_plano_testes") as mock_grafo:
        mock_grafo.invoke.return_value = {"plano": True}
        result = app.run_test_plan_graph({"analise": "x"})
        assert result == {"plano": True}
        mock_grafo.invoke.assert_called_once_with({"analise": "x"})


# --- TESTES DO HISTÓRICO ---
@patch("app.st")
def test_render_history_page_sem_historico(mock_st):
    mock_st.session_state = {}
    with patch("app.get_all_analysis_history", return_value=[]):
        app.render_history_page()
        mock_st.info.assert_called_once_with(
            "Ainda não há análises no histórico. Realize uma nova análise para começar."
        )


@patch("app.st")
def test_render_history_page_com_historico(mock_st):
    mock_st.session_state = {}
    mock_st.query_params = {}
    mock_st.columns.return_value = (MagicMock(), MagicMock())  # ✅ simula col1, col2
    
    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("app.get_all_analysis_history", return_value=history):
        app.render_history_page()
        mock_st.markdown.assert_any_call("**Análise de:** `2025-09-26`")


@patch("app.st")
def test_render_history_page_detalhes(mock_st):
    mock_st.session_state = {}
    mock_st.query_params = {"analysis_id": ["1"]}
    entry = {
        "id": 1,
        "created_at": "2025-09-26",
        "user_story": "Teste",
        "analysis_report": "Relatório",
        "test_plan_report": "Plano",
    }
    with patch("app.get_analysis_by_id", return_value=entry):
        app.render_history_page()
        mock_st.markdown.assert_any_call("### Análise de 2025-09-26")
        mock_st.code.assert_called_once_with("Teste", language="text")


# --- TESTE DO MAIN ---
@patch("app.render_main_analysis_page")
@patch("app.render_history_page")
@patch("app.st")
def test_main_troca_paginas(mock_st, mock_history, mock_main):
    mock_st.sidebar.radio.return_value = "Análise Principal"
    app.main()
    mock_main.assert_called_once()

    mock_st.sidebar.radio.return_value = "Histórico de Análises"
    app.main()
    mock_history.assert_called_once()

#---- Testes pro render_history_page ----
@pytest.fixture
def mock_st():
    with patch("app.st") as mock_st:
        mock_st.session_state = {}
        mock_st.query_params = {}
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        yield mock_st

def test_render_history_sem_historico(mock_st):
    with patch("app.get_all_analysis_history", return_value=[]):
        app.render_history_page()
    mock_st.info.assert_called_with("Ainda não há análises no histórico. Realize uma nova análise para começar.")

def test_render_history_com_historico_lista(mock_st):
    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("app.get_all_analysis_history", return_value=history):
        app.render_history_page()
    mock_st.container.assert_called()

def test_render_history_com_analysis_id_valido(mock_st):
    mock_st.query_params = {"analysis_id": ["1"]}
    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    analysis_entry = {
        "id": 1,
        "created_at": "2025-09-26",
        "user_story": "User Story completa",
        "analysis_report": "Relatório IA",
        "test_plan_report": "Plano gerado"
    }
    with patch("app.get_all_analysis_history", return_value=history), \
         patch("app.get_analysis_by_id", return_value=analysis_entry):
        app.render_history_page()
    mock_st.markdown.assert_any_call("### Análise de 2025-09-26")
    mock_st.code.assert_called_with("User Story completa", language="text")

def test_render_history_com_analysis_id_invalido(mock_st):
    mock_st.query_params = {"analysis_id": ["99"]}
    history = [{"id": 99, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("app.get_all_analysis_history", return_value=history), \
         patch("app.get_analysis_by_id", return_value=None):
        app.render_history_page()
    mock_st.error.assert_called_with("Análise não encontrada.")