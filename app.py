import streamlit as st
import json
import datetime
import re
from pathlib import Path

from graph import grafo 

# --- Configuração da Página do Streamlit ---
st.set_page_config(
    page_title="QA Oráculo",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Gerenciamento de Estado da Sessão ---
if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None
if "test_plan_report" not in st.session_state: 
    st.session_state.test_plan_report = None
if "final_report" not in st.session_state:
    st.session_state.final_report = None
if "user_story_input" not in st.session_state:
    st.session_state.user_story_input = ""
if "analysis_json" not in st.session_state:
    st.session_state.analysis_json = None
if "test_plan_json" not in st.session_state:
    st.session_state.test_plan_json = None


# --- Funções Auxiliares ---
def gerar_nome_arquivo_seguro(user_story: str) -> str:
    """
    Gera um nome de arquivo seguro e único a partir da User Story.
    """
    if not user_story:
        return "relatorio_qa_oraculo.md"
    
    
    primeira_linha_us = user_story.split('\n')[0].lower()
    
    nome_base = re.sub(r'[^\w\s-]', '', primeira_linha_us).strip()
    nome_base = re.sub(r'[-\s]+', '-', nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.md"


# --- Interface do Usuário (UI) ---
st.title("🤖 QA Oráculo")
st.markdown(
    """
    Bem-vindo ao seu assistente de QA Sênior.
    Cole uma User Story (US) abaixo para receber uma análise detalhada, 
    incluindo ambiguidades, critérios de aceite e perguntas para o Product Owner.
    """
)

user_story = st.text_area(
    "Insira a User Story aqui:",
    height=250,
    placeholder="Ex: Como um cliente registrado, eu quero poder visualizar meu histórico de pedidos para que eu possa acompanhar minhas compras.",
    key="user_story_input"
)

if st.button("Analisar User Story", type="primary"):
    if user_story and user_story.strip():
        # Limpa o estado de relatórios anteriores
        st.session_state.analysis_report = None
        st.session_state.final_report = None
        st.session_state.analysis_json = None
        st.session_state.test_plan_json = None

        with st.spinner("🔮 O Oráculo está conjurando a análise... Por favor, aguarde."):
            try:
                inputs = {"user_story": user_story, "user_response": "y"}
                resultado_completo = grafo.invoke(inputs)

                
                st.session_state.analysis_report = resultado_completo.get("relatorio_analise_inicial")
                st.session_state.test_plan_report = resultado_completo.get("relatorio_plano_de_testes")
                st.session_state.analysis_json = resultado_completo.get("analise_da_us")
                st.session_state.test_plan_json = resultado_completo.get("plano_e_casos_de_teste")

            except Exception as e:
                st.error(f"Ocorreu um erro crítico durante a execução do grafo: {e}")
    else:
        st.warning("Por favor, insira uma User Story antes de analisar.")


# --- Exibição dos Resultados ---

if st.session_state.analysis_report:
    st.markdown("---")
    st.subheader("1. Análise Inicial da User Story")
    st.markdown(st.session_state.analysis_report)
    if st.session_state.analysis_json:
        with st.expander("Ver detalhes da Análise em JSON"):
            st.json(st.session_state.analysis_json)

if st.session_state.test_plan_report:
    st.markdown("---")
    st.subheader("2. Plano de Testes Detalhado")
    st.markdown(st.session_state.test_plan_report)
    if st.session_state.test_plan_json:
        with st.expander("Ver detalhes do Plano de Testes em JSON"):
            st.json(st.session_state.test_plan_json)

    st.markdown("---")
    
    # Prepara o conteúdo completo para download
    relatorio_completo_para_download = (
        f"{st.session_state.analysis_report}\n\n"
        f"---\n\n"
        f"{st.session_state.test_plan_report}"
    )
    
    st.download_button(
        label="📥 Baixar Relatório Completo",
        data=relatorio_completo_para_download.encode("utf-8"),
        file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input),
        mime="text/markdown",
    )