import streamlit as st
import datetime
import re
import pandas as pd
import streamlit.components.v1 as components
from pdf_generator import generate_pdf_report
from graph import grafo_analise, grafo_plano_testes

# --- Configuração da Página ---
st.set_page_config(
    page_title="QA Oráculo | Análise de User Story e Geração de Testes com IA",
    page_icon="🤖",
    layout="wide"
)

# --- Gerenciamento de Estado da Sessão  ---
if "analysis_state" not in st.session_state:
    st.session_state.analysis_state = None
if "test_plan_report" not in st.session_state:
    st.session_state.test_plan_report = None
# <-- DataFrame e os bytes do PDF ao estado da sessão -->
if "test_plan_df" not in st.session_state:
    st.session_state.test_plan_df = None
if "pdf_report_bytes" not in st.session_state:
    st.session_state.pdf_report_bytes = None

if "show_generate_plan_button" not in st.session_state:
    st.session_state.show_generate_plan_button = False
if "user_story_input" not in st.session_state:
    st.session_state.user_story_input = ""

# --- Funções Auxiliares ---
def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str: 
    if not user_story: return f"relatorio_qa_oraculo.{extension}"
    primeira_linha_us = user_story.split('\n')[0].lower()
    nome_base = re.sub(r'[^\w\s-]', '', primeira_linha_us).strip()
    nome_base = re.sub(r'[-\s]+', '-', nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.{extension}" 

# --- Interface do Usuário (UI) ---
st.title("🤖 QA Oráculo")
st.markdown("Seja bem-vindo! Como seu Assistente de QA Sênior, estou aqui para apoiar na revisão de User Stories. Cole uma abaixo e vamos começar.")

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
            except Exception as e:
                st.error(f"Ocorreu um erro crítico durante a análise: {e}")
    else:
        st.warning("Por favor, insira uma User Story antes de analisar.")

# --- Exibição dos Resultados e Fluxo Interativo ---

if st.session_state.analysis_state:
    st.divider()
    with st.expander("1. Análise Inicial da User Story", expanded=True):
        analysis_report = st.session_state.analysis_state.get("relatorio_analise_inicial", "")
        analysis_json = st.session_state.analysis_state.get("analise_da_us")
        st.markdown(analysis_report)
        if analysis_json:
            with st.expander("Ver detalhes da Análise em JSON"):
                st.json(analysis_json)

    if st.session_state.show_generate_plan_button:
        st.info("A análise inicial está pronta. Deseja que o Oráculo continue e gere um Plano de Testes detalhado?")
        if st.button("Sim, Gerar Plano de Testes Detalhado"):
            with st.spinner("🔮  O Oráculo está elaborando o Plano de Testes..."):
                try:
                    resultado_plano = grafo_plano_testes.invoke(st.session_state.analysis_state)
                    st.session_state.analysis_state.update(resultado_plano)
                    st.session_state.test_plan_report = resultado_plano.get("relatorio_plano_de_testes")
                    
                    #  Lógica para criar o DataFrame e gerar o PDF -->
                    test_plan_json = st.session_state.analysis_state.get("plano_e_casos_de_teste", {})
                    casos_de_teste = test_plan_json.get("casos_de_teste_gherkin", [])
                    if casos_de_teste:
                        df = pd.DataFrame(casos_de_teste)
                        st.session_state.test_plan_df = df # Salva o DF no estado
                        
                        # Gera o PDF usando o relatório de análise e o novo DF
                        analysis_report_for_pdf = st.session_state.analysis_state.get("relatorio_analise_inicial", "")
                        pdf_bytes = generate_pdf_report(analysis_report_for_pdf, df)
                        st.session_state.pdf_report_bytes = pdf_bytes # Salva os bytes do PDF no estado
                    
                    st.session_state.show_generate_plan_button = False
                except Exception as e:
                    st.error(f"Ocorreu um erro crítico ao gerar o plano de testes: {e}")

if st.session_state.test_plan_report:
    st.divider()
    with st.expander("2. Plano de Testes Detalhado", expanded=True):
        st.markdown(st.session_state.test_plan_report)
        
        # Exibe a tabela interativa se o DataFrame existir no estado da sessão
        if st.session_state.test_plan_df is not None and not st.session_state.test_plan_df.empty:
            st.subheader("Tabela Interativa de Casos de Teste")
            df_to_display = st.session_state.test_plan_df.copy()
            # Tratamento para exibição no Streamlit, se necessário
            if 'cenario' in df_to_display.columns:
                df_to_display['cenario'] = df_to_display['cenario'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else x)
            st.dataframe(df_to_display, use_container_width=True)
            
        test_plan_json = st.session_state.analysis_state.get("plano_e_casos_de_teste", {})
        if test_plan_json:
            with st.expander("Ver JSON completo do Plano de Testes"):
                st.json(test_plan_json)
            
    st.divider()
    
    # --- BLOCO DE DOWNLOADS ---
    col1, col2 = st.columns(2)

    with col1:
        # Botão de download para o relatório em Markdown 
        relatorio_completo_md = (f"{st.session_state.analysis_state.get('relatorio_analise_inicial', '')}\n\n---\n\n{st.session_state.test_plan_report}")
        st.download_button(
            label="📥 Baixar Relatório (.md)",
            data=relatorio_completo_md.encode("utf-8"),
            file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input, "md"),
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        # Botão de download para o relatório em PDF -->
        if st.session_state.pdf_report_bytes:
            st.download_button(
                label="📄 Baixar Relatório (.pdf)",
                data=st.session_state.pdf_report_bytes,
                file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input, "pdf"),
                mime="application/pdf",
                use_container_width=True
            )