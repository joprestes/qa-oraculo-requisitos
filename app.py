# ==========================================================
# app.py — Aplicação principal do QA Oráculo
# ==========================================================
# 📘 Este arquivo define toda a interface Streamlit do projeto:
#   - Página principal de análise de User Stories
#   - Geração de plano de testes (IA)
#   - Exportações (Markdown, PDF, CSV Azure, XLSX Zephyr)
#   - Histórico de análises (visualização e exclusão)
#
# 🎯 Princípios (QA Oráculo):
#   • Código modular (funções separadas por responsabilidade)
#   • Acessibilidade + automação de testes (data-testid / navegação teclado)
#   • Preparado para testes unitários e E2E
#   • Comentários didáticos onde a lógica não for óbvia
# ==========================================================

import pandas as pd
import streamlit as st

# ===== Reexportações para compatibilidade com testes =====
# Os testes (tests/test_app_history_delete.py) fazem patch direto em:
# - app.delete_analysis_by_id
# - app.clear_history
# Por isso reexportamos estas funções do database aqui.
# Demais funções do banco: leitura/consulta e persistência no histórico
from database import (
    clear_history,
    delete_analysis_by_id,
    get_all_analysis_history,
    get_analysis_by_id,
    init_db,
    save_analysis_to_history,
)

# Grafos de IA (LangGraph) — invocados nas funções cacheadas
from graph import grafo_analise, grafo_plano_testes

# Gerador de PDF — consolida análise e plano de testes em um relatório
from pdf_generator import generate_pdf_report

# Estado global e reset — para nova análise sem resquícios
from state_manager import initialize_state, reset_session

# Utilitários — helpers de exportação, normalização e formatação
from utils import (
    clean_markdown_report,
    gerar_csv_azure_from_df,  # ✅ Exportador CSV (Azure DevOps)
    gerar_nome_arquivo_seguro,
    get_flexible,
    preparar_df_para_zephyr_xlsx,
    to_excel,
)


# ==========================================================
# 🔒 Auxiliar: garante bytes no download_button
# ==========================================================
def _ensure_bytes(data):
    """
    Garante que o conteúdo entregue ao st.download_button está em bytes.

    Por quê?
    - O Streamlit aceita bytes/bytearray como conteúdo binário.
    - Aqui convertemos strings, objetos com getvalue() (ex. BytesIO),
      e qualquer outro tipo para bytes de forma segura.
    """
    if isinstance(data, str):
        return data.encode("utf-8")

    if hasattr(data, "getvalue"):
        try:
            return data.getvalue()
        except Exception:
            # Se getvalue falhar, cai para as alternativas abaixo
            pass

    if isinstance(data, (bytes, bytearray)):
        return data

    # Fallback absoluto — converte para string e depois para bytes
    return bytes(str(data), "utf-8")


# ==========================================================
# 🚀 Funções cacheadas (IA via LangGraph)
# ==========================================================
@st.cache_data(show_spinner=False)
def run_analysis_graph(user_story: str):
    """
    Executa o grafo de análise de User Story.
    Retorna um dicionário com:
      - 'analise_da_us': blocos estruturados (avaliacao/pontos/riscos/criterios/perguntas)
      - 'relatorio_analise_inicial': texto consolidado em Markdown
    """
    return grafo_analise.invoke({"user_story": user_story})


@st.cache_data(show_spinner=False)
def run_test_plan_graph(analysis_state: dict):
    """
    Executa o grafo de geração de Plano de Testes.
    Espera receber o estado de análise refinado.
    Retorna:
      - 'plano_e_casos_de_teste' com 'casos_de_teste_gherkin' (lista de cenários)
      - 'relatorio_plano_de_testes' (Markdown)
    """
    return grafo_plano_testes.invoke(analysis_state)


