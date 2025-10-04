# app.py

import io
import streamlit as st
import pandas as pd
from pdf_generator import generate_pdf_report
from graph import grafo_analise, grafo_plano_testes
from database import init_db, save_analysis_to_history, get_all_analysis_history, get_analysis_by_id, delete_analysis_by_id, clear_history
from utils import clean_markdown_report

from utils import (
    gerar_nome_arquivo_seguro,
    preparar_df_para_azure_xlsx,
    preparar_df_para_zephyr_xlsx,
    to_excel,
    get_flexible,
    clean_markdown_report
)
from state_manager import initialize_state, reset_session


def _ensure_bytes(data):
    """
    Garante bytes para o download_button:
    - str -> UTF-8
    - objeto com .getvalue() -> getvalue()
    - bytes/bytearray -> ok
    """
    if isinstance(data, str):
        return data.encode("utf-8")
    if hasattr(data, "getvalue"):
        try:
            return data.getvalue()
        except Exception:
            pass
    if isinstance(data, (bytes, bytearray)):
        return data
    # fallback conservador
    return bytes(str(data), "utf-8")


@st.cache_data(show_spinner=False)
def run_analysis_graph(user_story: str):
    return grafo_analise.invoke({"user_story": user_story})


@st.cache_data(show_spinner=False)
def run_test_plan_graph(analysis_state: dict):
    return grafo_plano_testes.invoke(analysis_state)


