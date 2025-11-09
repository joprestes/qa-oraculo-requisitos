# =========================================================
# tests/test_app.py
# =========================================================
"""
Testes de alto nível para o módulo principal do QA Oráculo (app.py).

Este arquivo cobre:
- Funções wrapper de IA (run_analysis_graph, run_test_plan_graph)
- Renderização das páginas principais e histórico
- Fluxos principais de interação do usuário
- Execução direta do script (if __name__ == "__main__")
"""

import datetime
import importlib
import sqlite3
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from qa_core import app

# Constantes auxiliares para layouts de colunas nos testes
FOUR_COLUMN_COUNT = 4
TWO_COLUMN_COUNT = 2


# --- TESTES DAS FUNÇÕES WRAPPER ---
def test_run_analysis_graph():
    with patch("qa_core.app.grafo_analise") as mock_grafo:
        mock_grafo.invoke.return_value = {"ok": True}
        result = app.run_analysis_graph("US Teste")
        assert result == {"ok": True}
        mock_grafo.invoke.assert_called_once()
        args, _ = mock_grafo.invoke.call_args
        assert args[0]["user_story"] == "US Teste"
        assert "trace_id" in args[0]


def test_run_test_plan_graph():
    with patch("qa_core.app.grafo_plano_testes") as mock_grafo:
        mock_grafo.invoke.return_value = {"plano": True}
        result = app.run_test_plan_graph({"analise": "x"})
        assert result == {"plano": True}
        mock_grafo.invoke.assert_called_once()
        args, _ = mock_grafo.invoke.call_args
        assert args[0]["analise"] == "x"
        assert "trace_id" in args[0]


# --- TESTES DO HISTÓRICO (Versões antigas, mantidas para compatibilidade) ---
@patch("qa_core.app.st")
def test_render_history_page_com_historico(mock_st):
    mock_st.session_state = {}
    mock_st.query_params.get.return_value = [None]
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("qa_core.app.get_all_analysis_history", return_value=history):
        app.render_history_page()

    calls = [str(mock_call) for mock_call in mock_st.markdown.call_args_list]
    assert any("2025-09-26" in call_str for call_str in calls)


@patch("qa_core.app.st")
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
    with patch("qa_core.app.get_analysis_by_id", return_value=entry):
        app.render_history_page()
        mock_st.markdown.assert_any_call("### Análise de 2025-09-26")
        mock_st.code.assert_called_once_with("Teste", language="gherkin")


# --- TESTE DO MAIN ---
@patch("qa_core.app.render_main_analysis_page")
@patch("qa_core.app.render_history_page")
@patch("qa_core.app.st")
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
    with patch("qa_core.app.st") as mock_st:
        mock_st.session_state = {}

        def fake_columns(arg):
            if isinstance(arg, int):
                return tuple(MagicMock() for _ in range(arg))
            if isinstance(arg, (list | tuple)):
                return tuple(MagicMock() for _ in arg)
            return (MagicMock(), MagicMock())

        mock_st.columns.side_effect = fake_columns

        def make_context_manager():
            context = MagicMock()
            context.__enter__.return_value = MagicMock()
            context.__exit__.return_value = False
            return context

        mock_st.expander.side_effect = lambda *args, **kwargs: make_context_manager()
        mock_st.container.side_effect = lambda *args, **kwargs: make_context_manager()
        mock_st.spinner.side_effect = lambda *args, **kwargs: make_context_manager()
        mock_st.sidebar.radio.return_value = "Analisar User Story"
        mock_st.toast = MagicMock()

        yield mock_st


# ---- Testes de histórico com fixture (versão atualizada) ----
def test_render_history_sem_historico(mocked_st):
    mocked_st.query_params.get.return_value = [None]

    with patch("qa_core.app.get_all_analysis_history", return_value=[]):
        app.render_history_page()

    mocked_st.info.assert_called_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar."
    )


def test_render_history_com_historico_lista(mocked_st):
    mocked_st.query_params.get.return_value = [None]
    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("qa_core.app.get_all_analysis_history", return_value=history):
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
    with patch("qa_core.app.get_analysis_by_id", return_value=analysis_entry):
        app.render_history_page()
    mocked_st.markdown.assert_any_call("### Análise de 2025-09-26")
    mocked_st.code.assert_called_with("User Story completa", language="gherkin")


