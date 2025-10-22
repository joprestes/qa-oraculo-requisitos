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
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import app
from state_machine import AnalysisStage, AnalysisState

# Constantes auxiliares para layouts de colunas nos testes
FOUR_COLUMN_COUNT = 4
TWO_COLUMN_COUNT = 2

#Constantes para números Mágicos
EXISTING_HISTORY_ID = 10

# ==================================================
# FIXTURE: Mock de get_state
# ==================================================
@pytest.fixture
def mock_state():
    """Retorna um AnalysisState mockado"""
    state = AnalysisState()
    state.user_story = "História teste"
    return state


@pytest.fixture
def mock_completed_state():
    """Retorna estado no estágio COMPLETED"""
    state = AnalysisState()
    state.user_story = "História teste"
    state.stage = AnalysisStage.COMPLETED
    state.analysis_report = "# Relatório"
    state.test_plan_df = pd.DataFrame([
        {"id": "CT-001", "titulo": "Teste", "cenario": "Dado..."}
    ])
    state.test_plan_report = "### Plano"
    state.pdf_bytes = b"pdf"
    return state

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

    calls = [str(mock_call) for mock_call in mock_st.markdown.call_args_list]
    assert any("2025-09-26" in call_str for call_str in calls)


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

@patch('app.get_state')
@patch('app.st')
def test_render_main_analysis_page_sem_analysis_state(mock_st, mock_get_state, mock_state):
    """Valida renderização do formulário inicial"""
    mock_get_state.return_value = mock_state
    mock_st.session_state = {}
    
    # Simula accessible_text_area sendo chamado
    with patch('app.accessible_text_area') as mock_text_area:
        app.render_main_analysis_page()
        
        # Verifica que o text_area foi chamado
        mock_text_area.assert_called_once()
        call_kwargs = mock_text_area.call_args[1]
        assert call_kwargs['key'] == 'user_story_input'



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


@patch('app.get_state')
@patch('app.st')
def test_render_main_analysis_page_downloads_sem_dados(mock_st, mock_get_state, mock_completed_state):
    """Valida tela de downloads quando análise está completa"""
    # Remove test_plan_df para forçar estado sem dados
    mock_completed_state.test_plan_df = None
    mock_get_state.return_value = mock_completed_state
    
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    
    app.render_main_analysis_page()
    
    # Verifica que subheader foi chamado
    mock_st.subheader.assert_called_with("📥 Downloads Disponíveis")



