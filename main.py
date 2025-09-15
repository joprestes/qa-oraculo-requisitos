import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any

# --- Imports do LangGraph ---
from langgraph.graph import StateGraph, START, END

# --- Funções Auxiliares ---

def extrair_json_da_resposta(texto_resposta: str) -> str | None:
    """Extrai uma string JSON de dentro de um texto bruto, limpando formatação Markdown."""
    match = re.search(r"```json\s*([\s\S]*?)\s*```", texto_resposta)
    if match:
        return match.group(1).strip()
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", texto_resposta)
    if match:
        return match.group(0).strip()
    return None

# --- CONFIGURAÇÕES GLOBAIS ---
NOME_MODELO = "gemini-1.5-flash"
CONFIG_GERACAO_ANALISE = {"temperature": 0.2}
CONFIG_GERACAO_RELATORIO = {"temperature": 0.3}

# --- Configuração Inicial da API ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Prompts dos Especialistas ---

PROMPT_ANALISE_US = """
Você é um Analista de QA Sênior com vasta experiência em metodologias ágeis e um profundo entendimento de negócios.
Sua tarefa é analisar a User Story (US) a seguir e fornecer um feedback estruturado para o QA do time.
A análise deve ser completa, cética e focada em garantir que a história seja testável e que todas as ambiguidades sejam resolvidas ANTES do desenvolvimento começar.
Para a User Story fornecida, sua resposta deve ser APENAS um objeto JSON com a seguinte estrutura:
{
  "analise_ambiguidade": {
    "avaliacao_geral": "Uma avaliação de 1 a 2 frases sobre a clareza da US.",
    "pontos_ambiguos": ["Liste aqui cada ponto vago, termo subjetivo (ex: 'rápido', 'fácil'), ou informação faltante que você encontrou."]
  },
  "perguntas_para_po": ["Formule uma lista de perguntas claras e específicas que o QA deve fazer ao Product Owner (PO) para esclarecer cada um dos pontos ambíguos. As perguntas devem ser acionáveis."],
  "sugestao_criterios_aceite": [
    "Com base no seu entendimento da US, escreva uma lista inicial de Critérios de Aceite (ACs) em formato de lista simples e direta. Cada critério deve ser uma afirmação verificável."]
}
NÃO adicione nenhum texto introdutório. Sua resposta deve começar com '{' e terminar com '}'.
"""

PROMPT_GERAR_RELATORIO_US = """
Você é um Escritor Técnico criando um relatório de análise de uma User Story para um time ágil.
Use os dados JSON fornecidos para gerar um relatório claro e bem formatado em Markdown.
Estrutura do Relatório:
1. Título: `# Análise da User Story`.
2. Seção `## User Story Analisada`: Apresente a US original.
3. Seção `## 🔍 Análise de Ambiguidade`: Apresente a avaliação geral e a lista de pontos ambíguos.
4. Seção `## ❓ Perguntas para o Product Owner`: Liste as perguntas que o QA deve fazer. Esta é a seção mais importante, destaque-a.
5. Seção `## ✅ Sugestão de Critérios de Aceite`: Liste os ACs sugeridos como uma lista de marcadores (bullet points).
Use a formatação Markdown para melhorar a legibilidade.
"""

# --- Estado do Agente (AgentState) Simplificado ---

class AgentState(TypedDict):
    user_story: str
    analise_da_us: Dict[str, Any]
    relatorio_final: str

# --- Nós do Grafo Simplificado ---

def node_analisar_historia(state: AgentState) -> AgentState:
    """Nó 1: Pega a User Story e usa a IA para gerar a análise completa."""
    print("--- Etapa 1: Analisando a User Story... ---")
    us = state["user_story"]
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ANALISE)
    prompt_completo = f"{PROMPT_ANALISE_US}\n\nUser Story para Análise:\n---\n{us}"
    response = model.generate_content(prompt_completo)
    
    analise_json = {}
    json_limpo = extrair_json_da_resposta(response.text)
    
    if json_limpo:
        try:
            analise_json = json.loads(json_limpo)
        except json.JSONDecodeError:
            print("⚠️ Alerta: JSON inválido retornado pela análise da US.")
            analise_json = {"erro": "Falha ao decodificar o JSON da análise."}
    else:
        print("⚠️ Alerta: Nenhum JSON retornado pela IA para a análise.")
        analise_json = {"erro": "Nenhum JSON retornado pela IA."}
        
    return {"analise_da_us": analise_json}

def node_gerar_relatorio(state: AgentState) -> AgentState:
    """Nó 2: Consolida a análise em um relatório final em Markdown."""
    print("--- Etapa 2: Compilando o relatório de análise ---")
    
    contexto_completo = {
        "user_story_original": state["user_story"],
        "analise": state["analise_da_us"]
    }
    contexto_str = json.dumps(contexto_completo, indent=2, ensure_ascii=False)
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_RELATORIO)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_US}\n\nDados para o Relatório:\n---\n{contexto_str}"
    response = model.generate_content(prompt_completo)
    
    return {"relatorio_final": response.text}

# --- Construção do Grafo ---
workflow = StateGraph(AgentState)

workflow.add_node("analista_us", node_analisar_historia)
workflow.add_node("gerador_relatorio", node_gerar_relatorio)

workflow.add_edge(START, "analista_us")
workflow.add_edge("analista_us", "gerador_relatorio")
workflow.add_edge("gerador_relatorio", END)

grafo = workflow.compile()

# --- Execução ---

def main():
    """Função principal que executa o workflow do Oráculo."""
    print("--- 🔮 Iniciando Análise de User Story com QA Oráculo ---")
    
    USER_STORY_EXEMPLO = "Como um usuário premium, eu quero poder exportar meu relatório de atividades para um arquivo CSV, para que eu possa fazer uma análise mais aprofundada em outra ferramenta."
    
    inputs = {"user_story": USER_STORY_EXEMPLO}
    resultado_final = grafo.invoke(inputs)
    
    print("\n--- ✅ Relatório de Análise Gerado com Sucesso ---")
    print(resultado_final.get("relatorio_final", "Nenhum relatório foi gerado."))
    print("---------------------------------------------")


if __name__ == "__main__":
    main()