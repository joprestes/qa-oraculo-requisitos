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
    """
    Recebe o texto bruto da IA e tenta extrair uma string JSON.
    Procura por blocos de código Markdown (```json ... ```) ou JSONs brutos.
    Retorna a string JSON limpa ou None se nada for encontrado.
    """
    match = re.search(r"```json\s*([\s\S]*?)\s*```", texto_resposta)
    if match:
        return match.group(1).strip()
    
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", texto_resposta)
    if match:
        return match.group(0).strip()
        
    return None

# --- CONFIGURAÇÕES GLOBAIS ---
NOME_MODELO = "gemini-1.5-flash"
CONFIG_GERACAO_PADRAO = {"temperature": 0.1}
CONFIG_GERACAO_ESCRITA = {"temperature": 0.25}

# --- Configuração Inicial da API ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Prompts dos Especialistas ---

PROMPT_DIVISAO = """
Sua tarefa é analisar o texto fornecido e dividi-lo em uma lista de requisitos de software individuais e distintos.
Cada item na sua resposta deve ser um requisito completo e autocontido.
Responda APENAS com uma lista em formato JSON, onde cada item da lista é uma string contendo um requisito.
NÃO adicione nenhum texto introdutório ou formatação extra. Sua resposta deve começar com '[' e terminar com ']'.
"""

PROMPT_ANALISE_INDIVIDUAL = """
Você é um Analista de QA Sênior, especialista em Engenharia de Requisitos.
Sua tarefa é analisar UM único requisito de software e retornar uma avaliação detalhada em formato JSON.
Regras:
1. Seja Cético: Procure ativamente por ambiguidades, omissões e termos vagos.
2. Seja Construtivo: Sugira Critérios de Aceitação claros no formato "Dado-Quando-Então".
3. Pense em Riscos: Identifique riscos potenciais em categorias como: Funcional, Performance, Segurança, Usabilidade.
Formato de Saída JSON Obrigatório:
{
  "avaliacao_qualidade": {
    "clareza": "CLARO|AMBÍGUO|INCOMPLETO",
    "pontos_fortes": "Descreva o que está bem definido.",
    "pontos_ambiguos": ["Liste os termos ou frases vagas."],
    "sugestao_melhoria": "Ofereça uma sugestão de como reescrever o requisito."
  },
  "sugestao_criterios_aceite": ["Dado [contexto], Quando [ação], Então [resultado]."],
  "riscos_sugeridos": ["CATEGORIA: Descrição do risco."]
}
"""

PROMPT_ANALISE_CRUZADA = """
Você é um Arquiteto de Software Sênior. Sua tarefa é analisar uma lista de requisitos e identificar
quaisquer CONTRADIÇÕES lógicas ou SOBREPOSIÇÕES (funcionalidades duplicadas) entre eles.
Sua resposta deve ser APENAS uma lista de objetos JSON. Se nenhum problema for encontrado, retorne uma lista vazia [].
A estrutura de cada objeto de problema deve ser:
{
  "tipo": "CONTRADIÇÃO" | "SOBREPOSIÇÃO",
  "descricao": "Uma explicação clara do problema.",
  "ids_envolvidos": [lista_de_IDs_dos_requisitos_com_problema]
}
"""

PROMPT_GERAR_RELATORIO = """
Você é um Escritor Técnico criando um relatório de análise de requisitos.
Use os dados JSON fornecidos para gerar um relatório em formato Markdown.
Estrutura:
1. Título: `# Relatório de Análise do Oráculo de Requisitos`.
2. Seção `## Resumo Geral`: Um parágrafo resumindo os achados.
3. Seção `## Análise de Contradições e Sobreposições`: Liste os problemas (❌ para contradições, ⚠️ para sobreposições) ou diga "Nenhum problema encontrado.".
4. Seção `## Análise Detalhada dos Requisitos`: Para cada requisito:
   - Use um subtítulo `### Requisito {id}: {texto do requisito}`.
   - Apresente a análise de forma clara e organizada.
Use a formatação Markdown para melhorar a legibilidade.
"""


# --- Estado do Agente (AgentState) ---

class AgentState(TypedDict):
    texto_bruto: str
    requisitos_individuais: List[Dict[str, Any]]
    analise_cruzada: List[Dict[str, Any]]
    relatorio_final: str

# --- Nós do Grafo ---

def node_dividir_requisitos(state: AgentState) -> AgentState:
    """Nó 1: Usa a IA para dividir o texto bruto do usuário em uma lista de requisitos."""
    print("--- Executando Nó: Dividir Requisitos (com IA) ---")
    texto = state["texto_bruto"]
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_PADRAO)
    prompt_completo = f"{PROMPT_DIVISAO}\n\nTexto para dividir:\n---\n{texto}"
    response = model.generate_content(prompt_completo)
    
    lista_requisitos = []
    json_limpo = extrair_json_da_resposta(response.text)
    
    if json_limpo:
        try:
            lista_requisitos = json.loads(json_limpo)
            if not isinstance(lista_requisitos, list):
                lista_requisitos = []
        except json.JSONDecodeError:
            pass
            
    if not lista_requisitos:
        print("⚠️ Usando divisão simples como fallback.")
        lista_requisitos = [req.strip() for req in texto.split('\n\n') if req.strip()]

    requisitos_formatados = [{"id": i + 1, "texto": texto} for i, texto in enumerate(lista_requisitos)]
    print(f"Divisão concluída. Encontrados {len(requisitos_formatados)} requisitos.")
    
    return {"requisitos_individuais": requisitos_formatados}

