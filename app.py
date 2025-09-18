import streamlit as st
import datetime
import re
import pandas as pd

from graph import grafo_analise, grafo_plano_testes

# --- Configuração da Página ---
st.set_page_config(page_title="QA Oráculo", page_icon="🤖", layout="wide") 

# --- Gerenciamento de Estado da Sessão ---
if "analysis_state" not in st.session_state:
    st.session_state.analysis_state = None
if "test_plan_report" not in st.session_state:
    st.session_state.test_plan_report = None
if "show_generate_plan_button" not in st.session_state:
    st.session_state.show_generate_plan_button = False
if "user_story_input" not in st.session_state:
    st.session_state.user_story_input = ""

# --- Funções Auxiliares ---
def gerar_nome_arquivo_seguro(user_story: str) -> str:
    if not user_story:
        return "relatorio_qa_oraculo.md"
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
    key="user_story_input"
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

# --- Exibição dos Resultados e Fluxo Interativo ---

if st.session_state.analysis_state:
    analysis_report = st.session_state.analysis_state.get("relatorio_analise_inicial", "")
    analysis_json = st.session_state.analysis_state.get("analise_da_us")
    st.markdown("---")
    st.subheader("1. Análise Inicial da User Story")
    st.markdown(analysis_report, unsafe_allow_html=True)
    if analysis_json:
        with st.expander("Ver detalhes da Análise em JSON"):
            st.json(analysis_json)
    
    if st.session_state.show_generate_plan_button:
        st.markdown("---")
        st.info("Deseja aprofundar a análise e criar um Plano de Testes detalhado?")
        if st.button("Sim, Gerar Plano de Testes"):
            with st.spinner("🤖 O Oráculo está elaborando o Plano de Testes..."):
                try:
                    resultado_plano = grafo_plano_testes.invoke(st.session_state.analysis_state)
                    st.session_state.analysis_state.update(resultado_plano)
                    st.session_state.test_plan_report = resultado_plano.get("relatorio_plano_de_testes")
                    st.session_state.show_generate_plan_button = False
                except Exception as e:
                    st.error(f"Ocorreu um erro crítico ao gerar o plano de testes: {e}")


if st.session_state.test_plan_report:
    test_plan_json = st.session_state.analysis_state.get("plano_e_casos_de_teste", {})

    st.markdown("---")
    st.subheader("2. Plano de Testes Detalhado")

    if test_plan_json:
        # Pega o objeto 'plano_de_testes' de dentro do JSON
        plano = test_plan_json.get("plano_de_testes", {})
        
        # Exibe o relatório em Markdown gerado pelo backend (que já está bem formatado)
        st.markdown(st.session_state.test_plan_report, unsafe_allow_html=True)

        # Pega a lista de casos de teste da nova chave 'casos_de_teste_gherkin'
        casos_de_teste = test_plan_json.get("casos_de_teste_gherkin")
        if casos_de_teste and isinstance(casos_de_teste, list) and len(casos_de_teste) > 0:
            st.subheader("Tabela de Casos de Teste Interativa")
            try:
                df = pd.DataFrame(casos_de_teste)
                
                # Junta a lista de strings do 'cenario' em uma única string com quebras de linha
                if 'cenario' in df.columns:
                    df['cenario'] = df['cenario'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else x)
                
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Não foi possível formatar os casos de teste em uma tabela interativa: {e}")

        with st.expander("Ver JSON completo do Plano de Testes"):
            st.json(test_plan_json)
    else:
        # Fallback caso o JSON não seja gerado corretamente
        st.markdown(st.session_state.test_plan_report, unsafe_allow_html=True)
            
    st.markdown("---")
    
    relatorio_completo_para_download = (
        f"{st.session_state.analysis_state.get('relatorio_analise_inicial', '')}\n\n"
        f"---\n\n"
        f"{st.session_state.test_plan_report}"
    )
    
    st.download_button(
        label="📥 Baixar Relatório Completo",
        data=relatorio_completo_para_download.encode("utf-8"),
        file_name=gerar_nome_arquivo_seguro(st.session_state.user_story_input),
        mime="text/markdown",
    )