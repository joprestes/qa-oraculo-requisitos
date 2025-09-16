import json
import os
import re
import time
from typing import TypedDict, List, Dict, Any

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# Importa de outros módulos do projeto
from config import NOME_MODELO, CONFIG_GERACAO_ANALISE, CONFIG_GERACAO_RELATORIO
from prompts import (
    PROMPT_ANALISE_US,
    PROMPT_CRIAR_PLANO_DE_TESTES,
    PROMPT_GERAR_RELATORIO_ANALISE,
    PROMPT_GERAR_RELATORIO_COMPLETO
)

# Configuração da API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Funções Auxiliares ---

def extrair_json_da_resposta(texto_resposta: str) -> str | None:
    """Extrai uma string JSON de um texto bruto, limpando formatação comum."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", texto_resposta)
    if match:
        return match.group(1).strip()
    
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", texto_resposta)
    if match:
        return match.group(0).strip()
        
    return None

def chamar_modelo_com_retry(model, prompt_completo, tentativas=3, espera=60):
    """
    Executa uma chamada ao modelo generativo com lógica de retry para erros de cota.
    """
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

# --- Estruturas de Dados ---

class AgentState(TypedDict):
    user_story: str
    analise_da_us: Dict[str, Any]
    relatorio_analise_inicial: str 
    decisao_usuario_plano_testes: str
    plano_e_casos_de_teste: Dict[str, Any]
    relatorio_final_completo: str   

# --- Nós do Grafo ---

def node_analisar_historia(state: AgentState) -> AgentState:
    """Gera a análise de qualidade inicial da User Story."""
    print("--- Etapa 1: Analisando a User Story... ---")
    us = state["user_story"]
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_ANALISE_US}\n\nUser Story para Análise:\n---\n{us}"
    
    response = chamar_modelo_com_retry(model, prompt_completo)
    analise_json = {}

    if not response or not response.text:
        print("❌ Falha na comunicação com o serviço de análise.")
        analise_json = {"erro": "Falha na comunicação com o serviço de análise."}
    else:
        json_limpo = extrair_json_da_resposta(response.text)
        if json_limpo:
            try:
                analise_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                print("⚠️ Alerta: A resposta da análise continha um formato inválido.")
                analise_json = {"erro": "Falha ao decodificar a resposta da análise."}
        else:
            print("⚠️ Alerta: A resposta da análise não continha dados estruturados.")
            analise_json = {"erro": "Nenhum dado estruturado encontrado na resposta."}
        
    return {"analise_da_us": analise_json}

def node_gerar_relatorio_analise(state: AgentState) -> AgentState:
    """Compila e formata o relatório de análise inicial."""
    print("--- Etapa 2: Compilando relatório de análise inicial... ---")
    contexto = {
        "user_story_original": state["user_story"],
        "analise": state.get("analise_da_us", {})
    }
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_ANALISE}\n\nDados:\n---\n{contexto_str}"

    response = chamar_modelo_com_retry(model, prompt_completo)
    
    if response and response.text:
        return {"relatorio_analise_inicial": response.text}
    else:
        print("❌ Falha ao gerar o relatório de análise inicial.")
        relatorio_de_erro = "# Erro na Geração do Relatório\n\nO serviço de geração de relatórios não respondeu."
        return {"relatorio_analise_inicial": relatorio_de_erro}

def node_perguntar_plano_de_testes(state: AgentState) -> AgentState:
    """Apresenta o relatório inicial e solicita o próximo passo ao usuário."""
    print("\n--- ✅ Relatório de Análise Inicial Gerado ---")
    print(state.get("relatorio_analise_inicial", "Erro ao gerar relatório inicial."))
    print("-------------------------------------------\n")
    
    resposta = input("Deseja prosseguir com a criação do Plano e Casos de Teste? (s/n): ").lower()
    return {"decisao_usuario_plano_testes": resposta}

def node_criar_plano_e_casos_de_teste(state: AgentState) -> AgentState:
    """Gera o Plano de Testes detalhado e os Casos de Teste em Gherkin."""
    print("--- Etapa Extra: Criando Plano e Casos de Teste... ---")
    contexto_para_plano = {
        "user_story": state["user_story"],
        "analise_ambiguidade": state["analise_da_us"].get("analise_ambiguidade", {})
    }
    contexto_str = json.dumps(contexto_para_plano, indent=2, ensure_ascii=False)

    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_CRIAR_PLANO_DE_TESTES}\n\nContexto:\n---\n{contexto_str}"

    response = chamar_modelo_com_retry(model, prompt_completo)
    plano_json = {}

    if not response or not response.text:
        print("❌ Falha na comunicação com o serviço de planejamento de testes.")
        plano_json = {"erro": "Falha na comunicação com o serviço de planejamento de testes."}
    else:
        json_limpo = extrair_json_da_resposta(response.text)
        if json_limpo:
            try:
                plano_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                print("⚠️ Alerta: A resposta do plano de testes continha um formato inválido.")
                plano_json = {"erro": "Falha ao decodificar a resposta do plano de testes."}
        else:
            print("⚠️ Alerta: A resposta do plano de testes não continha dados estruturados.")
            plano_json = {"erro": "Nenhum dado estruturado encontrado na resposta do plano."}

    return {"plano_e_casos_de_teste": plano_json}

def node_gerar_relatorio_completo(state: AgentState) -> AgentState:
    """Compila e formata o relatório final, incluindo o plano de testes."""
    print("--- Etapa 4: Compilando o relatório completo... ---")
    contexto = {
        "user_story_original": state["user_story"],
        "analise": state.get("analise_da_us", {}),
        "plano_de_testes": state.get("plano_e_casos_de_teste")
    }
    
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_COMPLETO}\n\nDados:\n---\n{contexto_str}"

    response = chamar_modelo_com_retry(model, prompt_completo)
    
    if response and response.text:
        return {"relatorio_final_completo": response.text}
    else:
        print("❌ Falha ao gerar o relatório completo.")
        relatorio_de_erro = "# Erro na Geração do Relatório Final\n\nO serviço de geração de relatórios não respondeu."
        return {"relatorio_final_completo": relatorio_de_erro}

def decidir_proximo_passo(state: AgentState):
    """Decide o próximo passo do fluxo com base na entrada do usuário."""
    if state.get("decisao_usuario_plano_testes") == "s":
        return "criar_plano_e_casos"
    else:
        return "fim"

# --- Construção e Compilação do Grafo ---
workflow = StateGraph(AgentState)

workflow.add_node("analista_us", node_analisar_historia)
workflow.add_node("gerador_relatorio_analise", node_gerar_relatorio_analise)
workflow.add_node("perguntar_usuario", node_perguntar_plano_de_testes)
workflow.add_node("criador_plano_testes", node_criar_plano_e_casos_de_teste)
workflow.add_node("gerador_relatorio_completo", node_gerar_relatorio_completo)

workflow.set_entry_point("analista_us")
workflow.add_edge("analista_us", "gerador_relatorio_analise")
workflow.add_edge("gerador_relatorio_analise", "perguntar_usuario")
workflow.add_conditional_edges(
    "perguntar_usuario",
    decidir_proximo_passo,
    {
        "criar_plano_e_casos": "criador_plano_testes",
        "fim": END
    }
)
workflow.add_edge("criador_plano_testes", "gerador_relatorio_completo")
workflow.add_edge("gerador_relatorio_completo", END)

grafo = workflow.compile()