def node_analise_individual(state: AgentState) -> AgentState:
    """Nó 2: Itera sobre cada requisito e usa a IA para realizar a análise de qualidade."""
    print("--- Executando Nó: Análise Individual (com IA) ---")
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_PADRAO)
    requisitos_analisados = []
    
    for req in state["requisitos_individuais"]:
        print(f"Analisando requisito {req['id']}: '{req['texto'][:50]}...'")
        
        prompt_completo = f"{PROMPT_ANALISE_INDIVIDUAL}\n\nRequisito para Análise:\n---\n{req['texto']}"
        response = model.generate_content(prompt_completo)
        
        json_limpo = extrair_json_da_resposta(response.text)
        
        if json_limpo:
            try:
                req['analise'] = json.loads(json_limpo)
            except json.JSONDecodeError:
                req['analise'] = {"erro": "Falha ao decodificar o JSON da análise."}
        else:
            req['analise'] = {"erro": "Nenhum JSON retornado pela IA."}
            
        requisitos_analisados.append(req)

    return {"requisitos_individuais": requisitos_analisados}

def node_analise_cruzada(state: AgentState) -> AgentState:
    """Nó 3: Compara todos os requisitos para encontrar contradições."""
    print("--- Executando Nó: Análise Cruzada (com IA) ---")
    
    requisitos_para_comparacao = [{"id": req["id"], "texto": req["texto"]} for req in state["requisitos_individuais"]]
    requisitos_str = json.dumps(requisitos_para_comparacao, indent=2, ensure_ascii=False)
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_PADRAO)
    prompt_completo = f"{PROMPT_ANALISE_CRUZADA}\n\nLista de Requisitos para Análise:\n---\n{requisitos_str}"
    response = model.generate_content(prompt_completo)
    
    analise_final = []
    json_limpo = extrair_json_da_resposta(response.text)
    
    if json_limpo:
        try:
            analise_final = json.loads(json_limpo)
        except json.JSONDecodeError:
            print("⚠️ Alerta: JSON inválido retornado pela análise cruzada.")
            pass
            
    return {"analise_cruzada": analise_final}

def node_gerar_relatorio(state: AgentState) -> AgentState:
    """Nó 4: Consolida todas as informações em um relatório final em Markdown."""
    print("--- Executando Nó: Gerar Relatório Final (com IA) ---")
    
    contexto_completo = {
        "analise_individual": state["requisitos_individuais"],
        "analise_cruzada": state["analise_cruzada"]
    }
    contexto_str = json.dumps(contexto_completo, indent=2, ensure_ascii=False)
    
    model = genai.GenerativeModel(NOME_MODELO, generation_config=CONFIG_GERACAO_ESCRITA)
    prompt_completo = f"{PROMPT_GERAR_RELATORIO}\n\nDados para o Relatório:\n---\n{contexto_str}"
    response = model.generate_content(prompt_completo)
    
    return {"relatorio_final": response.text}

# --- Construção do Grafo ---
workflow = StateGraph(AgentState)

workflow.add_node("divisor", node_dividir_requisitos)
workflow.add_node("analista_individual", node_analise_individual)
workflow.add_node("analista_cruzado", node_analise_cruzada)
workflow.add_node("gerador_relatorio", node_gerar_relatorio)

workflow.add_edge(START, "divisor")
workflow.add_edge("divisor", "analista_individual")
workflow.add_edge("analista_individual", "analista_cruzado")
workflow.add_edge("analista_cruzado", "gerador_relatorio")
workflow.add_edge("gerador_relatorio", END)

grafo = workflow.compile()

# --- Execução ---
if __name__ == "__main__":
    print("--- 🔮 Bem-vindo ao QA Oráculo de Requisitos (v2 - LangGraph) ---")
    
    REQUISITOS_EXEMPLO = """
    Como usuário, quero poder me cadastrar usando email e senha, com a senha tendo no mínimo 6 caracteres.
    Como administrador, quero poder ver a lista de todos os usuários.
    Como usuário de segurança, a política de senhas da empresa exige que todas as senhas tenham no mínimo 10 caracteres.
    """
    
    inputs = {"texto_bruto": REQUISITOS_EXEMPLO}
    resultado_final = grafo.invoke(inputs)
    
    print("\n--- Relatório Final ---")
    print(resultado_final.get("relatorio_final", "Nenhum relatório foi gerado."))
    print("---------------------")