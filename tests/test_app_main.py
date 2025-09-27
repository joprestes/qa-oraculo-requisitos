# test_app_main.py
import pytest
from unittest.mock import patch, MagicMock
import app
import pandas as pd


# ----------------------------
# Fixture para mock do st
# ----------------------------
class SessionState(dict):
    """Simula o st.session_state com dot notation"""
    def __getattr__(self, key):
        return self.get(key, None)
    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def mock_st():
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


@patch("app.reset_session")
def test_nova_analise_button(mock_reset, mock_st):
    mock_st.session_state["analysis_finished"] = True
    mock_st.session_state["analysis_state"] = make_analysis_state()
    mock_st.session_state["test_plan_report"] = "Plano final"

    mock_st.button.return_value = True

    app.render_main_analysis_page()


# ----------------------------
# Casos extras de cobertura
# ----------------------------
def test_sem_user_story_mostra_warning(mock_st):
    mock_st.session_state.clear()
    mock_st.session_state["analysis_state"] = None
    mock_st.session_state["user_story_input"] = ""
    mock_st.button.return_value = True

    app.render_main_analysis_page()
    mock_st.warning.assert_called_once_with("Por favor, insira uma User Story antes de analisar.")


def test_salvar_edicao_formulario(mock_st):
    mock_st.session_state["analysis_finished"] = False
    mock_st.session_state["analysis_state"] = {
        "user_story": "Como usuário, quero salvar edições",
        "analise_da_us": {
            "avaliacao_geral": "Velha",
            "pontos_ambiguos": [],
            "perguntas_para_po": [],
            "sugestao_criterios_aceite": [],
            "riscos_e_dependencias": [],
        },
    }
    mock_st.session_state["edit_avaliacao"] = "Nova avaliação"
    mock_st.session_state["edit_pontos"] = "Novo ponto"
    mock_st.session_state["edit_perguntas"] = "Nova pergunta"
    mock_st.session_state["edit_criterios"] = "Novo critério"
    mock_st.session_state["edit_riscos"] = "Novo risco"

    mock_st.form.return_value.__enter__.return_value = True
    mock_st.form_submit_button.return_value = True

    app.render_main_analysis_page()

    assert mock_st.session_state["analysis_state"]["analise_da_us"]["avaliacao_geral"] == "Nova avaliação"
    assert "Novo ponto" in mock_st.session_state["analysis_state"]["analise_da_us"]["pontos_ambiguos"]


def test_exportacao_final_completa(mock_st):
    mock_st.session_state["analysis_finished"] = True
    mock_st.session_state["analysis_state"] = {"relatorio_analise_inicial": "Relatório inicial"}
    mock_st.session_state["test_plan_report"] = "Plano fake"
    mock_st.session_state["test_plan_df"] = pd.DataFrame([{"id": "CT1", "titulo": "Teste"}])
    mock_st.session_state["pdf_report_bytes"] = b"fakepdf"

    # Mocka 4 colunas com download_button configurado
    cols = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    for col in cols:
        col.download_button = MagicMock(return_value=True)  # ✅ garante chamada
    mock_st.columns.return_value = cols

    app.render_main_analysis_page()

    # Garante que columns foi chamado
    assert mock_st.columns.call_count >= 1

    # Garante que pelo menos 1 botão de download foi chamado
    assert any(col.download_button.called for col in cols), "Nenhum botão de download foi chamado"

    # Confere que o expander foi aberto
    mock_st.expander.assert_any_call("Opções de Exportação para Ferramentas Externas", expanded=True)
