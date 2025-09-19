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
    st.session_state.analysis_state = None
    st.session_state.test_plan_report = None
    st.session_state.test_plan_df = None
    st.session_state.pdf_report_bytes = None
    st.session_state.show_generate_plan_button = False
    st.session_state.analysis_finished = False
    st.session_state.user_story_input = ""
    st.session_state.area_path_input = ""
    st.session_state.assigned_to_input = ""

# Inicialização do estado
if "analysis_state" not in st.session_state:
    st.session_state.analysis_state = None
if "test_plan_report" not in st.session_state:
    st.session_state.test_plan_report = None
if "test_plan_df" not in st.session_state:
    st.session_state.test_plan_df = None
if "pdf_report_bytes" not in st.session_state:
    st.session_state.pdf_report_bytes = None
if "show_generate_plan_button" not in st.session_state:
    st.session_state.show_generate_plan_button = False
if "user_story_input" not in st.session_state:
    st.session_state.user_story_input = ""
if "analysis_finished" not in st.session_state:
    st.session_state.analysis_finished = False
if "area_path_input" not in st.session_state:
    st.session_state.area_path_input = ""
if "assigned_to_input" not in st.session_state:
    st.session_state.assigned_to_input = ""

# --- Funções Auxiliares ---
def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str: 
    if not user_story: return f"relatorio_qa_oraculo.{extension}"
    primeira_linha_us = user_story.split('\n')[0].lower()
    nome_base = re.sub(r'[^\w\s-]', '', primeira_linha_us).strip()
    nome_base = re.sub(r'[-\s]+', '-', nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.{extension}"

def preparar_df_para_azure_xlsx(df_original: pd.DataFrame, area_path_usuario: str, assigned_to_usuario: str) -> pd.DataFrame:
    azure_rows = []
    header = [
        "Work Item Type", "Title", "Test Step", "Step Action", "Step Expected",
        "Priority", "Area Path", "Assigned To", "State"
    ]
    
    priority_map = {"alta": "1", "média": "2", "baixa": "3"}

    for index, row in df_original.iterrows():
        title = row.get("titulo", f"Caso de Teste {index+1}")
        priority = priority_map.get(str(row.get("prioridade", "2")).lower(), "2")
        
        opener_row = {
            "Work Item Type": "Test Case",
            "Title": title,
            "Test Step": 1,
            "Step Action": "",
            "Step Expected": "",
            "Priority": priority,
            "Area Path": area_path_usuario,
            "Assigned To": assigned_to_usuario,
            "State": "Design"
        }
        azure_rows.append(opener_row)

        cenario_steps = row.get("cenario", [])
        if not isinstance(cenario_steps, list):
            cenario_steps = str(cenario_steps).split('\n')

        step_counter = 2
        
        context = "init"
        for i, step in enumerate(cenario_steps):
            step = step.strip()
            if not step: continue

            action, expected = "", ""
            step_lower = step.lower()

            if step_lower.startswith("dado"):
                action = step
                context = "dado"
            elif step_lower.startswith("quando"):
                action = step
                try:
                    if cenario_steps[i+1].strip().lower().startswith("então"):
                        expected = cenario_steps[i+1].strip()
                except IndexError:
                    pass
                context = "quando"
            elif step_lower.startswith("então"):
                if i > 0 and cenario_steps[i-1].strip().lower().startswith("quando"):
                    continue
                expected = step
                context = "entao"
            elif step_lower.startswith("e"):
                if context == "quando":
                    action = step
                else:
                    expected = step
            else:
                action = step

            step_row = {
                "Test Step": step_counter,
                "Step Action": action,
                "Step Expected": expected,
            }
            azure_rows.append(step_row)
            step_counter += 1

    df_azure = pd.DataFrame(azure_rows, columns=header)
    return df_azure

# --- Interface do Usuário (UI) ---
st.title("🤖 QA Oráculo")
st.markdown("Seja bem-vindo! Como seu Assistente de QA Sênior, estou aqui para apoiar na revisão de User Stories. Cole uma abaixo e vamos começar.")

if not st.session_state.analysis_finished:
    user_story = st.text_area(
        "Insira a User Story aqui:",
        height=250,
        placeholder="Ex: Como um cliente registrado, eu quero poder visualizar meu histórico de pedidos...",
        key="user_story_input",
        help="Você pode colar uma User Story com múltiplas linhas."
    )

    if st.button("Analisar User Story", type="primary"):
        if st.session_state.user_story_input and st.session_state.user_story_input.strip():
            st.session_state.analysis_state = None
            st.session_state.test_plan_report = None
            st.session_state.test_plan_df = None
            st.session_state.pdf_report_bytes = None
            st.session_state.show_generate_plan_button = False
            with st.spinner("🔮 O Oráculo está realizando a análise inicial..."):
                try:
                    resultado_analise = grafo_analise.invoke({"user_story": st.session_state.user_story_input})
                    st.session_state.analysis_state = resultado_analise
                    st.session_state.show_generate_plan_button = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Ocorreu um erro crítico durante a análise: {e}")
        else:
            st.warning("Por favor, insira uma User Story antes de analisar.")

# --- Exibição dos Resultados e Fluxo Interativo ---
if st.session_state.analysis_state:
    st.divider()
    with st.expander("1. Análise Inicial da User Story", expanded=True):
        analysis_report = st.session_state.analysis_state.get("relatorio_analise_inicial", "")
        st.markdown(analysis_report)
        analysis_json = st.session_state.analysis_state.get("analise_da_us")
        if analysis_json:
            with st.expander("Ver detalhes da Análise em JSON"):
                st.json(analysis_json)

    if st.session_state.show_generate_plan_button:
        st.info("A análise inicial está pronta. Deseja que o Oráculo continue e gere um Plano de Testes detalhado?")
        
        col1, col2, _ = st.columns([1, 1, 2])
        with col1:
            if st.button("Sim, Gerar Plano", type="primary", use_container_width=True):
                with st.spinner("🔮  O Oráculo está elaborando o Plano de Testes..."):
                    try:
                        resultado_plano = grafo_plano_testes.invoke(st.session_state.analysis_state)
                        st.session_state.analysis_state.update(resultado_plano)
                        st.session_state.test_plan_report = resultado_plano.get("relatorio_plano_de_testes")
                        
                        test_plan_json = st.session_state.analysis_state.get("plano_e_casos_de_teste", {})
                        casos_de_teste = test_plan_json.get("casos_de_teste_gherkin", [])
                        if casos_de_teste:
                            df = pd.DataFrame(casos_de_teste)
                            
                            df_clean = df.copy()
                            for col in df_clean.columns:
                                if df_clean[col].apply(lambda x: isinstance(x, list)).any():
                                    df_clean[col] = df_clean[col].apply(lambda x: '\n'.join(map(str, x)) if isinstance(x, list) else x)
                            df_clean.fillna("", inplace=True)
                            st.session_state.test_plan_df = df_clean
                            
                            analysis_report_for_pdf = st.session_state.analysis_state.get("relatorio_analise_inicial", "")
                            pdf_bytes = generate_pdf_report(analysis_report_for_pdf, df_clean)
                            st.session_state.pdf_report_bytes = pdf_bytes
                        
                        st.session_state.show_generate_plan_button = False
                        st.session_state.analysis_finished = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ocorreu um erro crítico ao gerar o plano de testes: {e}")
        with col2:
            if st.button("Não, Encerrar", use_container_width=True):
                st.session_state.show_generate_plan_button = False
                st.session_state.analysis_finished = True
                st.rerun()

# --- Exibição do Plano de Testes (se gerado) ---
if st.session_state.test_plan_report:
    st.divider()
    with st.expander("2. Plano de Testes Detalhado", expanded=True):
        st.markdown(st.session_state.test_plan_report)
        if st.session_state.test_plan_df is not None and not st.session_state.test_plan_df.empty:
            st.subheader("Tabela Interativa de Casos de Teste")
            st.dataframe(st.session_state.test_plan_df, use_container_width=True)
        
        test_plan_json = st.session_state.analysis_state.get("plano_e_casos_de_teste", {})
        if test_plan_json:
            with st.expander("Ver JSON completo do Plano de Testes"):
                st.json(test_plan_json)

# --- Bloco de Ações Finais ---
if st.session_state.analysis_finished:
    st.divider()
    st.success("Análise concluída com sucesso!")
    
    st.subheader("Downloads Disponíveis")

    if st.session_state.test_plan_df is not None and not st.session_state.test_plan_df.empty:
        st.info("Para exportar para o Azure DevOps, por favor, preencha os campos abaixo.")
        
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            st.text_input(
                "Area Path (Caminho da Área):",
                key="area_path_input",
                placeholder="Ex: NomeDoProjeto\\TimeDeProduto",
                help="Copie e cole o Area Path exato do seu projeto no Azure DevOps."
            )
        with col_input2:
            st.text_input(
                "Atribuído a (Assigned To):",
                key="assigned_to_input",
                placeholder="Ex: Nome Sobrenome <email@dominio.com>",
                help="Insira o nome e email do responsável como configurado no Azure DevOps."
            )

    col1, col2, col3 = st.columns(3)

    with col1:
        relatorio_completo_md = (f"{st.session_state.analysis_state.get('relatorio_analise_inicial', '')}")
        if st.session_state.test_plan_report:
             relatorio_completo_md += f"\n\n---\n\n{st.session_state.test_plan_report}"
        
        st.download_button(
            label="📥 Baixar Análise (.md)",
            data=relatorio_completo_md.encode("utf-8"),
            file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input, "md"),
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        if st.session_state.pdf_report_bytes:
            st.download_button(
                label="📄 Baixar Relatório (.pdf)",
                data=st.session_state.pdf_report_bytes,
                file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input, "pdf"),
                mime="application/pdf",
                use_container_width=True
            )
            
    with col3:
        if st.session_state.test_plan_df is not None and not st.session_state.test_plan_df.empty:
            area_path_input = st.session_state.area_path_input
            assigned_to_input = st.session_state.assigned_to_input
            
            is_disabled = not (
                bool(area_path_input and area_path_input.strip()) and 
                bool(assigned_to_input and assigned_to_input.strip())
            )
            
            if is_disabled:
                st.warning("Preencha o 'Area Path' e 'Atribuído a' para habilitar o download.")

            df_para_excel = preparar_df_para_azure_xlsx(
                st.session_state.test_plan_df, 
                area_path_input, 
                assigned_to_input
            )
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_para_excel.to_excel(writer, index=False, sheet_name='Test Cases')
            excel_data = output.getvalue()
            
            st.download_button(
                label="🚀 Baixar para Azure (.xlsx)",
                data=excel_data,
                file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input, "azure.xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Baixa os casos de teste no formato de importação do Azure Test Plans.",
                disabled=is_disabled
            )

    st.divider()
    st.button(
        "🔄 Realizar Nova Análise", 
        type="primary", 
        use_container_width=True,
        on_click=reset_session
    )