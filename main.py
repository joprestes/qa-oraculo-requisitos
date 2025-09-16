import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any
import time
from google.api_core.exceptions import ResourceExhausted

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

PROMPT_GERAR_RELATORIO_ANALISE  = """
Você é um Escritor Técnico criando um relatório de análise de uma User Story para um time ágil.
Use os dados JSON fornecidos para gerar um relatório claro e bem formatado em Markdown.

**Estrutura do Relatório:**
1. Título: `# Análise da User Story`.
2. Seção `## User Story Analisada`: Apresente a US original.
3. Seção `## 🔍 Análise de Ambiguidade`: Apresente a avaliação geral e a lista de pontos ambíguos.
4. Seção `## ❓ Perguntas para o Product Owner`: Liste as perguntas que o QA deve fazer.
5. Seção `## ✅ Sugestão de Critérios de Aceite`: Liste os ACs sugeridos como uma lista de marcadores.

Use a formatação Markdown para melhorar a legibilidade.
"""

PROMPT_CRIAR_PLANO_DE_TESTES = """
Você é um Engenheiro de QA Sênior, especialista em Estratégia de Testes, BDD e Acessibilidade Web (A11y).
Seu pensamento é crítico, detalhista e focado em encontrar cenários de borda e garantir que a aplicação seja utilizável por todos.
Sua tarefa é usar a User Story e a análise de ambiguidades fornecidas para criar um Plano de Testes conciso e gerar Casos de Teste detalhados e de alta qualidade em formato Gherkin.

**Diretrizes para Casos de Teste:**
- Cubra o caminho feliz.
- Cubra os caminhos negativos e de erro (ex: permissões, dados inválidos).
- Pense em cenários de borda (ex: valores limite, dados vazios, caracteres especiais).
- **Inclua cenários de acessibilidade (ex: navegação por teclado, leitores de tela, contraste de cores).**
- Cada cenário Gherkin deve ser claro, conciso e testar uma única condição.

Sua resposta deve ser APENAS um objeto JSON com a seguinte estrutura:
{
  "plano_de_testes": {
    "objetivo": "O objetivo principal dos testes para esta User Story.",
    "escopo": {
      "dentro_do_escopo": ["Liste aqui o que SERÁ testado."],
      "fora_do_escopo": ["Liste aqui o que NÃO SERÁ testado."]
    },
    "estrategia_de_testes": "Descreva a abordagem.",
    "recursos_necessarios": ["Liste os recursos e a massa de dados necessários."]
  },
  "casos_de_teste_gherkin": [
    {
      "id": "CT-001",
      "titulo": "Um título claro e conciso.",
      "cenario": [
        "Dado que [contexto ou pré-condição].",
        "E [outra pré-condição, se necessário].",
        "Quando [a ação do usuário ocorre].",
        "Então [o resultado observável esperado acontece]."
      ]
    }
  ]
}

**EXEMPLO DE ALTA QUALIDADE PARA UM CASO DE TESTE DE ACESSIBILIDADE:**
Se a US fosse sobre um formulário de login, um bom caso de teste de acessibilidade seria:
{
  "id": "CT-A11Y-01",
  "titulo": "Navegação por teclado no formulário de login",
  "cenario": [
    "Dado que a página de login está completamente carregada",
    "E o foco está no primeiro elemento interativo",
    "Quando eu pressiono a tecla 'Tab' repetidamente",
    "Então o foco deve navegar logicamente por todos os elementos interativos (email, senha, botão 'Entrar', link 'Esqueci minha senha')",
    "E a ordem da navegação deve ser visualmente lógica",
    "E o elemento focado deve ter um indicador visual claro (outline)."
  ]
}
"""

PROMPT_GERAR_RELATORIO_COMPLETO = """
Você é um Escritor Técnico criando um relatório de análise de uma User Story para um time ágil.
Use os dados JSON fornecidos para gerar um relatório COMPLETO em Markdown, combinando a análise inicial com o plano de testes.

**Estrutura do Relatório:**
1. Título: `# Análise da User Story e Plano de Testes`.
2. Seção `## User Story Analisada`: Apresente a US original.
3. Seção `## 🔍 Análise de Ambiguidade`: Apresente a avaliação geral e a lista de pontos ambíguos.
4. Seção `## ❓ Perguntas para o Product Owner`: Liste as perguntas que o QA deve fazer.
5. Seção `## ✅ Sugestão de Critérios de Aceite`: Liste os ACs sugeridos como uma lista de marcadores.
6. Seção `## 📝 Plano de Testes Sugerido`: Apresente o objetivo, escopo, estratégia e recursos.
7. Seção `## 🧪 Casos de Teste (Gherkin)`: Para cada caso de teste, crie um subtítulo `### {id}: {titulo}` e apresente o cenário Gherkin em um bloco de código.

Use a formatação Markdown para melhorar a legibilidade.
"""

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
    
    # --- LÓGICA CORRIGIDA ---
    
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

    # --- LÓGICA ROBUSTA APLICADA AQUI ---
    
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

# --- Execução ---
def main():
    print("--- 🔮 Iniciando Análise de User Story com QA Oráculo ---")
    USER_STORY_EXEMPLO = "Como um usuário premium, eu quero poder exportar meu relatório de atividades para um arquivo CSV, para que eu possa fazer uma análise mais aprofundada em outra ferramenta."
    inputs = {"user_story": USER_STORY_EXEMPLO}
    
    resultado_final = grafo.invoke(inputs)
    
    print("\n--- 🚀 Processo Finalizado ---")
    if "relatorio_final_completo" in resultado_final:
        print("\n--- ✅ Relatório Completo Gerado com Sucesso ---")
        print(resultado_final.get("relatorio_final_completo"))
        print("---------------------------------------------")
    else:
        # Se não gerou o relatório completo, significa que o usuário parou após a análise inicial.
        print("Finalizado após a análise inicial. O relatório foi exibido acima.")

if __name__ == "__main__":
    main()