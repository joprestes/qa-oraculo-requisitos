import json
import os
import re
import time
from typing import TypedDict, Any

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

# --- Funções Auxiliares e Estrutura de Dados (Sem alterações) ---
def extrair_json_da_resposta(texto_resposta: str) -> str | None:
    
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", texto_resposta)
    if match:
        return match.group(1).strip()
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", texto_resposta)
    if match:
        return match.group(0).strip()
    return None

def chamar_modelo_com_retry(model, prompt_completo, tentativas=3, espera=60):
    
    for tentativa in range(tentativas):
        try:
            resposta = model.generate_content(prompt_completo)
            return resposta
        except ResourceExhausted as e:
            print(f"⚠️ Alerta de Limite de Requisições (Tentativa {tentativa + 1}/{tentativas}).")
            if tentativa < tentativas - 1:
                print(f"Aguardando {espera} segundos para tentar novamente...")
                time.sleep(espera)
            else:
                print("❌ Esgotado o número de tentativas. A chamada falhou.")
                return None
        except Exception as e:
            print(f"❌ Ocorreu um erro inesperado na comunicação: {e}")
            return None
    return None

class AgentState(TypedDict):
    user_story: str
    analise_da_us: dict[str, Any]
    relatorio_analise_inicial: str
    plano_e_casos_de_teste: dict[str, Any]
    relatorio_plano_de_testes: str

# --- Nós do Grafo  ---
def node_analisar_historia(state: AgentState) -> AgentState:
    
    print("--- Etapa 1: Analisando a User Story... ---")
    us = state["user_story"]
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_ANALISE_US}\n\nUser Story para Análise:\n---\n{us}"
    response = chamar_modelo_com_retry(model, prompt_completo)
    analise_json = {}
    if not response or not response.text:
        analise_json = {"erro": "Falha na comunicação com o serviço de análise."}
    else:
        json_limpo = extrair_json_da_resposta(response.text)
        if json_limpo:
            try:
                analise_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                analise_json = {"erro": "Falha ao decodificar a resposta da análise."}
        else:
            analise_json = {"erro": "Nenhum dado estruturado encontrado na resposta."}
    return {"analise_da_us": analise_json}

def node_gerar_relatorio_analise(state: AgentState) -> AgentState:
    
    print("--- Etapa 2: Compilando relatório de análise inicial... ---")
    contexto = {"user_story_original": state["user_story"], "analise": state.get("analise_da_us", {})}
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_ANALISE}\n\nDados:\n---\n{contexto_str}"
    response = chamar_modelo_com_retry(model, prompt_completo)
    if response and response.text:
        return {"relatorio_analise_inicial": response.text}
    else:
        return {"relatorio_analise_inicial": "# Erro na Geração do Relatório"}

def node_criar_plano_e_casos_de_teste(state: AgentState) -> AgentState:
    
    print("--- Etapa Extra: Criando Plano e Casos de Teste... ---")
    contexto_para_plano = {"user_story": state["user_story"], "analise_ambiguidade": state["analise_da_us"].get("analise_ambiguidade", {})}
    contexto_str = json.dumps(contexto_para_plano, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_CRIAR_PLANO_DE_TESTES}\n\nContexto:\n---\n{contexto_str}"
    response = chamar_modelo_com_retry(model, prompt_completo)
    plano_json = {}
    if not response or not response.text:
        plano_json = {"erro": "Falha na comunicação com o serviço de planejamento."}
    else:
        json_limpo = extrair_json_da_resposta(response.text)
        if json_limpo:
            try:
                plano_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                plano_json = {"erro": "Falha ao decodificar a resposta do plano."}
        else:
            plano_json = {"erro": "Nenhum dado estruturado encontrado na resposta."}
    return {"plano_e_casos_de_teste": plano_json}

def node_gerar_relatorio_plano_de_testes(state: AgentState) -> AgentState:
    # ... (código existente)
    print("--- Etapa 4: Compilando o relatório do plano de testes... ---")
    contexto = state.get("plano_e_casos_de_teste", {})
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES}\n\nDados:\n---\n{contexto_str}"
    response = chamar_modelo_com_retry(model, prompt_completo)
    if response and response.text:
        return {"relatorio_plano_de_testes": response.text}
    else:
        return {"relatorio_plano_de_testes": "### Erro na Geração do Plano de Testes"}



# Grafo 1: Apenas para a análise inicial
workflow_analise = StateGraph(AgentState)
workflow_analise.add_node("analista_us", node_analisar_historia)
workflow_analise.add_node("gerador_relatorio_analise", node_gerar_relatorio_analise)
workflow_analise.set_entry_point("analista_us")
workflow_analise.add_edge("analista_us", "gerador_relatorio_analise")
workflow_analise.add_edge("gerador_relatorio_analise", END)
grafo_analise = workflow_analise.compile()

# Grafo 2: Apenas para o plano de testes (continuação)
workflow_plano_testes = StateGraph(AgentState)
workflow_plano_testes.add_node("criador_plano_testes", node_criar_plano_e_casos_de_teste)
workflow_plano_testes.add_node("gerador_relatorio_plano_de_testes", node_gerar_relatorio_plano_de_testes)
workflow_plano_testes.set_entry_point("criador_plano_testes")
workflow_plano_testes.add_edge("criador_plano_testes", "gerador_relatorio_plano_de_testes")
workflow_plano_testes.add_edge("gerador_relatorio_plano_de_testes", END)
grafo_plano_testes = workflow_plano_testes.compile()