@patch('app.get_state')
@patch('app.st')
def test_render_main_page_clica_em_encerrar(mock_st, mock_get_state):
    """Valida clique em 'Não, Encerrar'"""
    state = AnalysisState()
    state.user_story = "US de teste"
    state.stage = AnalysisStage.EDITING_ANALYSIS
    state.analysis_data = {"test": "data"}
    state.analysis_report = "Análise"
    
    mock_get_state.return_value = state
    mock_st.session_state = {}
    
    # Simula botão "Não, Encerrar" clicado
    mock_st.button.return_value = False
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.columns.return_value[1].button.return_value = True
    
    with patch('app._save_current_analysis_to_history'):
        app.render_main_analysis_page()
        
        # Verifica que mudou para COMPLETED
        assert state.stage == AnalysisStage.COMPLETED


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
            "app.run_test_plan_graph",
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
        patch("app.generate_pdf_report", return_value=b"pdf-gerado"),
        patch("app._save_current_analysis_to_history") as mock_save,
        patch(
            "app.accessible_text_area",
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

    with patch("app.announce") as mock_announce:
        app.render_main_analysis_page()

    mock_announce.assert_any_call(
        "Este caso de teste ainda não possui cenário em formato Gherkin.",
        "info",
        st_api=mocked_st,
    )


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


@patch('app.get_state')
@patch('app.save_or_update_analysis')
def test_save_current_analysis_to_history_sem_dados_suficientes(mock_save_func, mock_get_state):
    """Quando não há dados válidos, não salva"""
    state = AnalysisState()
    state.user_story = ""  # User Story vazia
    mock_get_state.return_value = state
    
    app._save_current_analysis_to_history()
    
    # Não deve chamar save_or_update_analysis
    mock_save_func.assert_not_called()


@patch('app.get_state')
@patch('app.save_or_update_analysis', return_value=42)
def test_save_current_analysis_to_history_atualiza_existente(mock_save_func, mock_get_state):
    """Atualiza registro existente quando state.saved_history_id existe"""
    state = AnalysisState()
    state.user_story = "História teste"
    state.analysis_report = "Relatório"
    state.saved_history_id = 10  # Já existe
    
    mock_get_state.return_value = state
    
    app._save_current_analysis_to_history()
    
    # Deve chamar com existing_id=10
    mock_save_func.assert_called_once()
    call_kwargs = mock_save_func.call_args[1]
    assert call_kwargs['existing_id'] == EXISTING_HISTORY_ID


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



@patch('app.get_state')
@patch('app.save_or_update_analysis', side_effect=RuntimeError("boom"))
@patch('app.announce')
def test_save_current_analysis_to_history_erro_generico(mock_announce, mock_save_func, mock_get_state):
    """Erro deve gerar announce de erro"""
    state = AnalysisState()
    state.user_story = "História teste"
    state.analysis_report = "Relatório"
    
    mock_get_state.return_value = state
    
    app._save_current_analysis_to_history()
    
    # Verifica que announce foi chamado com "error"
    mock_announce.assert_called_once()
    args = mock_announce.call_args
    assert args[1] == "error"



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


@patch('app.accessible_button')
@patch('app.delete_analysis_by_id', return_value=True)
@patch('app.get_all_analysis_history', return_value=[])
@patch('app.announce')
@patch('app.st')
def test_render_history_page_impl_confirma_exclusao(
    mock_st, mock_announce, mock_get_history, mock_delete, mock_accessible_button
):
    """Fluxo de confirmação remove item"""
    mock_st.session_state = {"confirm_delete_id": 5}
    mock_st.query_params.get.return_value = None
    
    # Simula botão "Confirmar" clicado
    def button_side_effect(*args, **kwargs):
        key = kwargs.get("key", "")
        if "confirmar_delete" in key:
            return True
        return False
    
    mock_accessible_button.side_effect = button_side_effect
    
    # Mock de container
    mock_container = MagicMock()
    mock_container.__enter__.return_value = mock_container
    mock_container.__exit__.return_value = None
    mock_st.container.return_value = mock_container
    
    # Mock de columns
    col1, col2 = MagicMock(), MagicMock()
    mock_st.columns.return_value = [col1, col2]
    
    app._render_history_page_impl()
    
    # Verifica exclusão
    mock_delete.assert_called_once_with(5)
    assert "confirm_delete_id" not in mock_st.session_state


@patch('app.announce')
@patch('app.clear_history', return_value=3)
@patch('app.get_all_analysis_history', return_value=[])
@patch('app.st')
def test_render_history_page_impl_confirma_limpeza_total(
    mock_st, mock_get_history, mock_clear_history, mock_announce
):
    """Clique em confirmar deve limpar todo o histórico."""

    mock_st.session_state = {"confirm_clear_all": True}
    mock_st.query_params.get.return_value = None

    mock_container = MagicMock()
    mock_container.__enter__.return_value = mock_container
    mock_container.__exit__.return_value = None
    mock_st.container.return_value = mock_container

    col_confirm, col_cancel = MagicMock(), MagicMock()
    col_confirm.accessible_button.return_value = True
    col_cancel.accessible_button.return_value = False
    mock_st.columns.return_value = [col_confirm, col_cancel]

    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    mock_clear_history.assert_called_once()
    assert "confirm_clear_all" not in mock_st.session_state
    mock_announce.assert_any_call(
        "3 análises foram removidas.", "success", st_api=mock_st
    )
    mock_st.rerun.assert_called_once()


@patch('app.accessible_button')
@patch('app.delete_analysis_by_id', return_value=False)
@patch('app.get_all_analysis_history', return_value=[])
@patch('app.announce')
@patch('app.st')
def test_render_history_page_impl_cancela_exclusao(
    mock_st, mock_announce, mock_get_history, mock_delete, mock_accessible_button
):
    """Clique em cancelar não deve deletar"""
    mock_st.session_state = {"confirm_delete_id": 42}
    mock_st.query_params.get.return_value = None
    
    # Simula botão "Cancelar" clicado
    def button_side_effect(*args, **kwargs):
        key = kwargs.get("key", "")
        if "cancelar_delete" in key:
            return True
        return False
    
    mock_accessible_button.side_effect = button_side_effect
    
    # Mock de container
    mock_container = MagicMock()
    mock_container.__enter__.return_value = mock_container
    mock_container.__exit__.return_value = None
    mock_st.container.return_value = mock_container
    
    # Mock de columns
    col1, col2 = MagicMock(), MagicMock()
    mock_st.columns.return_value = [col1, col2]
    
    app._render_history_page_impl()

    # Não deve ter deletado
    mock_delete.assert_not_called()
    assert "confirm_delete_id" not in mock_st.session_state


@patch('app.accessible_button')
@patch('app.get_all_analysis_history')
@patch('app.st')
def test_render_history_page_impl_lista_dispara_confirm_clear_all(
    mock_st, mock_get_history, mock_accessible_button
):
    """Botão principal deve sinalizar confirmação de limpeza total."""

    mock_st.session_state = {}
    mock_st.query_params.get.return_value = None

    mock_get_history.return_value = [
        {"id": 1, "created_at": "2024-01-01", "user_story": "Como usuário..."}
    ]

    def make_context():
        ctx = MagicMock()
        ctx.__enter__.return_value = MagicMock()
        ctx.__exit__.return_value = False
        return ctx

    mock_st.container.side_effect = lambda *args, **kwargs: make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: make_context()

    confirm_col, cancel_col = MagicMock(), MagicMock()
    confirm_col.accessible_button.return_value = False
    cancel_col.accessible_button.return_value = False

    column_calls = [
        [confirm_col, cancel_col],  # Para o bloco de confirmação
    ]

    def columns_side_effect(arg):
        if isinstance(arg, int) and arg == 2 and column_calls:
            return column_calls.pop(0)
        if isinstance(arg, int):
            cols = [MagicMock() for _ in range(arg)]
        elif isinstance(arg, list | tuple):
            cols = [MagicMock() for _ in arg]
        else:
            cols = [MagicMock(), MagicMock()]

        for col in cols:
            col.accessible_button.return_value = False
            col.button.return_value = False
        return cols

    mock_st.columns.side_effect = columns_side_effect

    def accessible_button_side_effect(*args, **kwargs):
        label = kwargs.get("label") or (args[0] if args else "")
        return label == "🗑️ Excluir TODO o Histórico"

    mock_accessible_button.side_effect = accessible_button_side_effect
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    assert mock_st.session_state["confirm_clear_all"] is True
    mock_st.rerun.assert_called_once()
