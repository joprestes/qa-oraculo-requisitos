import streamlit as st
import datetime
import re
import pandas as pd
import streamlit.components.v1 as components

from graph import grafo_analise, grafo_plano_testes

# --- Configuração da Página ---
st.set_page_config(
    page_title="QA Oráculo | Análise de User Story e Geração de Testes com IA",
    page_icon="🤖", 
    layout="wide"
)

# --- Gerenciamento de Estado da Sessão (Simplificado) ---
if "analysis_state" not in st.session_state:
    st.session_state.analysis_state = None
if "test_plan_report" not in st.session_state:
    st.session_state.test_plan_report = None
if "show_generate_plan_button" not in st.session_state:
    st.session_state.show_generate_plan_button = False
if "user_story_input" not in st.session_state:
    st.session_state.user_story_input = ""

# O bloco de CSS customizado foi COMPLETAMENTE REMOVIDO

# --- Funções Auxiliares ---
def gerar_nome_arquivo_seguro(user_story: str) -> str:
    if not user_story: return "relatorio_qa_oraculo.md"
    primeira_linha_us = user_story.split('\n')[0].lower()
    nome_base = re.sub(r'[^\w\s-]', '', primeira_linha_us).strip()
    nome_base = re.sub(r'[-\s]+', '-', nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.md"

# --- Interface do Usuário (UI) ---
st.title("🤖 QA Oráculo")
st.markdown("Bem-vindo ao seu assistente de QA Sênior. Cole uma User Story abaixo para iniciar a análise.")

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

# --- Exibição dos Resultados e Fluxo Interativo (REFATORADO COM st.expander) ---

if st.session_state.analysis_state:
    st.divider()
    # <-- MUDANÇA: Usando st.expander para criar um card visual -->
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
            with st.spinner("🤖 O Oráculo está elaborando o Plano de Testes..."):
                try:
                    resultado_plano = grafo_plano_testes.invoke(st.session_state.analysis_state)
                    st.session_state.analysis_state.update(resultado_plano)
                    st.session_state.test_plan_report = resultado_plano.get("relatorio_plano_de_testes")
                    st.session_state.show_generate_plan_button = False
                except Exception as e:
                    st.error(f"Ocorreu um erro crítico ao gerar o plano de testes: {e}")

if st.session_state.test_plan_report:
    st.divider()
    # <-- MUDANÇA: Usando st.expander também para o segundo relatório -->
    with st.expander("2. Plano de Testes Detalhado", expanded=True):
        test_plan_json = st.session_state.analysis_state.get("plano_e_casos_de_teste", {})
        
        if test_plan_json:
            st.markdown(st.session_state.test_plan_report)
            casos_de_teste = test_plan_json.get("casos_de_teste_gherkin")
            if casos_de_teste and isinstance(casos_de_teste, list) and len(casos_de_teste) > 0:
                st.subheader("Tabela Interativa de Casos de Teste")
                df = pd.DataFrame(casos_de_teste)
                if 'cenario' in df.columns:
                    df['cenario'] = df['cenario'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else x)
                st.dataframe(df, use_container_width=True)
            with st.expander("Ver JSON completo do Plano de Testes"):
                st.json(test_plan_json)
        else:
            st.markdown(st.session_state.test_plan_report)
            
    st.divider()
    
    relatorio_completo_para_download = (f"{st.session_state.analysis_state.get('relatorio_analise_inicial', '')}\n\n---\n\n{st.session_state.test_plan_report}")
    
    st.download_button(
        label="📥 Baixar Relatório Completo",
        data=relatorio_completo_para_download.encode("utf-8"),
        file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input),
        mime="text/markdown",
    )