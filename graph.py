import json
import os
import re
import google.generativeai as genai
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# Importa de outros módulos do nosso projeto
from config import NOME_MODELO, CONFIG_GERACAO_ANALISE, CONFIG_GERACAO_RELATORIO
from prompts import (
    PROMPT_ANALISE_US,
    PROMPT_CRIAR_PLANO_DE_TESTES,
    PROMPT_GERAR_RELATORIO_ANALISE,
    PROMPT_GERAR_RELATORIO_COMPLETO
)

# --- Funções Auxiliares e Configs da API (ficam aqui com a lógica) ---
from dotenv import load_dotenv
import time
from google.api_core.exceptions import ResourceExhausted

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extrair_json_da_resposta(texto_resposta: str) -> str | None:
    """
    Extrai uma string JSON de dentro de um texto bruto, limpando formatação Markdown.

    """
    # Procura por ```json ... ``` ou apenas ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", texto_resposta)
    if match:
        return match.group(1).strip()
    
    # Se não encontrar o bloco de código, procura por um JSON que comece com '{' ou '['
    # Isso ajuda a remover textos introdutórios
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", texto_resposta)
    if match:
        return match.group(0).strip()
        
    return None

def chamar_modelo_com_retry(model, prompt_completo, tentativas=3, espera=60):
    """
    Função wrapper que chama a IA, com lógica de retry para erros de cota.
    """
    for tentativa in range(tentativas):
        try:
            # Tenta fazer a chamada à API
            resposta = model.generate_content(prompt_completo)
            return resposta # Se bem-sucedido, retorna a resposta
        
        except ResourceExhausted as e:
            print(f"⚠️ Alerta de Limite de API (Tentativa {tentativa + 1}/{tentativas}): {e.message}")
            if tentativa < tentativas - 1:
                print(f"Aguardando {espera} segundos para tentar novamente...")
                time.sleep(espera) # Pausa a execução
            else:
                print("❌ Esgotado o número de tentativas. A chamada à API falhou.")
                return None # Se todas as tentativas falharem, retorna None
        
        except Exception as e:
            # Captura outros erros inesperados
            print(f"❌ Ocorreu um erro inesperado na chamada à API: {e}")
            return None
    return None

# --- Estado do Agente (AgentState) Simplificado ---

class AgentState(TypedDict):
    user_story: str
    analise_da_us: Dict[str, Any]
    relatorio_analise_inicial: str 
    decisao_usuario_plano_testes: str
    plano_e_casos_de_teste: Dict[str, Any]
    relatorio_final_completo: str   

# --- Nós do Grafo Simplificado ---

def node_analisar_historia(state: AgentState) -> AgentState:
    """Nó 1: Pega a User Story e usa a IA para gerar a análise completa."""
    print("--- Etapa 1: Analisando a User Story... ---")
    us = state["user_story"]
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_ANALISE_US}\n\nUser Story para Análise:\n---\n{us}"
    
    response = chamar_modelo_com_retry(model, prompt_completo)
    analise_json = {}

    if not response or not response.text:
        # Se a chamada com retry falhou, response será None ou sem texto
        print("❌ Falha na comunicação com a API após múltiplas tentativas.")
        analise_json = {"erro": "Falha na comunicação com a API após múltiplas tentativas."}
    else:
        # A chamada à API foi bem-sucedida, agora tentamos processar o texto
        json_limpo = extrair_json_da_resposta(response.text)
        
        if json_limpo:
            try:
                analise_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                print("⚠️ Alerta: A IA retornou um JSON mal formatado.")
                analise_json = {"erro": "Falha ao decodificar o JSON da análise."}
        else:
            print("⚠️ Alerta: A IA não retornou um JSON em sua resposta.")
            analise_json = {"erro": "Nenhum JSON encontrado na resposta da IA."}
        
    return {"analise_da_us": analise_json}

def node_gerar_relatorio_analise(state: AgentState) -> AgentState:
    print("--- Etapa 2: Compilando relatório de análise inicial... ---")
    contexto = {
        "user_story_original": state["user_story"],
        "analise": state.get("analise_da_us", {})
    }
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_ANALISE}\n\nDados:\n---\n{contexto_str}"

    response = chamar_modelo_com_retry(model, prompt_completo)
    
    # Verifica se a chamada foi bem-sucedida e tem texto
    if response and response.text:
        # Se sim, retorna o relatório
        return {"relatorio_analise_inicial": response.text}
    else:
        # Se falhou, retorna uma mensagem de erro como o relatório
        print("❌ Falha ao gerar o relatório de análise inicial.")
        relatorio_de_erro = "# Erro na Geração do Relatório\n\nA comunicação com a API falhou após múltiplas tentativas."
        return {"relatorio_analise_inicial": relatorio_de_erro}

def node_perguntar_plano_de_testes(state: AgentState) -> AgentState:
    """Nó Intermediário: Mostra o relatório inicial e pergunta ao usuário."""
    print("\n--- ✅ Relatório de Análise Inicial Gerado ---")
    print(state.get("relatorio_analise_inicial", "Erro ao gerar relatório inicial."))
    print("-------------------------------------------\n")
    
    resposta = input("Deseja prosseguir com a criação do Plano e Casos de Teste? (s/n): ").lower()
    return {"decisao_usuario_plano_testes": resposta}

def node_criar_plano_e_casos_de_teste(state: AgentState) -> AgentState:
    """Nó Opcional: Usa a IA para gerar o Plano de Testes e os Casos de Teste em Gherkin."""
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
        # Se a chamada com retry falhou
        print("❌ Falha na comunicação com a API para criar o plano de testes.")
        plano_json = {"erro": "Falha na comunicação com a API após múltiplas tentativas."}
    else:
        # A chamada foi bem-sucedida, agora processamos o texto
        json_limpo = extrair_json_da_resposta(response.text)
        
        if json_limpo:
            try:
                plano_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                print("⚠️ Alerta: A IA retornou um JSON mal formatado para o plano de testes.")
                plano_json = {"erro": "Falha ao decodificar o JSON do plano de testes."}
        else:
            print("⚠️ Alerta: A IA não retornou um JSON em sua resposta para o plano de testes.")
            plano_json = {"erro": "Nenhum JSON encontrado na resposta da IA."}

    return {"plano_e_casos_de_teste": plano_json}

def node_gerar_relatorio_completo(state: AgentState) -> AgentState:
    """Nó Final: Consolida TODA a análise em um relatório final em Markdown."""
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
    
    # Verifica se a chamada foi bem-sucedida e tem texto
    if response and response.text:
        # Se sim, retorna o relatório completo
        return {"relatorio_final_completo": response.text}
    else:
        # Se falhou, retorna uma mensagem de erro como o relatório final
        print("❌ Falha ao gerar o relatório completo.")
        relatorio_de_erro = "# Erro na Geração do Relatório Final\n\nA comunicação com a API falhou após múltiplas tentativas."
        return {"relatorio_final_completo": relatorio_de_erro}



# --- Construção do Grafo ---
def decidir_proximo_passo(state: AgentState):
    """Decide se o fluxo deve gerar o plano de testes ou terminar."""
    if state.get("decisao_usuario_plano_testes") == "s":
        return "criar_plano_e_casos"
    else:
        return "fim" # Rota para terminar o grafo

# --- Construção do Grafo ---
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
        "fim": END  # Se a decisão for 'fim', o grafo termina aqui.
    }
)
workflow.add_edge("criador_plano_testes", "gerador_relatorio_completo")
workflow.add_edge("gerador_relatorio_completo", END)

grafo = workflow.compile()