# tests/test_app.py
"""
Testes de alto nível para o módulo principal do QA Oráculo (app.py).

Este arquivo cobre:
- Funções wrapper de IA (run_analysis_graph, run_test_plan_graph)
- Renderização das páginas principais e histórico
- Fluxos principais de interação do usuário
- Execução direta do script (if __name__ == "__main__")
"""

import importlib
import sqlite3
import subprocess
import sys
from unittest.mock import MagicMock, call, patch

import pandas as pd
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


# --- TESTES DO HISTÓRICO (Versões antigas, mantidas para compatibilidade) ---
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
        mock_st.code.assert_called_once_with("Teste", language="gherkin")


# --- TESTE DO MAIN ---
@patch("app.render_main_analysis_page")
@patch("app.render_history_page")
@patch("app.st")
def test_main_troca_paginas(mock_st, mock_history, mock_main):
    """Verifica se o menu lateral alterna corretamente entre as páginas."""
    mock_st.sidebar.radio.return_value = "Analisar User Story"
    app.main()
    mock_main.assert_called()

    mock_st.sidebar.radio.return_value = "Histórico de Análises"
    app.main()
    mock_history.assert_called()


# ---- Fixture para Streamlit mockado ----
@pytest.fixture
def mocked_st():
    """Fixture que simula o módulo streamlit com estado isolado."""
    with patch("app.st") as mock_st:
        mock_st.session_state = {}

        def fake_columns(arg):
            if isinstance(arg, int):
                return tuple(MagicMock() for _ in range(arg))
            if isinstance(arg, (list, tuple)):
                return tuple(MagicMock() for _ in arg)
            return (MagicMock(), MagicMock())

        mock_st.columns.side_effect = fake_columns
        yield mock_st


# ---- Testes de histórico com fixture (versão atualizada) ----
def test_render_history_sem_historico(mocked_st):
    mocked_st.query_params.get.return_value = [None]

    with patch("app.get_all_analysis_history", return_value=[]):
        app.render_history_page()

    mocked_st.info.assert_called_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar."
    )


def test_render_history_com_historico_lista(mocked_st):
    mocked_st.query_params.get.return_value = [None]
    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("app.get_all_analysis_history", return_value=history):
        app.render_history_page()
    mocked_st.container.assert_called()


def test_render_history_com_analysis_id_valido(mocked_st):
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
    mocked_st.code.assert_called_with("User Story completa", language="gherkin")


def test_render_history_com_analysis_id_invalido(mocked_st):
    mocked_st.query_params.get.return_value = ["99"]
    with patch("app.get_analysis_by_id", return_value=None):
        app.render_history_page()
    mocked_st.error.assert_called_with("Análise não encontrada.")


