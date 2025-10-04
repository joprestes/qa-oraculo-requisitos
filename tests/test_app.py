# tests/test_app.py

from unittest.mock import MagicMock, patch

import pytest

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


# --- TESTES DO HISTÓRICO (Versões Antigas - Serão removidos ou atualizados) ---


@patch("app.st")
def test_render_history_page_com_historico(mock_st):
    mock_st.session_state = {}
    mock_st.query_params.get.return_value = [None]
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("app.get_all_analysis_history", return_value=history):
        app.render_history_page()

    calls = [str(call) for call in mock_st.markdown.call_args_list]
    assert any("2025-09-26" in c for c in calls)


@patch("app.st")
def test_render_history_page_detalhes(mock_st):
    mock_st.session_state = {}

    # Simula query_params para a view de detalhes
    mock_st.query_params.get.return_value = ["1"]

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

    mock_st.sidebar.radio.return_value = "Analisar User Story"
    app.main()
    mock_main.assert_called_once()

    mock_st.sidebar.radio.return_value = "Histórico de Análises"
    app.main()
    mock_history.assert_called_once()


# ---- Fixture para Streamlit mockado ----
@pytest.fixture
def mocked_st():
    with patch("app.st") as mock_st:
        mock_st.session_state = {}

        # O mock para query_params é configurado dentro de cada teste que usa a fixture
        # para evitar comportamento inesperado entre testes.

        def fake_columns(arg):
            if isinstance(arg, int):
                return tuple(MagicMock() for _ in range(arg))
            if isinstance(arg, (list, tuple)):
                return tuple(MagicMock() for _ in arg)
            return (MagicMock(), MagicMock())

        mock_st.columns.side_effect = fake_columns
        yield mock_st


# ---- Testes de histórico com fixture (VERSÃO CORRETA E ATUALIZADA) ----


# ✅ ESTE É O TESTE CORRETO para "sem histórico"
def test_render_history_sem_historico(mocked_st):
    # Garante que não estamos na view de detalhes
    mocked_st.query_params.get.return_value = [None]

    with patch("app.get_all_analysis_history", return_value=[]):
        app.render_history_page()

    mocked_st.info.assert_called_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar."
    )


def test_render_history_com_historico_lista(mocked_st):
    # Garante que não estamos na view de detalhes
    mocked_st.query_params.get.return_value = [None]

    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("app.get_all_analysis_history", return_value=history):
        app.render_history_page()
    mocked_st.container.assert_called()


def test_render_history_com_analysis_id_valido(mocked_st):
    # Simula estar na view de detalhes com analysis_id = 1
    mocked_st.query_params.get.return_value = ["1"]

    analysis_entry = {
        "id": 1,
        "created_at": "2025-09-26",
        "user_story": "User Story completa",
        "analysis_report": "Relatório IA",
        "test_plan_report": "Plano gerado",
    }
    with patch("app.get_analysis_by_id", return_value=analysis_entry):
        app.render_history_page()
    mocked_st.markdown.assert_any_call("### Análise de 2025-09-26")
    mocked_st.code.assert_called_with("User Story completa", language="text")


def test_render_history_com_analysis_id_invalido(mocked_st):
    # Simula estar na view de detalhes com um ID inválido
    mocked_st.query_params.get.return_value = ["99"]

    with patch("app.get_analysis_by_id", return_value=None):
        app.render_history_page()
    mocked_st.error.assert_called_with("Análise não encontrada.")


# ---- Testes extras de fluxos do render_main_analysis_page ----
# (O resto do arquivo permanece o mesmo)
def test_render_main_analysis_page_sem_analysis_state(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state["analysis_finished"] = False
    mocked_st.session_state["analysis_state"] = None
    mocked_st.session_state["user_story_input"] = ""
    mocked_st.button.return_value = False

    app.render_main_analysis_page()
    mocked_st.text_area.assert_any_call(
        "Insira a User Story aqui:", height=250, key="user_story_input"
    )


def test_render_main_analysis_page_sem_user_story(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state["analysis_finished"] = False
    mocked_st.session_state["analysis_state"] = None
    mocked_st.session_state["user_story_input"] = ""
    mocked_st.button.return_value = True

    app.render_main_analysis_page()
    mocked_st.warning.assert_called_once_with(
        "Por favor, insira uma User Story antes de analisar."
    )


def test_render_main_analysis_page_downloads_sem_dados():
    """Força finalização sem test_plan_df nem pdf"""
    with patch("app.st") as mock_st:
        mock_st.session_state = {
            "analysis_finished": True,
            "analysis_state": {"relatorio_analise_inicial": "Fake"},
            "test_plan_report": None,
            "test_plan_df": None,
            "pdf_report_bytes": None,
            "user_story_input": "História teste",
        }

        mock_st.columns.return_value = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        app.render_main_analysis_page()
        mock_st.subheader.assert_called_with("Downloads Disponíveis")