# --- FUNÇÕES PARA AS PÁGINAS ---
def render_main_analysis_page():
    st.title("🤖 QA Oráculo")
    st.markdown("Seja bem-vindo! Como seu Assistente de QA Sênior, estou aqui para apoiar na revisão de User Stories. Cole uma abaixo e vamos começar.")

    # O fluxo interativo só acontece se a análise NÃO estiver finalizada.
    if not st.session_state.get("analysis_finished", False):

        # Bloco para inserir a User Story (só aparece se não houver análise em andamento)
        if not st.session_state.get("analysis_state"):
            st.text_area("Insira a User Story aqui:", height=250, key="user_story_input")
            if st.button("Analisar User Story", type="primary"):
                user_story_txt = st.session_state.get("user_story_input", "")
                if user_story_txt.strip():
                    with st.spinner("🔮 O Oráculo está realizando a análise inicial..."):
                        resultado_analise = run_analysis_graph(user_story_txt)
                        st.session_state["analysis_state"] = resultado_analise
                        st.session_state["show_generate_plan_button"] = False
                        st.rerun()
                else:
                    st.warning("Por favor, insira uma User Story antes de analisar.")

        # Bloco interativo principal (edição e decisão)
        if st.session_state.get("analysis_state"):
            st.divider()

            # Mostra o formulário de edição
            if not st.session_state.get("show_generate_plan_button"):
                st.info("🔮 O Oráculo gerou a análise abaixo. Revise, edite se necessário e clique em 'Salvar' para prosseguir.")
                analise_json = st.session_state.get("analysis_state", {}).get("analise_da_us", {})

                avaliacao_str = get_flexible(analise_json, ["avaliacao_geral", "avaliacao"], "")
                pontos_list = get_flexible(analise_json, ["pontos_ambiguos", "pontos_de_ambiguidade"], [])
                perguntas_list = get_flexible(analise_json, ["perguntas_para_po", "perguntas_ao_po"], [])
                criterios_list = get_flexible(analise_json, ["sugestao_criterios_aceite", "criterios_de_aceite"], [])
                riscos_list = get_flexible(analise_json, ["riscos_e_dependencias", "riscos"], [])

                pontos_str = "\n".join(pontos_list)
                perguntas_str = "\n".join(perguntas_list)
                criterios_str = "\n".join(criterios_list)
                riscos_str = "\n".join(riscos_list)

                with st.form(key="analysis_edit_form"):
                    st.subheader("📝 Análise Editável")
                    st.text_area("Avaliação Geral", value=avaliacao_str, key="edit_avaliacao", height=75)
                    st.text_area("Pontos Ambíguos", value=pontos_str, key="edit_pontos", height=125)
                    st.text_area("Perguntas para PO", value=perguntas_str, key="edit_perguntas", height=125)
                    st.text_area("Critérios de Aceite", value=criterios_str, key="edit_criterios", height=150)
                    st.text_area("Riscos e Dependências", value=riscos_str, key="edit_riscos", height=100)
                    submitted = st.form_submit_button("Salvar Análise e Continuar")

                if submitted:
                    # Garante estrutura antes de escrever
                    st.session_state.setdefault("analysis_state", {})
                    st.session_state["analysis_state"].setdefault("analise_da_us", {})
                    bloco = st.session_state["analysis_state"]["analise_da_us"]

                    bloco["avaliacao_geral"] = st.session_state.get("edit_avaliacao", "")
                    bloco["pontos_ambiguos"] = [l.strip() for l in st.session_state.get("edit_pontos", "").split('\n') if l.strip()]
                    bloco["perguntas_para_po"] = [l.strip() for l in st.session_state.get("edit_perguntas", "").split('\n') if l.strip()]
                    bloco["sugestao_criterios_aceite"] = [l.strip() for l in st.session_state.get("edit_criterios", "").split('\n') if l.strip()]
                    bloco["riscos_e_dependencias"] = [l.strip() for l in st.session_state.get("edit_riscos", "").split('\n') if l.strip()]

                    st.session_state["show_generate_plan_button"] = True
                    st.success("Análise refinada salva com sucesso!")
                    st.rerun()

            # Mostra os botões de decisão (Sim/Não)
            if st.session_state.get("show_generate_plan_button"):
                with st.expander("1. Análise Refinada da User Story", expanded=True):
                    st.markdown(st.session_state.get("analysis_state", {}).get("relatorio_analise_inicial", ""))

                st.info("Deseja que o Oráculo gere um Plano de Testes com base na análise refinada?")
                col1, col2, _ = st.columns([1, 1, 2])

                if col1.button("Sim, Gerar Plano de Testes", type="primary", use_container_width=True):
                    with st.spinner("🔮 Elaborando o Plano de Testes com base na análise refinada..."):
                        resultado_plano = run_test_plan_graph(st.session_state.get("analysis_state", {}))
                        casos_de_teste = resultado_plano.get("plano_e_casos_de_teste", {}).get("casos_de_teste_gherkin", [])

                        if not casos_de_teste or not isinstance(casos_de_teste, list):
                            st.error("O Oráculo não conseguiu gerar um plano de testes estruturado.")
                            st.session_state["test_plan_report"] = resultado_plano.get("relatorio_plano_de_testes", "Falha na geração do plano.")
                        else:
                            st.session_state["test_plan_report"] = resultado_plano.get("relatorio_plano_de_testes")
                            df = pd.DataFrame(casos_de_teste)
                            df_clean = df.apply(lambda col: col.apply(lambda x: '\n'.join(map(str, x)) if isinstance(x, list) else x))
                            df_clean.fillna("", inplace=True)
                            st.session_state["test_plan_df"] = df_clean
                            pdf_bytes = generate_pdf_report(
                                st.session_state.get("analysis_state", {}).get("relatorio_analise_inicial", ""),
                                df_clean
                            )
                            st.session_state["pdf_report_bytes"] = pdf_bytes

                        st.session_state["analysis_finished"] = True

                        user_story_to_save = st.session_state.get("user_story_input", "")
                        analysis_report_to_save = st.session_state.get("analysis_state", {}).get("relatorio_analise_inicial", "")
                        test_plan_report_to_save = st.session_state.get("test_plan_report", "")
                        save_analysis_to_history(user_story_to_save, analysis_report_to_save, test_plan_report_to_save)

                        st.rerun()

                if col2.button("Não, Encerrar", use_container_width=True):
                    st.session_state["analysis_finished"] = True

                    user_story_to_save = st.session_state.get("user_story_input", "")
                    analysis_report_to_save = st.session_state.get("analysis_state", {}).get("relatorio_analise_inicial", "")
                    test_plan_report_to_save = st.session_state.get("test_plan_report", "") if st.session_state.get("test_plan_report") else ""
                    save_analysis_to_history(user_story_to_save, analysis_report_to_save, test_plan_report_to_save)

                    st.rerun()

    # Este bloco inteiro só aparece quando a análise ESTÁ finalizada.
    if st.session_state.get("analysis_finished"):
        st.success("Análise concluída com sucesso!")

        # Mostra o relatório de análise final
        if st.session_state.get("analysis_state"):
            with st.expander("1. Análise Refinada da User Story", expanded=True):
                st.markdown(st.session_state.get("analysis_state", {}).get("relatorio_analise_inicial", ""))

        # Mostra o plano de testes se ele existir
        if st.session_state.get("test_plan_report"):
            with st.expander("2. Plano de Testes Detalhado", expanded=True):
                cleaned_report = clean_markdown_report(st.session_state.get("test_plan_report", ""))
                st.markdown(cleaned_report)
                if st.session_state.get("test_plan_df") is not None and not st.session_state.get("test_plan_df").empty:
                    st.dataframe(st.session_state.get("test_plan_df"), use_container_width=True)

        st.divider()
        st.subheader("Downloads Disponíveis")

        col_md, col_pdf, col_azure, col_zephyr = st.columns(4)
        relatorio_completo_md = f"{st.session_state.get('analysis_state', {}).get('relatorio_analise_inicial', '')}\n\n---\n\n{st.session_state.get('test_plan_report', '')}"
        col_md.download_button(
            "📥 Análise (.md)",
            _ensure_bytes(relatorio_completo_md),
            file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "md"),
            use_container_width=True,
        )

        if st.session_state.get("pdf_report_bytes"):
            col_pdf.download_button(
                "📄 Relatório (.pdf)",
                _ensure_bytes(st.session_state.get("pdf_report_bytes")),
                file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "pdf"),
                use_container_width=True,
            )

        if st.session_state.get("test_plan_df") is not None and not st.session_state.get("test_plan_df").empty:
            with st.expander("Opções de Exportação para Ferramentas Externas", expanded=True):
                st.markdown("##### Azure DevOps")
                az_col1, az_col2 = st.columns(2)
                az_col1.text_input("Area Path:", key="area_path_input")
                az_col2.text_input("Atribuído a:", key="assigned_to_input")

                st.divider()
                st.markdown("##### Jira Zephyr")
                st.selectbox("Prioridade Padrão:", ["Medium", "High", "Low"], key="jira_priority")
                st.text_input("Labels (separadas por vírgula):", "QA-Oraculo", key="jira_labels")
                st.text_area("Descrição Padrão:", "Caso de teste gerado pelo QA Oráculo.", key="jira_description")

            df_para_ferramentas = st.session_state.get("test_plan_df", pd.DataFrame())

            is_azure_disabled = not (
                st.session_state.get("area_path_input", "").strip()
                and st.session_state.get("assigned_to_input", "").strip()
            )

            df_azure = preparar_df_para_azure_xlsx(
                df_para_ferramentas,
                st.session_state.get("area_path_input", ""),
                st.session_state.get("assigned_to_input", ""),
            )
            excel_azure = to_excel(df_azure, sheet_name="Test Cases")
            excel_azure_bytes = _ensure_bytes(excel_azure)

            col_azure.download_button(
                "🚀 Azure (.xlsx)",
                excel_azure_bytes,
                file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "azure.xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                disabled=is_azure_disabled,
                help="Preencha os campos no expander acima para habilitar.",
            )

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
                file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "zephyr.xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        st.divider()
        st.button(
            "🔄 Realizar Nova Análise",
            type="primary",
            use_container_width=True,
            on_click=reset_session,
            key="nova_analise_button",
        )

