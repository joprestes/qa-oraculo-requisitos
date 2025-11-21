import json
from unittest.mock import MagicMock, patch

import pandas as pd

from qa_core import app

FOUR_COLUMN_COUNT = 4
TWO_COLUMN_COUNT = 2


def test_render_main_analysis_page_sem_analysis_state(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state.update(
        {"analysis_finished": False, "analysis_state": None, "user_story_input": ""}
    )
    mocked_st.button.return_value = False

    app.render_main_analysis_page()
    mocked_st.text_area.assert_any_call(
        label="Insira a User Story aqui:",
        height=250,
        key="user_story_input",
        help="Digite ou cole sua User Story no formato: Como [persona], quero [ação], para [objetivo].\n\n💡 Use Tab para navegar entre campos.",
        placeholder="Exemplo: Como usuário do app, quero redefinir minha senha via email...",
    )


def test_render_main_analysis_page_sem_user_story(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state.update(
        {"analysis_finished": False, "analysis_state": None, "user_story_input": ""}
    )
    mocked_st.button.return_value = True

    app.render_main_analysis_page()
    mocked_st.warning.assert_called_once_with(
        "Erro na User Story: String should have at least 10 characters"
    )


@patch("qa_core.app.st")
def test_render_main_analysis_page_downloads_sem_dados(mock_st):
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

    col1, col2, _ = mocked_st.columns([1, 1, 2])
    col1.button.return_value = False
    col2.button.return_value = True

    with patch("qa_core.app._save_current_analysis_to_history") as mock_save:
        app.render_main_analysis_page()

    assert mocked_st.session_state["analysis_finished"] is True
    mock_save.assert_called()
    mocked_st.rerun.assert_called()


def test_render_main_page_falha_na_geracao_do_plano(mocked_st):
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

    mocked_st.button.side_effect = (
        lambda label, **kwargs: label == "Sim, Gerar Plano de Testes"
    )
    resultado_invalido = {
        "relatorio_plano_de_testes": "Falhou",
        "plano_e_casos_de_teste": {"casos_de_teste_gherkin": None},
    }

    with (
        patch("qa_core.app.run_test_plan_graph", return_value=resultado_invalido),
        patch("qa_core.app._save_current_analysis_to_history"),
    ):
        app.render_main_analysis_page()

    mocked_st.error.assert_called_with(
        "O Oráculo não conseguiu gerar um plano de testes estruturado."
    )
    assert mocked_st.session_state["analysis_finished"] is True
    mocked_st.rerun.assert_called()


def test_render_main_page_edicao_e_salvamento_gherkin(mocked_st):
    """
    Testa que cenários são exibidos em modo de visualização por padrão.
    Com a nova UX, edições só são salvas quando o usuário clica em 'Confirmar'.
    """
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
            "test_plan_report_intro": "Resumo original",
            "test_plan_df_records": [
                {
                    "id": 1,
                    "titulo": "Login válido",
                    "prioridade": "Alta",
                    "criterio_de_aceitacao_relacionado": "Usuário autenticado",
                    "justificativa_acessibilidade": "",
                    "cenario": "Cenário antigo",
                }
            ],
            "test_plan_df_json": json.dumps(
                [
                    {
                        "id": 1,
                        "titulo": "Login válido",
                        "prioridade": "Alta",
                        "criterio_de_aceitacao_relacionado": "Usuário autenticado",
                        "justificativa_acessibilidade": "",
                        "cenario": "Cenário antigo",
                    }
                ],
                ensure_ascii=False,
            ),
            "user_story_input": "US de login",
            "analysis_state": {"relatorio_analise_inicial": "Análise mock"},
        }
    )

    # Cenários agora são exibidos em modo de visualização por padrão (st.code)
    # Não há auto-save, então o relatório não deve mudar
    app.render_main_analysis_page()

    # Verifica que o relatório permanece inalterado (modo visualização)
    assert mocked_st.session_state["test_plan_report"] == "### 🧩 Login válido\n```gherkin\nCenário antigo\n```"
    # st.code deve ter sido chamado para exibir o cenário
    mocked_st.code.assert_called()


VALID_USER_STORY = (
    "Como tester, quero validar o fluxo para garantir a qualidade do produto"
)
INCOMPLETE_USER_STORY = "Quero validar o fluxo"


