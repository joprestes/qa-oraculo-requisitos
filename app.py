# app.py (Versão final, completa e corrigida)

import streamlit as st
import datetime
import re
import pandas as pd
import io
from pdf_generator import generate_pdf_report
from graph import grafo_analise, grafo_plano_testes

# --- Configuração da Página ---
st.set_page_config(
    page_title="QA Oráculo | Análise de User Story e Geração de Testes com IA",
    page_icon="🤖",
    layout="wide"
)

# --- Gerenciamento de Estado da Sessão ---
def reset_session():
    """Limpa todas as variáveis da sessão para iniciar uma nova análise."""
    # Lista de chaves a serem resetadas
    keys_to_reset = [
        "analysis_state", "test_plan_report", "test_plan_df", "pdf_report_bytes",
        "show_generate_plan_button", "analysis_finished", "user_story_input",
        "area_path_input", "assigned_to_input", "jira_priority", 
        "jira_labels", "jira_description"
    ]
    # Itera e deleta cada chave do estado da sessão
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    # st.rerun() é chamado automaticamente pelo on_click

# Inicialização do estado (segura, usando .get() no resto do código)
# Nenhuma inicialização explícita é necessária, mas mantê-la não prejudica.

# --- Funções Auxiliares ---
def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str: 
    if not user_story: return f"relatorio_qa_oraculo.{extension}"
    primeira_linha_us = user_story.split('\n')[0].lower()
    nome_base = re.sub(r'[^\w\s-]', '', primeira_linha_us).strip()
    nome_base = re.sub(r'[-\s]+', '-', nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.{extension}"

def preparar_df_para_azure_xlsx(df_original: pd.DataFrame, area_path: str, assigned_to: str) -> pd.DataFrame:
    """Prepara o DataFrame para o formato de importação do Azure DevOps."""
    azure_rows = []
    header = ["Work Item Type", "Title", "Test Step", "Step Action", "Step Expected", "Priority", "Area Path", "Assigned To", "State"]
    priority_map = {"alta": "1", "média": "2", "baixa": "3"}

    for index, row in df_original.iterrows():
        title = row.get("titulo", f"Caso de Teste {index+1}")
        priority = priority_map.get(str(row.get("prioridade", "2")).lower(), "2")
        
        azure_rows.append({
            "Work Item Type": "Test Case", "Title": title, "Test Step": 1, "Step Action": "", "Step Expected": "",
            "Priority": priority, "Area Path": area_path, "Assigned To": assigned_to, "State": "Design"
        })

        cenario_steps = row.get("cenario", [])
        if isinstance(cenario_steps, str):
            cenario_steps = [step for step in cenario_steps.split('\n') if step.strip()]

        step_counter = 2
        for step in cenario_steps:
            azure_rows.append({"Test Step": step_counter, "Step Action": step, "Step Expected": ""})
            step_counter += 1

    return pd.DataFrame(azure_rows, columns=header)

def preparar_df_para_zephyr_xlsx(df_original: pd.DataFrame, priority: str, labels: str, description: str) -> pd.DataFrame:
    """Transforma o DataFrame no formato de importação do Jira Zephyr."""
    zephyr_rows = []
    header = ["Issue Type", "Summary", "Priority", "Labels", "Description", "Test Step", "Expected Result"]
    
    for index, row in df_original.iterrows():
        summary = row.get("titulo", f"Caso de Teste {index+1}")
        cenario_steps = row.get("cenario", [])
        if isinstance(cenario_steps, str):
            cenario_steps = [step for step in cenario_steps.split('\n') if step.strip()]

        if not cenario_steps: continue

        zephyr_rows.append({
            "Issue Type": "Test", "Summary": summary, "Priority": priority, "Labels": labels,
            "Description": description, "Test Step": cenario_steps[0], "Expected Result": ""
        })

        for i in range(1, len(cenario_steps)):
            zephyr_rows.append({"Test Step": cenario_steps[i]})

    return pd.DataFrame(zephyr_rows, columns=header)

# --- Interface do Usuário (UI) ---
st.title("🤖 QA Oráculo")
st.markdown("Seja bem-vindo! Como seu Assistente de QA Sênior, estou aqui para apoiar na revisão de User Stories. Cole uma abaixo e vamos começar.")

if not st.session_state.get("analysis_finished", False):
    st.text_area("Insira a User Story aqui:", height=250, key="user_story_input")
    if st.button("Analisar User Story", type="primary"):
        if st.session_state.get("user_story_input", "").strip():
            with st.spinner("🔮 O Oráculo está realizando a análise inicial..."):
                resultado_analise = grafo_analise.invoke({"user_story": st.session_state.user_story_input})
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
                resultado_plano = grafo_plano_testes.invoke(st.session_state.analysis_state)
                
                casos_de_teste = resultado_plano.get("plano_e_casos_de_teste", {}).get("casos_de_teste_gherkin", [])
                
                if not casos_de_teste or not isinstance(casos_de_teste, list):
                    st.error("O Oráculo não conseguiu gerar um plano de testes estruturado. A resposta da IA pode ter sido inválida. Por favor, tente novamente ou refine a User Story.")
                    st.session_state.test_plan_report = resultado_plano.get("relatorio_plano_de_testes", "Falha na geração do plano de testes.")
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

# --- Exibição do Plano de Testes (se gerado) ---
if st.session_state.get("test_plan_report"):
    st.divider()
    with st.expander("2. Plano de Testes Detalhado", expanded=True):
        st.markdown(st.session_state.test_plan_report)
        if st.session_state.get("test_plan_df") is not None and not st.session_state.get("test_plan_df").empty:
            st.dataframe(st.session_state.test_plan_df, use_container_width=True)

# --- Bloco de Ações Finais ---
if st.session_state.get("analysis_finished"):
    st.divider()
    st.success("Análise concluída com sucesso!")
    st.subheader("Downloads Disponíveis")

    col_md, col_pdf, col_azure, col_zephyr = st.columns(4)

    relatorio_completo_md = f"{st.session_state.get('analysis_state', {}).get('relatorio_analise_inicial', '')}\n\n---\n\n{st.session_state.get('test_plan_report', '')}"
    col_md.download_button(
        "📥 Análise (.md)", relatorio_completo_md.encode("utf-8"),
        file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "md"), use_container_width=True
    )
    
    if st.session_state.get("pdf_report_bytes"):
        col_pdf.download_button(
            "📄 Relatório (.pdf)", st.session_state.pdf_report_bytes,
            file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "pdf"), use_container_width=True
        )

    if st.session_state.get("test_plan_df") is not None and not st.session_state.get("test_plan_df").empty:
        with st.expander("Opções de Exportação para Ferramentas Externas", expanded=True):
            st.markdown("##### Azure DevOps")
            az_col1, az_col2 = st.columns(2)
            az_col1.text_input("Area Path:", key="area_path_input")
            az_col2.text_input("Atribuído a:", key="assigned_to_input")
            
            st.divider()
            st.markdown("##### Jira Zephyr")
            zephyr_priority = st.selectbox("Prioridade Padrão:", ["Medium", "High", "Low"], key="jira_priority")
            zephyr_labels = st.text_input("Labels (separadas por vírgula):", "QA-Oraculo", key="jira_labels")
            zephyr_desc = st.text_area("Descrição Padrão:", "Caso de teste gerado pelo QA Oráculo.", key="jira_description")

        # Lógica para os botões de Azure e Zephyr
        df_para_ferramentas = st.session_state.get("test_plan_df", pd.DataFrame())

        is_azure_disabled = not (st.session_state.get("area_path_input", "").strip() and st.session_state.get("assigned_to_input", "").strip())
        df_azure = preparar_df_para_azure_xlsx(df_para_ferramentas, st.session_state.get("area_path_input", ""), st.session_state.get("assigned_to_input", ""))
        output_azure = io.BytesIO()
        with pd.ExcelWriter(output_azure, engine='openpyxl') as writer:
            df_azure.to_excel(writer, index=False, sheet_name='Test Cases')
        excel_azure = output_azure.getvalue()
        
        col_azure.download_button(
            "🚀 Azure (.xlsx)", excel_azure,
            file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "azure.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, disabled=is_azure_disabled, help="Preencha os campos no expander acima para habilitar."
        )

        df_zephyr = preparar_df_para_zephyr_xlsx(df_para_ferramentas, st.session_state.get("jira_priority", "Medium"), st.session_state.get("jira_labels", ""), st.session_state.get("jira_description", ""))
        output_zephyr = io.BytesIO()
        with pd.ExcelWriter(output_zephyr, engine='openpyxl') as writer:
            df_zephyr.to_excel(writer, index=False, sheet_name='Zephyr Import')
        excel_zephyr = output_zephyr.getvalue()
        
        col_zephyr.download_button(
            "📊 Jira Zephyr (.xlsx)", excel_zephyr,
            file_name=gerar_nome_arquivo_seguro(st.session_state.get("user_story_input", ""), "zephyr.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()
    st.button(
        "🔄 Realizar Nova Análise", 
        type="primary", 
        use_container_width=True,
        on_click=reset_session,
        key="nova_analise_button"
    )