# ==========================================================
# 🧠 Página Principal — Análise de User Story
# ==========================================================
def render_main_analysis_page():  # noqa: C901, PLR0912, PLR0915
    """
    Fluxo da página principal:

    1) Entrada da User Story (text_area) + Execução da análise de IA.
    2) Edição humana dos blocos sugeridos (form).
    3) Geração do Plano de Testes (IA) com base na análise refinada.
    4) Exportações (MD, PDF, CSV Azure, XLSX Zephyr).
    5) Botão para iniciar uma nova análise (reset).
    """
    st.title("🤖 QA Oráculo")
    st.markdown(
        "Seja bem-vindo! Como seu Assistente de QA Sênior, estou aqui para apoiar na revisão de User Stories. "
        "Cole uma abaixo e vamos começar."
    )

    # ------------------------------------------------------
    # 1) Entrada e execução da análise inicial
    # ------------------------------------------------------
    if not st.session_state.get("analysis_finished", False):

        # Se ainda não há análise no estado, exibimos o input inicial
        if not st.session_state.get("analysis_state"):
            st.text_area(
                "Insira a User Story aqui:", height=250, key="user_story_input"
            )

            # Botão que dispara a análise inicial usando o grafo
            if st.button("Analisar User Story", type="primary"):
                user_story_txt = st.session_state.get("user_story_input", "")

                if user_story_txt.strip():
                    with st.spinner(
                        "🔮 O Oráculo está realizando a análise inicial..."
                    ):
                        resultado_analise = run_analysis_graph(user_story_txt)

                        # Guarda o resultado bruto da IA para edição posterior
                        st.session_state["analysis_state"] = resultado_analise

                        # Enquanto a edição não é confirmada, não mostramos o botão de gerar o plano
                        st.session_state["show_generate_plan_button"] = False

                        # Re-renderiza a página para exibir a seção de edição
                        st.rerun()
                else:
                    st.warning("Por favor, insira uma User Story antes de analisar.")

        # ------------------------------------------------------
        # 2) Edição dos blocos gerados pela IA
        # ------------------------------------------------------
        if st.session_state.get("analysis_state"):
            st.divider()

            # Enquanto a edição não for salva, mostramos o formulário editável
            if not st.session_state.get("show_generate_plan_button"):
                st.info(
                    "🔮 O Oráculo gerou a análise abaixo. Revise, edite se necessário e clique em 'Salvar' para prosseguir."
                )

                # Extrai o bloco 'analise_da_us' (estrutura recomendada)
                analise_json = st.session_state.get("analysis_state", {}).get(
                    "analise_da_us", {}
                )

                # Usa get_flexible para aceitar variações de chave que a IA pode devolver
                avaliacao_str = get_flexible(
                    analise_json, ["avaliacao_geral", "avaliacao"], ""
                )
                pontos_list = get_flexible(
                    analise_json, ["pontos_ambiguos", "pontos_de_ambiguidade"], []
                )
                perguntas_list = get_flexible(
                    analise_json, ["perguntas_para_po", "perguntas_ao_po"], []
                )
                criterios_list = get_flexible(
                    analise_json,
                    ["sugestao_criterios_aceite", "criterios_de_aceite"],
                    [],
                )
                riscos_list = get_flexible(
                    analise_json, ["riscos_e_dependencias", "riscos"], []
                )

                # Converte listas em strings com quebra de linha para o form
                pontos_str = "\n".join(pontos_list)
                perguntas_str = "\n".join(perguntas_list)
                criterios_str = "\n".join(criterios_list)
                riscos_str = "\n".join(riscos_list)

                # Formulário de edição — decisão de UX:
                #   editar tudo numa única tela para facilitar a revisão humana.
                with st.form(key="analysis_edit_form"):
                    st.subheader("📝 Análise Editável")

                    st.text_area(
                        "Avaliação Geral",
                        value=avaliacao_str,
                        key="edit_avaliacao",
                        height=75,
                    )

                    st.text_area(
                        "Pontos Ambíguos",
                        value=pontos_str,
                        key="edit_pontos",
                        height=125,
                    )

                    st.text_area(
                        "Perguntas para PO",
                        value=perguntas_str,
                        key="edit_perguntas",
                        height=125,
                    )

                    st.text_area(
                        "Critérios de Aceite",
                        value=criterios_str,
                        key="edit_criterios",
                        height=150,
                    )

                    st.text_area(
                        "Riscos e Dependências",
                        value=riscos_str,
                        key="edit_riscos",
                        height=100,
                    )

                    submitted = st.form_submit_button("Salvar Análise e Continuar")

                # Quando o form é submetido, persistimos as edições no estado
                if submitted:
                    st.session_state.setdefault("analysis_state", {})
                    st.session_state["analysis_state"].setdefault("analise_da_us", {})
                    bloco = st.session_state["analysis_state"]["analise_da_us"]

                    # Salva os campos editados — sempre normalizando para lista onde necessário
                    bloco["avaliacao_geral"] = st.session_state.get(
                        "edit_avaliacao", ""
                    )

                    bloco["pontos_ambiguos"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_pontos", "").split("\n")
                        if linha.strip()
                    ]

                    bloco["perguntas_para_po"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_perguntas", "").split(
                            "\n"
                        )
                        if linha.strip()
                    ]

                    bloco["sugestao_criterios_aceite"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_criterios", "").split(
                            "\n"
                        )
                        if linha.strip()
                    ]

                    bloco["riscos_e_dependencias"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_riscos", "").split("\n")
                        if linha.strip()
                    ]

                    # Agora podemos avançar para a geração de plano
                    st.session_state["show_generate_plan_button"] = True

                    st.success("Análise refinada salva com sucesso!")
                    st.rerun()

        # ------------------------------------------------------
        # 3) Geração do Plano de Testes (após edição)
        # ------------------------------------------------------
        if st.session_state.get("show_generate_plan_button"):

            # Mostra o relatório de análise (texto da IA)
            with st.expander("1. Análise Refinada da User Story", expanded=True):
                st.markdown(
                    st.session_state.get("analysis_state", {}).get(
                        "relatorio_analise_inicial", ""
                    )
                )

            st.info(
                "Deseja que o Oráculo gere um Plano de Testes com base na análise refinada?"
            )
            col1, col2, _ = st.columns([1, 1, 2])

            # Botão para gerar o plano de testes com LangGraph
            if col1.button(
                "Sim, Gerar Plano de Testes", type="primary", use_container_width=True
            ):
                with st.spinner(
                    "🔮 Elaborando o Plano de Testes com base na análise refinada..."
                ):
                    resultado_plano = run_test_plan_graph(
                        st.session_state.get("analysis_state", {})
                    )

                    # Extrai lista de casos Gherkin (se houver)
                    casos_de_teste = resultado_plano.get(
                        "plano_e_casos_de_teste", {}
                    ).get("casos_de_teste_gherkin", [])

                    if not casos_de_teste or not isinstance(casos_de_teste, list):
                        # Caso a IA não retorne o formato esperado
                        st.error(
                            "O Oráculo não conseguiu gerar um plano de testes estruturado."
                        )
                        st.session_state["test_plan_report"] = resultado_plano.get(
                            "relatorio_plano_de_testes", "Falha na geração do plano."
                        )

                    else:
                        # Guarda o relatório detalhado do plano
                        st.session_state["test_plan_report"] = resultado_plano.get(
                            "relatorio_plano_de_testes"
                        )

                        # Converte a lista de cenários para DataFrame
                        df = pd.DataFrame(casos_de_teste)

                        # Normaliza colunas que podem vir como listas (várias linhas)
                        df_clean = df.apply(
                            lambda col: col.apply(
                                lambda x: (
                                    "\n".join(map(str, x)) if isinstance(x, list) else x
                                )
                            )
                        )
                        df_clean.fillna("", inplace=True)

                        st.session_state["test_plan_df"] = df_clean

                        # Gera PDF consolidando análise + plano
                        pdf_bytes = generate_pdf_report(
                            st.session_state.get("analysis_state", {}).get(
                                "relatorio_analise_inicial", ""
                            ),
                            df_clean,
                        )
                        st.session_state["pdf_report_bytes"] = pdf_bytes

                    # Marca o fluxo como finalizado (mostra seção de exportações)
                    st.session_state["analysis_finished"] = True

                    # Persiste no histórico (para consulta futura)
                    user_story_to_save = st.session_state.get("user_story_input", "")
                    analysis_report_to_save = st.session_state.get(
                        "analysis_state", {}
                    ).get("relatorio_analise_inicial", "")
                    test_plan_report_to_save = st.session_state.get(
                        "test_plan_report", ""
                    )

                    save_analysis_to_history(
                        user_story_to_save,
                        analysis_report_to_save,
                        test_plan_report_to_save,
                    )

                    # Re-renderiza para exibir a seção de downloads
                    st.rerun()
                    return  # garante que o fluxo acima finalize aqui

            # Botão para encerrar sem gerar plano (mas salvando análise)
            if col2.button("Não, Encerrar", use_container_width=True):
                st.session_state["analysis_finished"] = True

                user_story_to_save = st.session_state.get("user_story_input", "")
                analysis_report_to_save = st.session_state.get(
                    "analysis_state", {}
                ).get("relatorio_analise_inicial", "")
                test_plan_report_to_save = (
                    st.session_state.get("test_plan_report", "")
                    if st.session_state.get("test_plan_report")
                    else ""
                )

                save_analysis_to_history(
                    user_story_to_save,
                    analysis_report_to_save,
                    test_plan_report_to_save,
                )

                st.rerun()
    # ------------------------------------------------------
    # 4) Tela de resultados e exportações
    # ------------------------------------------------------
    if st.session_state.get("analysis_finished"):
        st.success("Análise concluída com sucesso!")

        # Exibe os blocos de relatório e plano de testes (se existirem)
        if st.session_state.get("analysis_state"):
            with st.expander("1. Análise Refinada da User Story", expanded=True):
                st.markdown(
                    st.session_state.get("analysis_state", {}).get(
                        "relatorio_analise_inicial", ""
                    )
                )

        if st.session_state.get("test_plan_report"):
            with st.expander("2. Plano de Testes Detalhado", expanded=True):
                cleaned_report = clean_markdown_report(
                    st.session_state.get("test_plan_report", "")
                )
                st.markdown(cleaned_report)

                # Mostra tabela e cenários em Gherkin
                if (
                    st.session_state.get("test_plan_df") is not None
                    and not st.session_state.get("test_plan_df").empty
                ):
                    st.dataframe(
                        st.session_state.get("test_plan_df"), use_container_width=True
                    )
                    st.subheader("📜 Cenários em Gherkin")
                    for _, row in st.session_state["test_plan_df"].iterrows():
                        if row.get("cenario"):
                            st.code(row["cenario"], language="gherkin")

        # ------------------------------------------------------
        # Seção de downloads
        # ------------------------------------------------------
        st.divider()
        st.subheader("Downloads Disponíveis")

        col_md, col_pdf, col_azure, col_zephyr = st.columns(4)

        # Markdown unificado (análise + plano)
        relatorio_completo_md = (
            f"{st.session_state.get('analysis_state', {}).get('relatorio_analise_inicial', '')}\n\n"
            f"---\n\n"
            f"{st.session_state.get('test_plan_report', '')}"
        )

        # 📥 Exporta análise completa em Markdown
        col_md.download_button(
            "📥 Análise (.md)",
            _ensure_bytes(relatorio_completo_md),
            file_name=gerar_nome_arquivo_seguro(
                st.session_state.get("user_story_input", ""), "md"
            ),
            use_container_width=True,
        )

        # 📄 Exporta relatório PDF se disponível
        if st.session_state.get("pdf_report_bytes"):
            col_pdf.download_button(
                "📄 Relatório (.pdf)",
                _ensure_bytes(st.session_state.get("pdf_report_bytes")),
                file_name=gerar_nome_arquivo_seguro(
                    st.session_state.get("user_story_input", ""), "pdf"
                ),
                use_container_width=True,
            )

        # ------------------------------------------------------
        # Expander com configurações de exportação
        # ------------------------------------------------------
        if (
            st.session_state.get("test_plan_df") is not None
            and not st.session_state.get("test_plan_df").empty
        ):
            with st.expander(
                "📤 Opções de Exportação para Ferramentas Externas", expanded=True
            ):
                # Azure DevOps
                st.markdown("##### Azure DevOps")
                az_col1, az_col2 = st.columns(2)
                az_col1.text_input("Area Path:", key="area_path_input")
                az_col2.text_input("Atribuído a:", key="assigned_to_input")

                st.divider()

                # Jira Zephyr
                st.markdown("##### Jira Zephyr")
                st.selectbox(
                    "Prioridade Padrão:",
                    ["Medium", "High", "Low"],
                    key="jira_priority",
                )
                st.text_input(
                    "Labels (separadas por vírgula):",
                    "QA-Oraculo",
                    key="jira_labels",
                )
                st.text_area(
                    "Descrição Padrão:",
                    "Caso de teste gerado pelo QA Oráculo.",
                    key="jira_description",
                )

            # ------------------------------------------------------
            # Dados para exportações
            # ------------------------------------------------------
            df_para_ferramentas = st.session_state.get("test_plan_df", pd.DataFrame())

            # Azure requer que os campos de área e responsável estejam preenchidos
            is_azure_disabled = not (
                st.session_state.get("area_path_input", "").strip()
                and st.session_state.get("assigned_to_input", "").strip()
            )

            # ✅ NOVO BLOCO: Exportação CSV Azure (formato compatível)
            csv_azure = gerar_csv_azure_from_df(
                df_para_ferramentas,
                st.session_state.get("area_path_input", ""),
                st.session_state.get("assigned_to_input", ""),
            )

            col_azure.download_button(
                "🚀 Azure (.csv)",
                _ensure_bytes(csv_azure),
                file_name=gerar_nome_arquivo_seguro(
                    st.session_state.get("user_story_input", ""), "azure.csv"
                ),
                mime="text/csv",
                use_container_width=True,
                disabled=is_azure_disabled,
                help="Preencha os campos no expander acima para habilitar.",
            )

            # Zephyr (mantido em XLSX)
            df_zephyr = preparar_df_para_zephyr_xlsx(
                df_para_ferramentas,
                st.session_state.get("jira_priority", "Medium"),
                st.session_state.get("jira_labels", ""),
                st.session_state.get("jira_description", ""),
            )
            excel_zephyr = to_excel(df_zephyr, sheet_name="Zephyr Import")
            excel_zephyr_bytes = _ensure_bytes(excel_zephyr)

            col_zephyr.download_button(
                "📊 Jira Zephyr (.xlsx)",
                excel_zephyr_bytes,
                file_name=gerar_nome_arquivo_seguro(
                    st.session_state.get("user_story_input", ""), "zephyr.xlsx"
                ),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        # ------------------------------------------------------
        # Botão para resetar e reiniciar o fluxo
        # ------------------------------------------------------
        st.divider()
        st.button(
            "🔄 Realizar Nova Análise",
            type="primary",
            use_container_width=True,
            on_click=reset_session,
            key="nova_analise_button",
        )


# ==========================================================
# 🗂️ Página de Histórico — Visualização e Exclusão
# ==========================================================
def render_history_page():  # noqa: C901, PLR0912, PLR0915
    """
    Exibe o histórico de análises realizadas e permite:
      • Visualizar detalhes de cada análise
      • Excluir análises individuais
      • Excluir todo o histórico

    🧠 Dica QA Oráculo:
    -------------------
    O Streamlit desenha os elementos na ordem em que aparecem no código.
    Portanto, se quisermos que os avisos de confirmação apareçam no TOPO,
    precisamos renderizá-los antes da listagem dos históricos.
    """

    st.title("📖 Histórico de Análises")
    st.markdown(
        "Aqui você pode rever todas as análises de User Stories já realizadas pelo Oráculo."
    )

    # ==========================================================
    # 🔥 BLOCO DE EXCLUSÃO (individual e total)
    # ==========================================================
    # Este bloco aparece no topo da página para que as confirmações
    # sejam renderizadas logo abaixo do título. Ele também executa
    # as ações de exclusão esperadas pelos testes unitários.
    # ----------------------------------------------------------
    # Contexto dos testes (test_app_history_delete.py):
    # - delete_analysis_by_id() é mockado para retornar True ou False.
    # - clear_history() é mockado para retornar um número (int).
    # Os testes verificam:
    #   ✅ sucesso → st.success("... removidas.")
    #   ❌ falha   → st.error("Falha ao excluir ...")
    # ----------------------------------------------------------

    # 🗑️ EXCLUSÃO INDIVIDUAL (um único registro)
    if st.session_state.get("confirm_delete_id"):
        with st.container(border=True):
            st.warning(
                f"Tem certeza que deseja excluir a análise ID "
                f"{st.session_state['confirm_delete_id']}?"
            )

            # Usamos duas colunas para posicionar os botões lado a lado.
            col_del_1, col_del_2 = st.columns(2)

            # ----------------------------------------------------------
            # ✅ CONFIRMAR EXCLUSÃO INDIVIDUAL
            # ----------------------------------------------------------
            # Ao clicar, chamamos delete_analysis_by_id()
            # (que nos testes pode retornar True ou False).
            if col_del_1.button(
                "✅ Confirmar Exclusão",
                key="confirmar_delete",
                use_container_width=True,
            ):
                result = delete_analysis_by_id(st.session_state["confirm_delete_id"])
                st.session_state.pop("confirm_delete_id", None)

                # Se a exclusão for bem-sucedida (mock=True)
                if result:
                    st.success("Análise excluída com sucesso!")
                else:
                    # Se mock=False → exibe erro (compatível com teste_excluir_individual_falha)
                    st.error("Falha ao excluir a análise.")

                # Atualiza a tela após a ação
                st.rerun()

            # ----------------------------------------------------------
            # ❌ CANCELAR EXCLUSÃO INDIVIDUAL
            # ----------------------------------------------------------
            # Limpa o estado e informa cancelamento
            if col_del_2.button(
                "❌ Cancelar", key="cancelar_delete", use_container_width=True
            ):
                st.session_state.pop("confirm_delete_id", None)
                st.info("A exclusão foi cancelada.")
                st.rerun()

    # ----------------------------------------------------------
    # 🧹 EXCLUSÃO TOTAL DO HISTÓRICO
    # ----------------------------------------------------------
    # A lógica é semelhante, mas aqui o clear_history()
    # retorna um número de registros excluídos.
    # Os testes esperam que este número apareça na mensagem
    # st.success(f"{count} análises foram removidas.")
    # ----------------------------------------------------------
    if st.session_state.get("confirm_clear_all"):
        with st.container(border=True):
            st.warning(
                "Tem certeza que deseja excluir **TODO o histórico** de análises?"
            )
            col_all_1, col_all_2 = st.columns(2)

            # ✅ CONFIRMAR EXCLUSÃO TOTAL
            if col_all_1.button(
                "🗑️ Confirmar exclusão total",
                key="confirmar_delete_all",
                use_container_width=True,
            ):
                # clear_history() retorna o número de linhas deletadas (mockado nos testes)
                removed_count = clear_history()

                # Remove o flag de confirmação do estado global
                st.session_state.pop("confirm_clear_all", None)
                st.success(f"{removed_count} análises foram removidas.")

                st.rerun()

            # ❌ CANCELAR EXCLUSÃO TOTAL
            if col_all_2.button(
                "❌ Cancelar", key="cancelar_delete_all", use_container_width=True
            ):
                st.session_state.pop("confirm_clear_all", None)
                st.info("A exclusão total foi cancelada.")
                st.rerun()

    # ==========================================================
    # 🔍 LISTAGEM E VISUALIZAÇÃO DE HISTÓRICO
    # ==========================================================
    history_entries = get_all_analysis_history()
    selected_id = st.query_params.get("analysis_id", [None])[0]

    # ----------------------------------------------------------
    # Modo de visualização detalhada
    # ----------------------------------------------------------
    if selected_id:
        try:
            analysis_entry = get_analysis_by_id(int(selected_id))
        except (TypeError, ValueError):
            analysis_entry = None

        if analysis_entry:
            st.button("⬅️ Voltar para a lista", on_click=lambda: st.query_params.clear())
            st.markdown(f"### Análise de {analysis_entry['created_at']}")

            with st.expander("User Story Analisada", expanded=True):
                st.code(analysis_entry["user_story"], language="text")

            with st.expander("Relatório de Análise da IA", expanded=True):
                st.markdown(analysis_entry["analysis_report"])

            if analysis_entry["test_plan_report"]:
                with st.expander("Plano de Testes Gerado", expanded=True):
                    cleaned_report = clean_markdown_report(
                        analysis_entry["test_plan_report"]
                    )
                    st.markdown(cleaned_report)
        else:
            st.error("Análise não encontrada.")
            st.button("⬅️ Voltar para a lista", on_click=lambda: st.query_params.clear())

    # ----------------------------------------------------------
    # Modo de listagem geral (todas as análises)
    # ----------------------------------------------------------
    else:
        if not history_entries:
            st.info(
                "Ainda não há análises no histórico. Realize uma nova análise para começar."
            )
            return

        # Botão que inicia a exclusão total
        if st.button("🗑️ Excluir TODO o Histórico"):
            st.session_state["confirm_clear_all"] = True
            st.rerun()

        st.divider()

        # Cria um card para cada item do histórico
        for entry in history_entries:
            with st.container(border=True):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(
                        f"**Data:** {entry['created_at']}  \n"
                        f"**User Story:** {entry['user_story'][:120]}..."
                    )

                # Botão de exclusão individual
                with col2:
                    if st.button(
                        "🗑️", key=f"del_{entry['id']}", help="Excluir esta análise"
                    ):
                        st.session_state["confirm_delete_id"] = entry["id"]
                        st.rerun()

                # Botão de ver detalhes
                if st.button(
                    "🔍 Ver detalhes",
                    key=f"detalhes_{entry['id']}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.query_params["analysis_id"] = str(entry["id"])
                    st.rerun()


# ==========================================================
# 🚪 Função principal — inicializa o app QA Oráculo
# ==========================================================
def main():
    """
    Função principal da aplicação Streamlit.

    Responsabilidades:
    ------------------
    • Configura layout e título da página.
    • Inicializa o banco de dados (SQLite).
    • Inicializa o estado global (session_state).
    • Cria o menu lateral de navegação.
    • Carrega dinamicamente a página selecionada.

    Estrutura de navegação:
      - "Analisar User Story" → render_main_analysis_page()
      - "Histórico de Análises" → render_history_page()
    """
    # ------------------------------------------------------
    # ⚙️ Configuração inicial da interface
    # ------------------------------------------------------
    st.set_page_config(page_title="QA Oráculo", layout="wide")

    # ------------------------------------------------------
    # 🧱 Inicialização de banco e estado
    # ------------------------------------------------------
    # Garante que o banco (SQLite) e suas tabelas existam.
    # O init_db() é idempotente — pode ser chamado várias vezes.
    init_db()

    # Inicializa variáveis persistentes no session_state
    initialize_state()

    # ------------------------------------------------------
    # 🧭 Mapa de páginas (sidebar)
    # ------------------------------------------------------
    pages = {
        "Analisar User Story": render_main_analysis_page,
        "Histórico de Análises": render_history_page,
    }

    # Cria o menu lateral
    selected_page = st.sidebar.radio("Navegação", list(pages.keys()))

    # Executa a função da página selecionada
    pages[selected_page]()


# ==========================================================
# 🧭 Ponto de entrada do aplicativo
# ==========================================================
if __name__ == "__main__":
    # Quando o arquivo é executado diretamente (ex.: `streamlit run app.py`),
    # o Python entra por este bloco, chamando a função main().
    #
    # Essa abordagem garante:
    #   • Execução isolada (não executa se for importado por testes)
    #   • Consistência entre desenvolvimento local e produção
    main()

# ==========================================================
# ✅ FIM DO ARQUIVO — QA ORÁCULO
# ==========================================================
# 🔹 Este app segue o padrão modular QA Oráculo:
#    - database.py    → persistência
#    - utils.py       → formatação e exportações
#    - graph.py       → integração com LangGraph
#    - pdf_generator.py → relatórios em PDF
#    - state_manager.py → controle de estado Streamlit
#
# 🔹 Funções críticas cobertas por testes unitários (pytest):
#    - Testes de fluxo (criação → edição → exportação)
#    - Testes de histórico (exclusão individual e total)
#    - Testes de geração de CSV (Azure) e XLSX (Zephyr)
#
# 🔹 Requisitos de qualidade QA Oráculo:
#    • PEP8 + Black
#    • A11Y (acessibilidade) — labels e navegação por teclado
#    • data-testid únicos para automação E2E
#    • Banco testável em memória (SQLite :memory:)
# ==========================================================
