import json
import os
import re
import time
from typing import TypedDict, Any

import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from config import NOME_MODELO, CONFIG_GERACAO_ANALISE, CONFIG_GERACAO_RELATORIO
from prompts import (
    PROMPT_ANALISE_US,
    PROMPT_CRIAR_PLANO_DE_TESTES,
    PROMPT_GERAR_RELATORIO_ANALISE,
    PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES
)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# --- Funções Auxiliares e Estrutura de Dados ---
def extrair_json_da_resposta(texto_resposta: str) -> str | None:
    """Função de segurança para extrair JSON de uma string, caso a API não retorne JSON puro."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", texto_resposta)
    if match: return match.group(1).strip()
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", texto_resposta)
    if match: return match.group(0).strip()
    return None

def chamar_modelo_com_retry(model, prompt_completo, tentativas=3, espera=60):
    """Encapsula a chamada à API com lógica de retry para lidar com limites de requisição."""
    for tentativa in range(tentativas):
        try:
            return model.generate_content(prompt_completo)
        except ResourceExhausted:
            print(f"⚠️ Limite de Requisições (Tentativa {tentativa + 1}/{tentativas}). Aguardando {espera}s...")
            if tentativa < tentativas - 1: time.sleep(espera)
            else: print("❌ Esgotado o número de tentativas.")
        except Exception as e:
            print(f"❌ Erro inesperado na comunicação: {e}")
            return None
    return None

class AgentState(TypedDict):
    """Define a estrutura de estado que flui através dos grafos."""
    user_story: str
    analise_da_us: dict[str, Any]
    relatorio_analise_inicial: str
    plano_e_casos_de_teste: dict[str, Any]
    relatorio_plano_de_testes: str

# --- Nós do Grafo ---
def node_analisar_historia(state: AgentState) -> AgentState:
    print("--- Etapa 1: Analisando a User Story... ---")
    us = state["user_story"]
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_ANALISE_US}\n\nUser Story para Análise:\n---\n{us}"
    response = chamar_modelo_com_retry(model, prompt_completo)
    
    if not response or not response.text:
        return {"analise_da_us": {"erro": "Falha na comunicação com o serviço de análise."}}
    
    try:
        # Tenta decodificar diretamente, pois `response_mime_type` deve garantir JSON puro
        analise_json = json.loads(response.text)
    except json.JSONDecodeError:
        # Se falhar, tenta limpar a string como um fallback de segurança
        json_limpo = extrair_json_da_resposta(response.text)
        if json_limpo:
            try:
                analise_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                 analise_json = {"erro": f"Falha ao decodificar a resposta da análise. Resposta recebida: {response.text}"}
        else:
            analise_json = {"erro": f"Nenhum dado estruturado encontrado na resposta. Resposta recebida: {response.text}"}
            
    return {"analise_da_us": analise_json}

def node_gerar_relatorio_analise(state: AgentState) -> AgentState:
    print("--- Etapa 2: Compilando relatório de análise... ---")
    contexto = {"user_story_original": state["user_story"], "analise": state.get("analise_da_us", {})}
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_ANALISE}\n\nDados:\n---\n{contexto_str}"
    response = chamar_modelo_com_retry(model, prompt_completo)
    return {"relatorio_analise_inicial": response.text if response and response.text else "# Erro na Geração do Relatório"}

def node_criar_plano_e_casos_de_teste(state: AgentState) -> AgentState:
    print("--- Etapa Extra: Criando Plano de Testes... ---")
    contexto_para_plano = {"user_story": state["user_story"], "analise_ambiguidade": state["analise_da_us"].get("analise_ambiguidade", {})}
    contexto_str = json.dumps(contexto_para_plano, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_CRIAR_PLANO_DE_TESTES}\n\nContexto:\n---\n{contexto_str}"
    response = chamar_modelo_com_retry(model, prompt_completo)

    if not response or not response.text:
        return {"plano_e_casos_de_teste": {"erro": "Falha na comunicação com o serviço de planejamento."}}

    try:
        plano_json = json.loads(response.text)
    except json.JSONDecodeError:
        json_limpo = extrair_json_da_resposta(response.text)
        if json_limpo:
            try:
                plano_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                plano_json = {"erro": f"Falha ao decodificar a resposta do plano. Resposta recebida: {response.text}"}
        else:
            plano_json = {"erro": f"Nenhum dado estruturado encontrado na resposta. Resposta recebida: {response.text}"}

    return {"plano_e_casos_de_teste": plano_json}

def node_gerar_relatorio_plano_de_testes(state: AgentState) -> AgentState:
    print("--- Etapa 4: Compilando relatório do plano... ---")
    contexto = state.get("plano_e_casos_de_teste", {})
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES}\n\nDados:\n---\n{contexto_str}"
    response = chamar_modelo_com_retry(model, prompt_completo)
    return {"relatorio_plano_de_testes": response.text if response and response.text else "### Erro na Geração do Plano de Testes"}

# --- Construção e Cache dos Grafos ---
@st.cache_resource
def get_analysis_graph():
    """Cria, compila e cacheia o grafo para a análise inicial."""
    print("--- ⚙️ COMPILANDO GRAFO DE ANÁLISE (deve aparecer só uma vez) ---")
    workflow_analise = StateGraph(AgentState)
    workflow_analise.add_node("analista_us", node_analisar_historia)
    workflow_analise.add_node("gerador_relatorio_analise", node_gerar_relatorio_analise)
    workflow_analise.set_entry_point("analista_us")
    workflow_analise.add_edge("analista_us", "gerador_relatorio_analise")
    workflow_analise.add_edge("gerador_relatorio_analise", END)
    return workflow_analise.compile()

@st.cache_resource
def get_test_plan_graph():
    """Cria, compila e cacheia o grafo para o plano de testes."""
    print("--- ⚙️ COMPILANDO GRAFO DE PLANO DE TESTES (deve aparecer só uma vez) ---")
    workflow_plano_testes = StateGraph(AgentState)
    workflow_plano_testes.add_node("criador_plano_testes", node_criar_plano_e_casos_de_teste)
    workflow_plano_testes.add_node("gerador_relatorio_plano_de_testes", node_gerar_relatorio_plano_de_testes)
    workflow_plano_testes.set_entry_point("criador_plano_testes")
    workflow_plano_testes.add_edge("criador_plano_testes", "gerador_relatorio_plano_de_testes")
    workflow_plano_testes.add_edge("gerador_relatorio_plano_de_testes", END)
    return workflow_plano_testes.compile()

# --- Instanciação dos Grafos ---
grafo_analise = get_analysis_graph()
grafo_plano_testes = get_test_plan_graph()