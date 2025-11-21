from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from qa_core import app
from tests.fixtures.datasets import (
    TEST_ANALYSIS_STATE,
    TEST_DF_BASIC,
    TEST_EDIT_STATE,
    TEST_SESSION_STATE_FINISHED,
)


def make_analysis_state():
    return TEST_ANALYSIS_STATE.copy()


@pytest.fixture
def mock_streamlit(mock_streamlit_session):
    return mock_streamlit_session


def test_analise_iniciada_nao_salva(mock_streamlit):
    mock_streamlit.session_state["analysis_finished"] = False
    mock_streamlit.session_state["analysis_state"] = make_analysis_state()
    mock_streamlit.session_state["show_generate_plan_button"] = False

    context = MagicMock()
    context.__enter__.return_value = True
    context.__exit__.return_value = False
    mock_streamlit.form.return_value = context
    mock_streamlit.form_submit_button.return_value = False

    app.render_main_analysis_page()


def test_salvar_analise_refinada(mock_streamlit):
    mock_streamlit.session_state["analysis_finished"] = False
    mock_streamlit.session_state["analysis_state"] = make_analysis_state()
    mock_streamlit.session_state["show_generate_plan_button"] = False
    mock_streamlit.session_state.update(TEST_EDIT_STATE)

    context = MagicMock()
    context.__enter__.return_value = True
    context.__exit__.return_value = False
    mock_streamlit.form.return_value = context
    mock_streamlit.form_submit_button.return_value = True

    app.render_main_analysis_page()


@patch("qa_core.app.save_analysis_to_history")
def test_nao_encerrar_fluxo(mock_save, mock_streamlit):
    mock_streamlit.session_state["analysis_finished"] = False
    mock_streamlit.session_state["analysis_state"] = make_analysis_state()
    mock_streamlit.session_state["show_generate_plan_button"] = True
    mock_streamlit.session_state["test_plan_report"] = ""

    cols = mock_streamlit.columns([1, 1, 2])
    cols[0].button.return_value = False
    cols[1].button.return_value = True

    app.render_main_analysis_page()


@patch("qa_core.app.save_analysis_to_history")
@patch("qa_core.app.generate_pdf_report", return_value=b"fakepdf")
@patch("qa_core.app.run_test_plan_graph")
def test_sim_gerar_plano(mock_run, mock_pdf, mock_save, mock_streamlit):
    mock_streamlit.session_state["analysis_finished"] = False
    mock_streamlit.session_state["analysis_state"] = make_analysis_state()
    mock_streamlit.session_state["show_generate_plan_button"] = True

    cols = mock_streamlit.columns([1, 1, 2])
    cols[0].button.return_value = True
    cols[1].button.return_value = False

    mock_run.return_value = {
        "plano_e_casos_de_teste": {
            "casos_de_teste_gherkin": [{"titulo": "CT 1", "cenario": ["passo 1"]}]
        },
        "relatorio_plano_de_testes": "Plano fake",
    }

    app.render_main_analysis_page()


@patch("qa_core.app.reset_session")
def test_nova_analise_button(mock_reset, mock_streamlit):
    mock_streamlit.session_state["analysis_finished"] = True
    mock_streamlit.session_state["analysis_state"] = make_analysis_state()
    mock_streamlit.session_state["test_plan_report"] = "Plano final"
    mock_streamlit.session_state["history_saved"] = True

    def button_side_effect(*args, **kwargs):
        if kwargs.get("key") == "nova_analise_button" and kwargs.get("on_click"):
            kwargs["on_click"]()
            return True
        return False

    mock_streamlit.button.side_effect = button_side_effect

    app.render_main_analysis_page()

    assert "history_saved" not in mock_streamlit.session_state
    mock_reset.assert_called_once_with()


def test_sem_user_story_mostra_warning(mock_streamlit):
    mock_streamlit.session_state.clear()
    mock_streamlit.session_state["analysis_state"] = None
    mock_streamlit.session_state["user_story_input"] = ""
    mock_streamlit.button.return_value = True

    app.render_main_analysis_page()
    mock_streamlit.warning.assert_called_once_with(
        "Erro na User Story: String should have at least 10 characters"
    )


def test_salvar_edicao_formulario(mock_streamlit):
    mock_streamlit.session_state["analysis_finished"] = False
    mock_streamlit.session_state["analysis_state"] = TEST_ANALYSIS_STATE.copy()
    mock_streamlit.session_state.update(TEST_EDIT_STATE)

    context = MagicMock()
    context.__enter__.return_value = True
    context.__exit__.return_value = False
    mock_streamlit.form.return_value = context
    mock_streamlit.form_submit_button.return_value = True

    app.render_main_analysis_page()

    assert (
        mock_streamlit.session_state["analysis_state"]["analise_da_us"][
            "avaliacao_geral"
        ]
        == TEST_EDIT_STATE["edit_avaliacao"]
    )
    assert (
        TEST_EDIT_STATE["edit_pontos"]
        in mock_streamlit.session_state["analysis_state"]["analise_da_us"][
            "pontos_ambiguos"
        ]
    )


@patch("qa_core.app._render_export_section")
def test_render_main_analysis_page_exportadores(mock_render_export, mock_streamlit):
    test_df = pd.DataFrame(TEST_DF_BASIC)
    mock_streamlit.session_state.update(TEST_SESSION_STATE_FINISHED.copy())
    mock_streamlit.session_state["test_plan_df"] = test_df

    app.render_main_analysis_page()

    mock_render_export.assert_called_once()