def render_history_page():
    st.title("📖 Histórico de Análises")
    st.markdown("Aqui você pode rever todas as análises de User Stories já realizadas pelo Oráculo.")

    history_entries = get_all_analysis_history()

    if not history_entries:
        st.info("Ainda não há análises no histórico. Realize uma nova análise para começar.")
        return

    # --- Confirmação de exclusão individual (topo da página) ---
    if st.session_state.get("confirm_delete_id"):
        delete_id = st.session_state["confirm_delete_id"]
        st.warning(f"⚠️ Tem certeza que deseja excluir a análise {delete_id}? Esta ação não pode ser desfeita.")
        col1, col2 = st.columns(2)
        if col1.button("✅ Confirmar", key="confirmar_delete"):
            if delete_analysis_by_id(delete_id):
                st.success("Análise excluída com sucesso!")
            else:
                st.error("Falha ao excluir análise.")
            st.session_state.pop("confirm_delete_id", None)
            st.rerun()
        if col2.button("❌ Cancelar", key="cancelar_delete"):
            st.session_state.pop("confirm_delete_id", None)
            st.rerun()

    # --- Confirmação de exclusão total (topo da página) ---
    if st.session_state.get("confirm_clear_all"):
        st.warning("⚠️ Tem certeza que deseja excluir **todo o histórico de análises**? Esta ação não pode ser desfeita.")
        col1, col2 = st.columns(2)
        if col1.button("✅ Confirmar", key="confirmar_delete_all"):
            apagados = clear_history()
            st.success(f"{apagados} análises foram removidas.")
            st.session_state.pop("confirm_clear_all", None)
            st.rerun()
        if col2.button("❌ Cancelar", key="cancelar_delete_all"):
            st.session_state.pop("confirm_clear_all", None)
            st.rerun()

    # --- Botão para excluir tudo ---
    if st.button("🗑️ Excluir TODO o Histórico", key="btn-deletar-tudo"):
        st.session_state["confirm_clear_all"] = True
        st.rerun()
    st.markdown('<div data-testid="btn-deletar-tudo"></div>', unsafe_allow_html=True)

    selected_id = st.query_params.get("analysis_id", [None])[0]

    if selected_id:
        analysis_entry = get_analysis_by_id(int(selected_id))
        if analysis_entry:
            st.button("⬅️ Voltar para a lista", on_click=lambda: st.query_params.clear())
            st.markdown(f"### Análise de {analysis_entry['created_at']}")

            with st.expander("User Story Analisada", expanded=True):
                st.code(analysis_entry['user_story'], language='text')

            with st.expander("Relatório de Análise da IA", expanded=True):
                st.markdown(analysis_entry['analysis_report'])

            if analysis_entry['test_plan_report']:
                with st.expander("Plano de Testes Gerado", expanded=True):
                    cleaned_report = clean_markdown_report(analysis_entry['test_plan_report'])
                    st.markdown(cleaned_report)
        else:
            st.error("Análise não encontrada.")
            st.button("⬅️ Voltar para a lista", on_click=lambda: st.query_params.clear())
    else:
        for entry in history_entries:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**Análise de:** `{entry['created_at']}`")
                    st.caption(f"Início da US: *{entry['user_story'][:100]}...*")
                with col2:
                    if st.button("Ver Detalhes", key=f"btn-ver-detalhes-{entry['id']}", use_container_width=True):
                        st.query_params["analysis_id"] = str(entry['id'])
                        st.rerun()

                    if st.button("🗑️ Excluir", key=f"btn-deletar-{entry['id']}", use_container_width=True):
                        st.session_state["confirm_delete_id"] = entry['id']
                        st.rerun()
                    st.markdown(f'<div data-testid="btn-deletar-{entry["id"]}"></div>', unsafe_allow_html=True)


# --- LÓGICA PRINCIPAL DA APLICAÇÃO ---
def main():
    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Escolha uma página:", ["Análise Principal", "Histórico de Análises"])

    if page == "Análise Principal":
        render_main_analysis_page()
    elif page == "Histórico de Análises":
        render_history_page()


if __name__ == "__main__":
    st.set_page_config(
        page_title="QA Oráculo | Análise e Geração de Testes com IA",
        page_icon="🤖",
        layout="wide"
    )
    init_db()
    initialize_state()
    main()