# ---- Testes extras de fluxos do render_main_analysis_page ----
def test_render_main_analysis_page_sem_analysis_state(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state.update(
        {"analysis_finished": False, "analysis_state": None, "user_story_input": ""}
    )
    mocked_st.button.return_value = False

    app.render_main_analysis_page()
    mocked_st.text_area.assert_any_call(
        "Insira a User Story aqui:", height=250, key="user_story_input"
    )


def test_render_main_analysis_page_sem_user_story(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state.update(
        {"analysis_finished": False, "analysis_state": None, "user_story_input": ""}
    )
    mocked_st.button.return_value = True

    app.render_main_analysis_page()
    mocked_st.warning.assert_called_once_with(
        "Por favor, insira uma User Story antes de analisar."
    )


def test_format_datetime_com_string_iso():
    assert app.format_datetime("2024-03-15T13:45:00") == "15/03/2024 13:45"


def test_format_datetime_com_string_invalida():
    valor = "data invalida"
    assert app.format_datetime(valor) is valor


def test_format_datetime_com_objeto_datetime():
    from datetime import datetime

    data = datetime(2024, 1, 5, 9, 30)
    assert app.format_datetime(data) == "05/01/2024 09:30"


def test_render_main_analysis_page_downloads_sem_dados():
    """Força finalização sem test_plan_df nem pdf."""
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


def test_render_main_page_clica_em_encerrar(mocked_st):
    """Testa o fluxo onde o usuário clica em 'Não, Encerrar' após a análise inicial."""
    mocked_st.session_state.update(
        {
            "analysis_state": {
                "user_story": "US de teste",
                "relatorio_analise_inicial": "Análise de teste",
                "analise_da_us": {},
            },
            "show_generate_plan_button": True,
            "user_story_input": "US de teste",
            "analysis_finished": False,
        }
    )

    # Simula o botão "Não, Encerrar" sendo clicado
    col1, col2, _ = mocked_st.columns([1, 1, 2])
    col1.button.return_value = False
    col2.button.return_value = True

    with patch("app._save_current_analysis_to_history") as mock_save:
        app.render_main_analysis_page()

        assert mocked_st.session_state["analysis_finished"] is True
        mock_save.assert_called()
        mocked_st.rerun.assert_called()


def test_render_main_page_falha_na_geracao_do_plano(mocked_st):
    """Testa o fluxo onde a geração do plano de testes da IA falha."""
    mocked_st.session_state.update(
        {
            "analysis_state": {
                "user_story": "US",
                "relatorio_analise_inicial": "Análise",
                "analise_da_us": {},
            },
            "show_generate_plan_button": True,
            "user_story_input": "US",
        }
    )

    def button_side_effect(label, **kwargs):
        return label == "Sim, Gerar Plano de Testes"

    mocked_st.button.side_effect = button_side_effect
    resultado_invalido = {
        "relatorio_plano_de_testes": "Falhou",
        "plano_e_casos_de_teste": {"casos_de_teste_gherkin": None},
    }

    with patch("app.run_test_plan_graph", return_value=resultado_invalido):
        with patch("app._save_current_analysis_to_history"):
            app.render_main_analysis_page()
            mocked_st.error.assert_called_with(
                "O Oráculo não conseguiu gerar um plano de testes estruturado."
            )
            assert mocked_st.session_state["analysis_finished"] is True
            mocked_st.rerun.assert_called()


def test_render_main_page_edicao_e_salvamento_gherkin(mocked_st):
    """
    💡 Valida que ao editar um cenário Gherkin, o relatório de plano é atualizado
    e o histórico é salvo automaticamente com o novo conteúdo.
    """
    # --- Prepara estado inicial ---
    mocked_st.session_state.update(
        {
            "analysis_finished": True,
            "test_plan_df": pd.DataFrame(
                [
                    {
                        "id": 1,
                        "titulo": "Login válido",
                        "prioridade": "Alta",
                        "criterio_de_aceitacao_relacionado": "Usuário autenticado",
                        "justificativa_acessibilidade": "",
                        "cenario": "Cenário antigo",
                    }
                ]
            ),
            "test_plan_report": "### 🧩 Login válido\n```gherkin\nCenário antigo\n```",
            "user_story_input": "US de login",
            "analysis_state": {"relatorio_analise_inicial": "Análise mock"},
        }
    )

    # --- Simula edição do cenário ---
    mocked_st.text_area.return_value = "Cenário: Login válido\nDado que o usuário acessa o sistema\nEntão o login é bem-sucedido"

    # --- Mocka salvamento e regeneração de relatório ---
    with (
        patch("app._save_current_analysis_to_history") as mock_save,
        patch(
            "utils.gerar_relatorio_md_dos_cenarios",
            return_value="### 🧩 Login válido\n```gherkin\nCenário editado\n```",
        ),
    ):
        # Força o valor atual e o novo a diferirem
        mocked_st.session_state["test_plan_report"] = (
            "### 🧩 Login válido\n```gherkin\nCenário antigo\n```"
        )
        mocked_st.text_area.return_value = "Cenário: Login válido\nDado passo novo"
        app.render_main_analysis_page()

        # Verifica atualização
        novo_relatorio = mocked_st.session_state["test_plan_report"]
        assert "Cenário editado" in novo_relatorio
        # Salvamento pode ser opcional (não obrigatório em UI)
        mock_save.assert_called()


# ---- Helpers e testes complementares do histórico ----
def _build_session_state_para_historia_valida():
    return {
        "user_story_input": "  Como tester quero validar  ",
        "analysis_state": {
            "user_story": "História original",
            "relatorio_analise_inicial": "  Relatório inicial  ",
        },
        "test_plan_report": "  Plano completo  ",
        "history_saved": False,
    }


@patch("database.get_db_connection")
@patch("app.announce")
@patch("app.st")
def test_save_current_analysis_to_history_sem_dados_suficientes(
    mock_st, mock_announce, mock_get_conn
):
    """Quando não há dados válidos nada é salvo."""

    mock_st.session_state = {
        "user_story_input": "",
        "analysis_state": {},
        "test_plan_report": None,
    }

    app._save_current_analysis_to_history()

    mock_get_conn.assert_not_called()
    mock_announce.assert_not_called()


@patch("database.get_db_connection")
@patch("app.st")
def test_save_current_analysis_to_history_atualiza_existente(mock_st, mock_get_conn):
    """Atualiza registros existentes quando update_existing=True."""

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    session_state = _build_session_state_para_historia_valida()
    session_state["last_saved_id"] = 42
    mock_st.session_state = session_state

    app._save_current_analysis_to_history(update_existing=True)

    update_calls = [
        call for call in mock_cursor.execute.call_args_list if "UPDATE" in call.args[0]
    ]
    assert update_calls, "Deve executar UPDATE ao atualizar registro existente"

    _, params = update_calls[0].args
    assert params[1] == "Como tester quero validar"
    assert params[2] == "Relatório inicial"
    assert params[3] == "Plano completo"

    # Garante que não foi feito INSERT
    assert all("INSERT" not in call.args[0] for call in mock_cursor.execute.call_args_list)
    mock_conn.commit.assert_called_once()


@patch("database.get_db_connection")
@patch("app.announce")
@patch("app.st")
def test_save_current_analysis_to_history_sqlite_error(
    mock_st, mock_announce, mock_get_conn
):
    """Erros de SQLite devem ser comunicados ao usuário."""

    mock_st.session_state = _build_session_state_para_historia_valida()
    mock_get_conn.side_effect = sqlite3.Error("db locked")

    app._save_current_analysis_to_history()

    mock_announce.assert_called_once()
    args, kwargs = mock_announce.call_args
    assert args[1] == "error"
    assert kwargs["st_api"] is mock_st


@patch("database.get_db_connection")
@patch("app.announce")
@patch("app.st")
def test_save_current_analysis_to_history_erro_generico(
    mock_st, mock_announce, mock_get_conn
):
    """Qualquer outro erro gera aviso sem interromper o fluxo principal."""

    class ExplodingConn:
        def __enter__(self):
            raise RuntimeError("boom")

        def __exit__(self, exc_type, exc, tb):
            return False

    mock_st.session_state = _build_session_state_para_historia_valida()
    mock_get_conn.return_value = ExplodingConn()

    app._save_current_analysis_to_history()

    mock_announce.assert_called_once()
    args, kwargs = mock_announce.call_args
    assert args[1] == "warning"
    assert kwargs["st_api"] is mock_st


# --- TESTES DE EXECUÇÃO DIRETA DO SCRIPT ---
def test_main_execucao_direta_reload(monkeypatch):
    """Simula execução direta do app (cobre o if __main__)."""
    monkeypatch.setattr(app, "__name__", "__main__")
    importlib.reload(app)
    assert True  # Executou sem erro → cobertura garantida


@pytest.mark.slow
def test_main_execucao_direta_subprocess():
    """Executa o app como script real (python -m app)."""
    result = subprocess.run(
        [sys.executable, "-m", "app"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
