import streamlit as st
import pandas as pd
from pdf_generator import generate_pdf_report
from graph import grafo_analise, grafo_plano_testes

# Importando  módulos 
from utils import (
    gerar_nome_arquivo_seguro,
    preparar_df_para_azure_xlsx,
    preparar_df_para_zephyr_xlsx,
    to_excel
)
from state_manager import initialize_state, reset_session

# --- Configuração da Página e Estado Inicial ---
st.set_page_config(
    page_title="QA Oráculo | Análise e Geração de Testes com IA",
    page_icon="🤖",
    layout="wide"
)
initialize_state()



@st.cache_data
def run_analysis_graph(user_story: str):
    """Executa o grafo de análise e cacheia o resultado."""
    print(f"--- 🧠 EXECUTANDO ANÁLISE VIA API (Cache Miss para US: '{user_story[:20]}...') ---")
    return grafo_analise.invoke({"user_story": user_story})

@st.cache_data
def run_test_plan_graph(analysis_state: dict):
    """Executa o grafo de plano de testes e cacheia o resultado."""

    print(f"--- 🧠 EXECUTANDO PLANO DE TESTES VIA API (Cache Miss) ---")
    return grafo_plano_testes.invoke(analysis_state)

# --- Interface Principal (UI) ---
st.title("🤖 QA Oráculo")
st.markdown("Seja bem-vindo! Como seu Assistente de QA Sênior, estou aqui para apoiar na revisão de User Stories. Cole uma abaixo e vamos começar.")

if not st.session_state.get("analysis_finished", False):
    st.text_area("Insira a User Story aqui:", height=250, key="user_story_input")
    if st.button("Analisar User Story", type="primary"):
        if st.session_state.get("user_story_input", "").strip():
            with st.spinner("🔮 O Oráculo está realizando a análise inicial..."):
           
                resultado_analise = run_analysis_graph(st.session_state.user_story_input)
                st.session_state.analysis_state = resultado_analise
                st.session_state.show_generate_plan_button = True
                st.rerun()
        else:
            st.warning("Por favor, insira uma User Story antes de analisar.")

# --- Exibição dos Resultados e Fluxo Interativo ---
if st.session_state.get("analysis_state"):
    st.divider()
    with st.expander("1. Análise Inicial da User Story", expanded=True):
        st.markdown(st.session_state.analysis_state.get("relatorio_analise_inicial", ""))

    if st.session_state.get("show_generate_plan_button"):
        st.info("A análise inicial está pronta. Deseja gerar um Plano de Testes detalhado?")
        col1, col2, _ = st.columns([1, 1, 2])
        if col1.button("Sim, Gerar Plano", type="primary", use_container_width=True):
            with st.spinner("🔮 Elaborando o Plano de Testes..."):
                # ATUALIZADO: Chamando a função com cache
                resultado_plano = run_test_plan_graph(st.session_state.analysis_state)
                casos_de_teste = resultado_plano.get("plano_e_casos_de_teste", {}).get("casos_de_teste_gherkin", [])
                
                if not casos_de_teste or not isinstance(casos_de_teste, list):
                    st.error("O Oráculo não conseguiu gerar um plano de testes estruturado...")
                    st.session_state.test_plan_report = resultado_plano.get("relatorio_plano_de_testes", "Falha na geração.")
                else:
                    st.session_state.test_plan_report = resultado_plano.get("relatorio_plano_de_testes")
                    df = pd.DataFrame(casos_de_teste)
                    df_clean = df.apply(lambda col: col.apply(lambda x: '\n'.join(map(str, x)) if isinstance(x, list) else x))
                    df_clean.fillna("", inplace=True)
                    st.session_state.test_plan_df = df_clean
                    pdf_bytes = generate_pdf_report(st.session_state.analysis_state.get("relatorio_analise_inicial", ""), df_clean)
                    st.session_state.pdf_report_bytes = pdf_bytes
                
                st.session_state.show_generate_plan_button = False
                st.session_state.analysis_finished = True
                st.rerun()

        if col2.button("Não, Encerrar", use_container_width=True):
            st.session_state.show_generate_plan_button = False
            st.session_state.analysis_finished = True
            st.rerun()


if st.session_state.get("test_plan_report"):
    st.divider()
    with st.expander("2. Plano de Testes Detalhado", expanded=True):
        st.markdown(st.session_state.test_plan_report)
        if st.session_state.get("test_plan_df") is not None and not st.session_state.get("test_plan_df").empty:
            st.dataframe(st.session_state.get("test_plan_df"), use_container_width=True)

if st.session_state.get("analysis_finished"):
    st.divider()
    st.success("Análise concluída com sucesso!")
    st.subheader("Downloads Disponíveis")

    col_md, col_pdf, col_azure, col_zephyr = st.columns(4)
    relatorio_completo_md = f"{st.session_state.get('analysis_state', {}).get('relatorio_analise_inicial', '')}\n\n---\n\n{st.session_state.get('test_plan_report', '')}"
    col_md.download_button("📥 Análise (.md)", relatorio_completo_md.encode("utf-8"), file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "md"), use_container_width=True)
    if st.session_state.get("pdf_report_bytes"):
        col_pdf.download_button("📄 Relatório (.pdf)", st.session_state.pdf_report_bytes, file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "pdf"), use_container_width=True)

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
        is_azure_disabled = not (st.session_state.get("area_path_input", "").strip() and st.session_state.get("assigned_to_input", "").strip())
        df_azure = preparar_df_para_azure_xlsx(df_para_ferramentas, st.session_state.get("area_path_input", ""), st.session_state.get("assigned_to_input", ""))
        excel_azure = to_excel(df_azure, sheet_name='Test Cases')
        col_azure.download_button("🚀 Azure (.xlsx)", excel_azure, file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "azure.xlsx"), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, disabled=is_azure_disabled, help="Preencha os campos no expander acima para habilitar.")
        
        df_zephyr = preparar_df_para_zephyr_xlsx(df_para_ferramentas, st.session_state.get("jira_priority", "Medium"), st.session_state.get("jira_labels", ""), st.session_state.get("jira_description", ""))
        excel_zephyr = to_excel(df_zephyr, sheet_name='Zephyr Import')
        col_zephyr.download_button("📊 Jira Zephyr (.xlsx)", excel_zephyr, file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "zephyr.xlsx"), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    st.divider()
    st.button("🔄 Realizar Nova Análise", type="primary", use_container_width=True, on_click=reset_session, key="nova_analise_button")