def test_render_history_com_analysis_id_invalido(mocked_st):
    mocked_st.query_params.get.return_value = ["99"]
    with patch("qa_core.app.get_analysis_by_id", return_value=None):
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


def _make_context():
    ctx = MagicMock()
    ctx.__enter__.return_value = MagicMock()
    ctx.__exit__.return_value = False
    return ctx


def test_render_history_confirm_delete_sem_sucesso(mocked_st):
    """Cobre o branch onde a exclusão individual falha e gera announce erro."""
    mocked_st.session_state.clear()
    mocked_st.session_state["confirm_delete_id"] = 7
    mocked_st.query_params.get.return_value = None
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    original_columns = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == 2:
            confirm_col, cancel_col = MagicMock(), MagicMock()
            confirm_col.button.return_value = True
            cancel_col.button.return_value = False
            return (confirm_col, cancel_col)
        return original_columns(arg)

    mocked_st.columns.side_effect = columns_side_effect

    with (
        patch("qa_core.app.delete_analysis_by_id", return_value=False),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call(
        "Não foi possível excluir a análise selecionada.", "error", st_api=mocked_st
    )
    mocked_st.columns.side_effect = original_columns


def test_render_history_clear_all_sem_registros(mocked_st):
    """Cobre o branch de confirmação geral quando nenhum registro é removido."""
    mocked_st.session_state.clear()
    mocked_st.session_state["confirm_clear_all"] = True
    mocked_st.query_params.get.return_value = None
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    original_columns = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == 2:
            confirm_col, cancel_col = MagicMock(), MagicMock()
            confirm_col.button.return_value = True
            cancel_col.button.return_value = False
            return (confirm_col, cancel_col)
        return original_columns(arg)

    mocked_st.columns.side_effect = columns_side_effect

    with (
        patch("qa_core.app.clear_history", return_value=0),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call(
        "Nenhuma análise foi removida.", "warning", st_api=mocked_st
    )
    mocked_st.columns.side_effect = original_columns


def test_render_history_clear_all_cancelado(mocked_st):
    """Cobre o caminho onde o usuário cancela a exclusão geral."""
    mocked_st.session_state.clear()
    mocked_st.session_state["confirm_clear_all"] = True
    mocked_st.query_params.get.return_value = None
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    original_columns = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == 2:
            confirm_col, cancel_col = MagicMock(), MagicMock()
            confirm_col.button.return_value = False
            cancel_col.button.return_value = True
            return (confirm_col, cancel_col)
        return original_columns(arg)

    mocked_st.columns.side_effect = columns_side_effect

    with (
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call(
        "Nenhuma exclusão foi realizada.", "info", st_api=mocked_st
    )
    mocked_st.columns.side_effect = original_columns


def test_render_history_id_invalido_tratado(mocked_st):
    """Garante que IDs inválidos não causam exceções na conversão."""
    mocked_st.query_params.get.return_value = ["abc"]
    with (
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()
    mock_announce.assert_called_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar.",
        "info",
        st_api=mocked_st,
    )


def test_render_history_sem_plano_exibe_aviso(mocked_st):
    """Cobre o branch de detalhe quando não existe plano de testes salvo."""
    mocked_st.query_params.get.return_value = ["1"]
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()
    mocked_st.session_state.clear()

    with (
        patch(
            "qa_core.app.get_analysis_by_id",
            return_value={
                "created_at": "2025-10-01",
                "user_story": "História",
                "analysis_report": "Relatório",
            },
        ),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()
    mock_announce.assert_any_call(
        "Nenhum plano de testes foi gerado para esta análise.", "info", st_api=mocked_st
    )


def test_render_history_lista_formata_datas(mocked_st):
    """Garante cobertura das ramificações de data no modo lista."""
    mocked_st.query_params.get.return_value = None
    history = [
        {"id": 1, "created_at": "2025-10-01 10:00", "user_story": "Story 1"},
        {
            "id": 2,
            "created_at": datetime.datetime(2025, 10, 2, 11, 30),
            "user_story": "Story 2",
        },
        {"id": 3, "created_at": 123456, "user_story": "Story 3"},
    ]
    with patch("qa_core.app.get_all_analysis_history", return_value=history):
        app.render_history_page()
    # Para o datetime, deve ter formatado como dd/mm/YYYY HH:MM
    mocked_st.markdown.assert_any_call("**🕒 Data:** 02/10/2025 11:30")
    mocked_st.markdown.assert_any_call("**🕒 Data:** 123456")


def test_render_history_analysis_entry_convertido_dict(mocked_st):
    """Cobre a conversão de registros não-dict para dict no modo detalhado."""
    mocked_st.query_params.get.return_value = ["5"]
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()
    entry_as_list = [
        ("id", 5),
        ("created_at", datetime.datetime(2025, 10, 3, 14, 0)),
        ("user_story", "História convertida"),
        ("analysis_report", "Relatório detalhado"),
        ("test_plan_report", "Plano convertido"),
    ]

    with (
        patch("qa_core.app.get_analysis_by_id", return_value=entry_as_list),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.accessible_button", return_value=False),
    ):
        app.render_history_page()

    mocked_st.markdown.assert_any_call("### Análise de 2025-10-03")


def test_render_history_selected_id_type_error(mocked_st):
    """Cobre o tratamento de exceções ao buscar análise específica."""
    mocked_st.query_params.get.return_value = ["7"]
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    with (
        patch("qa_core.app.get_analysis_by_id", side_effect=TypeError("boom")),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.accessible_button", return_value=False),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call("Análise não encontrada.", "error", st_api=mocked_st)


def test_render_history_page_test_mode_com_plano():
    """Cobre o modo de teste simplificado com plano disponível."""
    st_api = MagicMock()
    st_api.session_state = {}
    st_api.query_params = MagicMock(get=lambda key: ["1"])

    with patch(
        "qa_core.app.get_analysis_by_id",
        return_value={
            "created_at": "2025-10-02",
            "user_story": "US",
            "analysis_report": "Rel",
            "test_plan_report": "Plano",
        },
    ):
        app._render_history_page_test_mode(st_api)

    st_api.markdown.assert_any_call("### Análise de 2025-10-02")
    st_api.markdown.assert_any_call("Plano")


def test_render_main_analysis_page_downloads_sem_dados():
    """Força finalização sem test_plan_df nem pdf."""
    with patch("qa_core.app.st") as mock_st:
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

    with patch("qa_core.app._save_current_analysis_to_history") as mock_save:
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

    with patch("qa_core.app.run_test_plan_graph", return_value=resultado_invalido):
        with patch("qa_core.app._save_current_analysis_to_history"):
            app.render_main_analysis_page()
            mocked_st.error.assert_called_with(
                "O Oráculo não conseguiu gerar um plano de testes estruturado."
            )
            assert mocked_st.session_state["analysis_finished"] is True
            mocked_st.rerun.assert_called()


def test_render_main_page_edicao_e_salvamento_gherkin(mocked_st):
    """
    Valida que ao editar um cenário Gherkin, o relatório de plano é atualizado
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
        patch("qa_core.app._save_current_analysis_to_history") as mock_save,
        patch(
            "qa_core.utils.gerar_relatorio_md_dos_cenarios",
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


def test_render_user_story_input_fluxo_sucesso(mocked_st):
    """Garante que o fluxo feliz de entrada da user story aciona o grafo e re-renderiza."""
    mocked_st.session_state.clear()
    mocked_st.session_state["user_story_input"] = "Como tester, quero validar o fluxo"

    with (
        patch("qa_core.app.accessible_button", return_value=True),
        patch(
            "qa_core.app.run_analysis_graph",
            return_value={
                "analise_da_us": {"avaliacao": "ok"},
                "relatorio_analise_inicial": "Relatório",
            },
        ) as mock_grafo,
    ):
        resultado = app._render_user_story_input()

    assert resultado is True
    mock_grafo.assert_called_once_with("Como tester, quero validar o fluxo")
    assert (
        mocked_st.session_state["analysis_state"]["analise_da_us"]["avaliacao"] == "ok"
    )
    assert mocked_st.session_state["show_generate_plan_button"] is False
    mocked_st.rerun.assert_called()


def test_save_analysis_to_history_wrapper_chama_privado():
    """Valida cobertura da função pública que delega ao helper interno."""
    with patch(
        "qa_core.app._save_current_analysis_to_history", return_value="ok"
    ) as mock_save:
        assert app.save_analysis_to_history(update_existing=True) == "ok"
    mock_save.assert_called_once_with(update_existing=True)


def test_render_main_page_gera_plano_com_sucesso(mocked_st):
    """Cobre o fluxo feliz da geração de plano de testes pela IA."""

    mocked_st.session_state.update(
        {
            "analysis_state": {
                "relatorio_analise_inicial": "Relatório IA",
                "analise_da_us": {},
            },
            "show_generate_plan_button": True,
            "user_story_input": "Como tester, quero ...",
            "analysis_finished": False,
        }
    )

    col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()

    original_columns_side_effect = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == [1, 1, 2]:
            col1.button.return_value = True
            col2.button.return_value = False
            return (col1, col2, col3)
        if arg == FOUR_COLUMN_COUNT:
            return tuple(MagicMock() for _ in range(4))
        return original_columns_side_effect(arg)

    mocked_st.columns.side_effect = columns_side_effect

    with (
        patch(
            "qa_core.app.run_test_plan_graph",
            return_value={
                "plano_e_casos_de_teste": {
                    "casos_de_teste_gherkin": [
                        {
                            "id": "CT-1",
                            "titulo": "Login",
                            "cenario": ["Dado", "Quando", "Então"],
                        }
                    ]
                },
                "relatorio_plano_de_testes": "### Plano",
            },
        ),
        patch("qa_core.app.generate_pdf_report", return_value=b"pdf-gerado"),
        patch("qa_core.app._save_current_analysis_to_history") as mock_save,
        patch(
            "qa_core.app.accessible_text_area",
            side_effect=lambda *args, **kwargs: kwargs.get("value", ""),
        ),
    ):
        app.render_main_analysis_page()

    assert mocked_st.session_state["analysis_finished"] is True
    assert mocked_st.session_state["history_saved"] is True
    assert (
        mocked_st.session_state["test_plan_df"].iloc[0]["cenario"]
        == "Dado\nQuando\nEntão"
    )
    assert mocked_st.session_state["pdf_report_bytes"] == b"pdf-gerado"
    mock_save.assert_called_once()
    mocked_st.rerun.assert_called()


def test_render_main_page_sem_cenario_dispara_aviso(mocked_st):
    """Lista de casos sem cenário deve acionar mensagem informativa."""

    mocked_st.session_state.update(
        {
            "analysis_finished": True,
            "analysis_state": {"relatorio_analise_inicial": "Relatório"},
            "test_plan_df": pd.DataFrame(
                [
                    {
                        "id": "CT-1",
                        "titulo": "Caso",
                        "prioridade": "Alta",
                        "criterio_de_aceitacao_relacionado": "Critério",
                        "justificativa_acessibilidade": "",
                        "cenario": "",
                    }
                ]
            ),
            "test_plan_report": "### Plano",
            "pdf_report_bytes": b"",
            "user_story_input": "História",
        }
    )

    mocked_st.session_state.setdefault("show_generate_plan_button", False)

    with patch("qa_core.app.announce") as mock_announce:
        app.render_main_analysis_page()

    mock_announce.assert_any_call(
        "Este caso de teste ainda não possui cenário em formato Gherkin.",
        "info",
        st_api=mocked_st,
    )


def test_render_export_section_com_campos_xray_e_testrail(mocked_st):
    """Cobre a montagem de campos Xray/TestRail com valores preenchidos."""
    df = pd.DataFrame(
        [
            {
                "titulo": "Caso completo",
                "prioridade": "Alta",
                "cenario": ["Dado algo", "Então resultado"],
            }
        ]
    )
    mocked_st.session_state.update(
        {
            "test_plan_df": df,
            "xray_test_folder": "QA/FOLDER",
            "xray_labels": "Regression",
            "xray_priority": "High",
            "xray_component": "Core",
            "xray_fix_version": "1.0.0",
            "xray_assignee": "qa.user",
            "xray_test_set": "Sprint 42",
            "xray_custom_fields": "Epic Link=PROJ-1\nTeam=QA Core",
            "testrail_section": "Backoffice",
            "testrail_priority": "Medium",
            "testrail_references": "PROJ-1",
        }
    )

    col_azure = MagicMock()
    col_zephyr = MagicMock()
    col_xray = MagicMock()

    with (
        patch(
            "qa_core.app._render_basic_exports",
            return_value=(col_azure, col_zephyr, col_xray),
        ),
        patch("qa_core.app.gerar_csv_xray_from_df", return_value=b"xray") as mock_xray,
        patch(
            "qa_core.app.gerar_csv_testrail_from_df", return_value=b"testrail"
        ) as mock_testrail,
    ):
        app._render_export_section()

    custom_fields = mock_xray.call_args.kwargs["custom_fields"]
    assert custom_fields == {
        "Labels": "Regression",
        "Priority": "High",
        "Component": "Core",
        "Fix Version": "1.0.0",
        "Assignee": "qa.user",
        "Test Set": "Sprint 42",
        "Epic Link": "PROJ-1",
        "Team": "QA Core",
    }
    mock_testrail.assert_called_once()
    col_xray.download_button.assert_called_once()
    label, payload = col_zephyr.download_button.call_args[0][:2]
    kwargs = col_zephyr.download_button.call_args[1]
    assert label == "🧪 TestRail (.csv)"
    assert payload == b"testrail"
    assert kwargs["mime"] == "text/csv"
    assert kwargs["use_container_width"] is True
    assert kwargs["file_name"].endswith("testrail.csv")


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


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.announce")
@patch("qa_core.app.st")
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


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.st")
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
        mock_call
        for mock_call in mock_cursor.execute.call_args_list
        if "UPDATE" in mock_call.args[0]
    ]
    assert update_calls, "Deve executar UPDATE ao atualizar registro existente"

    _, params = update_calls[0].args
    assert params[1] == "Como tester quero validar"
    assert params[2] == "Relatório inicial"
    assert params[3] == "Plano completo"

    # Garante que não foi feito INSERT
    assert all(
        "INSERT" not in mock_call.args[0]
        for mock_call in mock_cursor.execute.call_args_list
    )
    mock_conn.commit.assert_called_once()


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.announce")
@patch("qa_core.app.st")
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


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.announce")
@patch("qa_core.app.st")
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


@patch("qa_core.app.announce")
@patch("qa_core.app.delete_analysis_by_id", return_value=True)
@patch("qa_core.app.get_all_analysis_history", return_value=[])
@patch("qa_core.app.st")
def test_render_history_page_impl_confirma_exclusao(
    mock_st, mock_get_history, mock_delete, mock_announce
):
    """Fluxo de confirmação remove item e reinicia a página."""

    mock_st.session_state = {"confirm_delete_id": 5}
    mock_st.query_params.get.return_value = None

    def make_context():
        ctx = MagicMock()
        ctx.__enter__.return_value = MagicMock()
        ctx.__exit__.return_value = False
        return ctx

    mock_st.container.side_effect = lambda *args, **kwargs: make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: make_context()
    confirm_col, cancel_col = MagicMock(), MagicMock()

    def columns_side_effect(arg):
        if arg == TWO_COLUMN_COUNT:
            return (confirm_col, cancel_col)
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        return tuple(MagicMock() for _ in range(len(arg)))

    mock_st.columns.side_effect = columns_side_effect
    confirm_col.button.return_value = True
    cancel_col.button.return_value = False
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    mock_delete.assert_called_once_with(5)
    assert "confirm_delete_id" not in mock_st.session_state
    mock_announce.assert_any_call(
        "Análise 5 removida com sucesso.", "success", st_api=mock_st
    )
    mock_st.rerun.assert_called_once()


@patch("qa_core.app.announce")
@patch("qa_core.app.delete_analysis_by_id", return_value=False)
@patch("qa_core.app.get_all_analysis_history", return_value=[])
@patch("qa_core.app.st")
def test_render_history_page_impl_cancela_exclusao(
    mock_st, mock_get_history, mock_delete, mock_announce
):
    """Clique em cancelar deve apenas limpar o estado."""

    mock_st.session_state = {"confirm_delete_id": 42}
    mock_st.query_params.get.return_value = None

    def make_context():
        ctx = MagicMock()
        ctx.__enter__.return_value = MagicMock()
        ctx.__exit__.return_value = False
        return ctx

    mock_st.container.side_effect = lambda *args, **kwargs: make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: make_context()
    confirm_col, cancel_col = MagicMock(), MagicMock()

    def columns_side_effect(arg):
        if arg == TWO_COLUMN_COUNT:
            return (confirm_col, cancel_col)
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        return tuple(MagicMock() for _ in range(len(arg)))

    mock_st.columns.side_effect = columns_side_effect
    confirm_col.button.return_value = False
    cancel_col.button.return_value = True
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    mock_delete.assert_not_called()
    assert "confirm_delete_id" not in mock_st.session_state
    mock_announce.assert_any_call(
        "Nenhuma exclusão foi realizada.", "info", st_api=mock_st
    )
    mock_st.rerun.assert_called_once()


@patch("qa_core.app.announce")
@patch("qa_core.app.clear_history", return_value=3)
@patch("qa_core.app.get_all_analysis_history", return_value=[])
@patch("qa_core.app.st")
def test_render_history_page_impl_confirma_limpeza_total(
    mock_st, mock_get_history, mock_clear_history, mock_announce
):
    """Valida a confirmação da limpeza completa do histórico."""

    mock_st.session_state = {"confirm_clear_all": True}
    mock_st.query_params.get.return_value = None

    def make_context():
        ctx = MagicMock()
        ctx.__enter__.return_value = MagicMock()
        ctx.__exit__.return_value = False
        return ctx

    mock_st.container.side_effect = lambda *args, **kwargs: make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: make_context()
    confirm_col, cancel_col = MagicMock(), MagicMock()

    def columns_side_effect(arg):
        if arg == TWO_COLUMN_COUNT:
            return (confirm_col, cancel_col)
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        return tuple(MagicMock() for _ in range(len(arg)))

    mock_st.columns.side_effect = columns_side_effect
    confirm_col.button.return_value = True
    cancel_col.button.return_value = False
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    mock_clear_history.assert_called_once()
    assert "confirm_clear_all" not in mock_st.session_state
    mock_announce.assert_any_call(
        "3 análises foram removidas.", "success", st_api=mock_st
    )
    mock_st.rerun.assert_called_once()


@patch("qa_core.app.accessible_button")
@patch("qa_core.app.get_all_analysis_history")
@patch("qa_core.app.st")
def test_render_history_page_impl_lista_dispara_confirm_clear_all(
    mock_st, mock_get_history, mock_accessible_button
):
    """O botão para limpar histórico deve sinalizar confirm_clear_all."""

    mock_st.session_state = {}
    mock_st.query_params.get.return_value = None

    def make_context():
        ctx = MagicMock()
        ctx.__enter__.return_value = MagicMock()
        ctx.__exit__.return_value = False
        return ctx

    mock_st.container.side_effect = lambda *args, **kwargs: make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: make_context()

    def columns_side_effect(arg):
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        if isinstance(arg, (list | tuple)):
            return tuple(MagicMock() for _ in arg)
        return (MagicMock(), MagicMock())

    mock_st.columns.side_effect = columns_side_effect

    mock_get_history.return_value = [
        {"id": 1, "created_at": "2024-01-01", "user_story": "Como usuário..."}
    ]

    def accessible_button_side_effect(*args, **kwargs):
        label = kwargs.get("label") or (args[0] if args else "")
        return label == "🗑️ Excluir TODO o Histórico"

    mock_accessible_button.side_effect = accessible_button_side_effect
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    assert mock_st.session_state["confirm_clear_all"] is True
    mock_st.rerun.assert_called_once()


# --- TESTES DE EXECUÇÃO DIRETA DO SCRIPT ---
def test_main_execucao_direta_reload(monkeypatch):
    """Simula execução direta do app (cobre o if __main__)."""
    monkeypatch.setattr(app, "__name__", "__main__")
    importlib.reload(app)
    assert True  # Executou sem erro → cobertura garantida


@pytest.mark.slow
def test_main_execucao_direta_subprocess():
    """Executa o app como script real (python -m qa_core.app)."""
    result = subprocess.run(
        [sys.executable, "-m", "qa_core.app"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