def test_render_user_story_input_fluxo_sucesso(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state["user_story_input"] = VALID_USER_STORY

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
    mock_grafo.assert_called_once_with(VALID_USER_STORY)
    assert (
        mocked_st.session_state["analysis_state"]["analise_da_us"]["avaliacao"] == "ok"
    )
    assert mocked_st.session_state["show_generate_plan_button"] is False
    mocked_st.rerun.assert_called()


def test_render_user_story_input_incompleta(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state["user_story_input"] = INCOMPLETE_USER_STORY

    with (
        patch("qa_core.app.accessible_button", return_value=True),
        patch("qa_core.app.run_analysis_graph") as mock_grafo,
        patch("qa_core.app.announce") as mock_announce,
    ):
        resultado = app._render_user_story_input()

    assert resultado is True
    mock_grafo.assert_not_called()

    mensagens_emitidas = [
        args[0].lower() for args, _ in mock_announce.call_args_list if args
    ]
    assert any(
        "incompleta" in mensagem and "persona" in mensagem
        for mensagem in mensagens_emitidas
    )
    assert any(
        "exemplos" in mensagem and "como gerente de contas" in mensagem
        for mensagem in mensagens_emitidas
    )
    assert mocked_st.session_state.get("analysis_state") is None
    assert mocked_st.session_state.get("show_generate_plan_button") is False
    mocked_st.rerun.assert_not_called()


def test_render_main_page_gera_plano_com_sucesso(mocked_st):
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

    original_columns_side_effect = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == [1, 1, 2]:
            col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
            col1.button.return_value = True
            col2.button.return_value = False
            return (col1, col2, col3)
        if arg == FOUR_COLUMN_COUNT:
            return tuple(MagicMock() for _ in range(FOUR_COLUMN_COUNT))
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

    with patch("qa_core.app.announce") as mock_announce:
        app.render_main_analysis_page()

    mock_announce.assert_any_call(
        "Este caso de teste ainda não possui cenário em formato Gherkin.",
        "info",
        st_api=mocked_st,
    )


def test_render_main_page_dispara_confirmacao_exclusao(mocked_st):
    df = pd.DataFrame(
        [
            {
                "id": "CT-1",
                "titulo": "Caso 1",
                "prioridade": "Alta",
                "criterio_de_aceitacao_relacionado": "",
                "justificativa_acessibilidade": "",
                "cenario": "Dado algo\nEntão resultado",
            }
        ]
    )

    mocked_st.session_state.update(
        {
            "analysis_finished": True,
            "analysis_state": {"relatorio_analise_inicial": "Relatório"},
            "test_plan_df": df,
            "test_plan_report": "Relatório",
            "test_plan_report_intro": "Relatório",
            "test_plan_df_records": df.to_dict(orient="records"),
            "test_plan_df_json": json.dumps(
                df.to_dict(orient="records"), ensure_ascii=False
            ),
            "pdf_report_bytes": b"bytes",
        }
    )

    mocked_st.button.side_effect = (
        lambda label=None, **kwargs: kwargs.get("key") == "delete_case_0"
    )

    app.render_main_analysis_page()

    pending = mocked_st.session_state.get("pending_case_deletion")
    assert pending is not None
    assert pending["row_index"] == 0
    assert "Caso 1" in pending["label"]
    assert pending["test_id"] == "CT-1"
    assert pending["title"] == "Caso 1"


def test_render_main_page_confirma_exclusao_remove_cenario(mocked_st):
    df = pd.DataFrame(
        [
            {
                "id": "CT-1",
                "titulo": "Caso 1",
                "prioridade": "Alta",
                "criterio_de_aceitacao_relacionado": "",
                "justificativa_acessibilidade": "",
                "cenario": "Dado\nQuando\nEntão",
            },
            {
                "id": "CT-2",
                "titulo": "Caso 2",
                "prioridade": "Média",
                "criterio_de_aceitacao_relacionado": "",
                "justificativa_acessibilidade": "",
                "cenario": "Dado outro\nEntão outro",
            },
        ]
    )

    mocked_st.session_state.update(
        {
            "analysis_finished": True,
            "analysis_state": {"relatorio_analise_inicial": "Relatório"},
            "test_plan_df": df,
            "test_plan_report": "Relatório",
            "test_plan_report_intro": "Relatório",
            "test_plan_df_records": df.to_dict(orient="records"),
            "test_plan_df_json": json.dumps(
                df.to_dict(orient="records"), ensure_ascii=False
            ),
            "pdf_report_bytes": b"bytes",
            "pending_case_deletion": {
                "row_index": 0,
                "label": "CT-1 — Caso 1",
                "test_id": "CT-1",
                "title": "Caso 1",
            },
        }
    )

    mocked_st.button.side_effect = (
        lambda label=None, **kwargs: kwargs.get("key") == "confirm_delete_case_0"
    )

    with (
        patch("qa_core.app.generate_pdf_report", return_value=b"novo_pdf") as mock_pdf,
        patch("qa_core.app._save_current_analysis_to_history") as mock_save,
    ):
        app.render_main_analysis_page()

    updated_df = mocked_st.session_state["test_plan_df"]
    assert len(updated_df) == 1
    assert updated_df.iloc[0]["id"] == "CT-2"
    assert mocked_st.session_state.get("pending_case_deletion") is None
    mock_save.assert_called_once_with(update_existing=True)
    mock_pdf.assert_called_once()
    assert mocked_st.session_state["pdf_report_bytes"] == b"novo_pdf"
    assert mocked_st.session_state["test_plan_df_records"] == [
        df.to_dict(orient="records")[1]
    ]
    assert "### 🧩" in mocked_st.session_state["test_plan_report"]
    assert "Caso 2" in mocked_st.session_state["test_plan_report"]
    mocked_st.toast.assert_called_with("🗑️ Cenário excluído com sucesso.")
    mocked_st.rerun.assert_called()
