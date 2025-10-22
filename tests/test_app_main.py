# tests/test_app_main.py (SUBSTITUIR IMPORTS)
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import app
import state_manager
from state_machine import AnalysisStage, AnalysisState


# ----------------------------
# Fixture para mock do st
# ----------------------------
class SessionState(dict):
    """Simula o st.session_state com dot notation."""

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def mock_st():
    """Mocka o módulo Streamlit para isolar comportamento durante os testes."""
    with patch("app.st") as mock_st:
        mock_st.session_state = SessionState()

        # Mock para st.columns que devolve a quantidade correta
        def fake_columns(arg):
            if arg == [1, 1, 2]:
                return [MagicMock(), MagicMock(), MagicMock()]
            if arg == 4:
                return [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            if arg == 2:
                return [MagicMock(), MagicMock()]
            return [MagicMock(), MagicMock(), MagicMock()]

        mock_st.columns.side_effect = fake_columns
        yield mock_st

    import streamlit as real_streamlit

    state_manager.set_streamlit_module(real_streamlit)


# ----------------------------
# Função auxiliar
# ----------------------------
def make_analysis_state():
    return {
        "user_story": "Como usuário quero testar o oráculo",
        "analise_da_us": {
            "avaliacao_geral": "Boa US",
            "pontos_ambiguos": ["Ambiguidade 1"],
            "perguntas_para_po": ["Pergunta 1"],
            "sugestao_criterios_aceite": ["Critério 1"],
            "riscos_e_dependencias": ["Risco 1"],
        },
        "relatorio_analise_inicial": "Relatório inicial",
    }


# ----------------------------
# Testes principais
# ----------------------------
def test_analise_iniciada_nao_salva(mock_st):
    mock_st.session_state["analysis_finished"] = False
    mock_st.session_state["analysis_state"] = make_analysis_state()
    mock_st.session_state["show_generate_plan_button"] = False

    mock_st.form.return_value.__enter__.return_value = True
    mock_st.form_submit_button.return_value = False

    app.render_main_analysis_page()


def test_salvar_analise_refinada(mock_st):
    mock_st.session_state["analysis_finished"] = False
    mock_st.session_state["analysis_state"] = make_analysis_state()
    mock_st.session_state["show_generate_plan_button"] = False
    mock_st.session_state["edit_avaliacao"] = "Nova avaliação"
    mock_st.session_state["edit_pontos"] = "Novo ponto"
    mock_st.session_state["edit_perguntas"] = "Nova pergunta"
    mock_st.session_state["edit_criterios"] = "Novo critério"
    mock_st.session_state["edit_riscos"] = "Novo risco"

    mock_st.form.return_value.__enter__.return_value = True
    mock_st.form_submit_button.return_value = True

    app.render_main_analysis_page()


@patch("app.save_analysis_to_history")
def test_nao_encerrar_fluxo(mock_save, mock_st):
    mock_st.session_state["analysis_finished"] = False
    mock_st.session_state["analysis_state"] = make_analysis_state()
    mock_st.session_state["show_generate_plan_button"] = True
    mock_st.session_state["test_plan_report"] = ""

    cols = mock_st.columns([1, 1, 2])
    cols[0].button.return_value = False
    cols[1].button.return_value = True

    app.render_main_analysis_page()


@patch("app.save_analysis_to_history")
@patch("app.generate_pdf_report", return_value=b"fakepdf")
@patch("app.run_test_plan_graph")
def test_sim_gerar_plano(mock_run, mock_pdf, mock_save, mock_st):
    mock_st.session_state["analysis_finished"] = False
    mock_st.session_state["analysis_state"] = make_analysis_state()
    mock_st.session_state["show_generate_plan_button"] = True

    cols = mock_st.columns([1, 1, 2])
    cols[0].button.return_value = True
    cols[1].button.return_value = False

    mock_run.return_value = {
        "plano_e_casos_de_teste": {
            "casos_de_teste_gherkin": [{"titulo": "CT 1", "cenario": ["passo 1"]}]
        },
        "relatorio_plano_de_testes": "Plano fake",
    }

    app.render_main_analysis_page()


# ----------------------------
# Casos extras de cobertura
# ----------------------------
def test_render_main_analysis_page_exportadores(mock_st):
    """Força exibição dos exportadores e verifica se os botões de download são chamados."""
    # --- 1. Configura sessão com dados válidos ---
    df = pd.DataFrame([{"titulo": "CT", "cenario": ["Dado", "Quando", "Então"]}])
    mock_st.session_state.update(
        {
            "analysis_finished": True,
            "analysis_state": {"relatorio_analise_inicial": "Relatório"},
            "test_plan_report": "Plano",
            "test_plan_df": df,
            "pdf_report_bytes": b"pdf",
            "user_story_input": "US Exemplo",
            "area_path_input": "Área QA",
            "assigned_to_input": "Joelma",
        }
    )

    # --- 2. Cria um side_effect inteligente para st.columns ---
    # Cria mocks distintos para cada chamada, para podermos rastreá-los
    cols_downloads = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    cols_azure = [MagicMock(), MagicMock()]

    def columns_side_effect(arg):
        if arg == 4:
            return cols_downloads
        if arg == 2:
            return cols_azure
        # Fallback para outros casos, como [1, 1, 2]
        return [MagicMock(), MagicMock(), MagicMock()]

    mock_st.columns.side_effect = columns_side_effect

    # --- 3. Executa a função com patches de exportação ---
    with (
        patch("app.to_excel", return_value=b"excel"),
        patch("app.gerar_nome_arquivo_seguro", return_value="fake.xlsx"),
    ):
        app.render_main_analysis_page()

    # --- 4. Verifica se os botões de download foram chamados em seus respectivos mocks ---
    # Usamos any() para verificar se PELO MENOS um dos botões de download foi chamado,
    # o que é suficiente para este teste de cobertura.
    assert any(
        col.download_button.called for col in cols_downloads
    ), "Nenhum botão de download principal foi acionado."

@pytest.fixture
def mock_state():
    state = AnalysisState()
    state.user_story = "Como usuário quero testar"
    return state


@patch('app.reset_session')
@patch('app.get_state')
@patch('app.st')
def test_nova_analise_button(mock_st, mock_get_state, mock_reset):
    """Valida reset ao clicar em Nova Análise"""
    state = AnalysisState()
    state.stage = AnalysisStage.COMPLETED
    state.user_story = "História"

    mock_get_state.return_value = state
    mock_st.session_state = {}

    def make_context():
        ctx = MagicMock()
        ctx.__enter__.return_value = MagicMock()
        ctx.__exit__.return_value = False
        return ctx

    mock_st.expander.side_effect = lambda *args, **kwargs: make_context()

    def columns_side_effect(arg):
        if isinstance(arg, int):
            count = arg
        elif isinstance(arg, list | tuple):
            count = len(arg)
        else:
            count = 2

        cols = [MagicMock() for _ in range(count)]
        for col in cols:
            col.accessible_button.return_value = False
            col.button.return_value = False
            col.download_button.return_value = None
        return cols

    mock_st.columns.side_effect = columns_side_effect
    mock_st.rerun = MagicMock()

    # Simula botão clicado
    def button_side_effect(*args, **kwargs):
        if kwargs.get("key") == "nova_analise_button" and kwargs.get("on_click"):
            kwargs["on_click"]()
            return True
        return False
    
    with patch('app.accessible_button', side_effect=button_side_effect):
        app.render_main_analysis_page()
    
    # Verifica que reset_session foi chamado
    mock_reset.assert_called_once()


@patch('app.get_state')
@patch('app.announce')
@patch('app.st')
def test_sem_user_story_mostra_warning(mock_st, mock_announce, mock_get_state):
    """Valida warning quando User Story está vazia"""
    state = AnalysisState()
    state.user_story = ""
    mock_get_state.return_value = state
    
    mock_st.session_state = {"user_story_input": ""}
    
    # Simula botão clicado
    with patch('app.accessible_button', return_value=True):
        app.render_main_analysis_page()

    # Verifica que announce foi chamado com warning
    mock_announce.assert_called_once()
    args = mock_announce.call_args[0]
    assert "insira uma user story" in args[0].lower()
    assert args[1] == "warning"


@patch('app.get_state')
@patch('app.st')
def test_salvar_edicao_formulario(mock_st, mock_get_state):
    """Valida salvamento de edições do formulário"""
    state = AnalysisState()
    state.user_story = "História"
    state.stage = AnalysisStage.EDITING_ANALYSIS
    state.analysis_data = {
        "avaliacao_geral": "Velha",
        "pontos_ambiguos": [],
        "perguntas_para_po": [],
        "sugestao_criterios_aceite": [],
        "riscos_e_dependencias": []
    }
    
    mock_get_state.return_value = state
    
    # Simula valores editados
    mock_st.session_state = {
        "edit_avaliacao": "Nova avaliação",
        "edit_pontos": "",
        "edit_perguntas": "",
        "edit_criterios": "",
        "edit_riscos": ""
    }
    
    # Simula form submetido
    mock_form = MagicMock()
    mock_form.__enter__.return_value = mock_form
    mock_form.__exit__.return_value = None
    mock_st.form.return_value = mock_form
    mock_st.form_submit_button.return_value = True

    def columns_side_effect(arg):
        if isinstance(arg, int):
            count = arg
        elif isinstance(arg, list | tuple):
            count = len(arg)
        else:
            count = 2

        cols = [MagicMock() for _ in range(count)]
        for col in cols:
            col.button.return_value = False
            col.accessible_button.return_value = False
        return cols

    mock_st.columns.side_effect = columns_side_effect
    mock_st.rerun = MagicMock()

    app.render_main_analysis_page()

    # Verifica que analysis_data foi atualizado
    assert state.analysis_data["avaliacao_geral"] == "Nova avaliação"
