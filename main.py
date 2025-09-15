import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any
import json
import re

# --- Imports do LangGraph ---
from langgraph.graph import StateGraph, START, END


def extrair_json_da_resposta(texto_resposta: str) -> str | None:
    """
    Recebe o texto bruto da IA e tenta extrair uma string JSON.
    Procura por blocos de código Markdown (```json ... ```).
    Retorna a string JSON limpa ou None se nada for encontrado.
    """
    # Procura por blocos de código Markdown JSON
    match = re.search(r"```json\s*([\s\S]*?)\s*```", texto_resposta)
    if match:
        return match.group(1).strip()
    
    # Se não encontrar bloco de código, procura por um JSON que comece com '{' ou '['
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", texto_resposta)
    if match:
        return match.group(0).strip()
        
    return None # Retorna None se nenhum padrão JSON for encontrado
# --- Configuração Inicial ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- 1. O Blueprint: Definindo o Estado do Agente (AgentState) ---
# Esta é a "memória" do nosso fluxo. Cada nó que executarmos poderá ler e escrever
# informações neste dicionário, passando o estado para o próximo passo.

class AgentState(TypedDict):
    texto_bruto: str                             # O input inicial do usuário com todos os requisitos
    requisitos_individuais: List[Dict[str, Any]] # Uma lista, onde cada item é um requisito analisado
    analise_cruzada: List[Dict[str, Any]]        # O resultado da análise de contradições/sobreposições
    relatorio_final: str                         # O relatório em Markdown pronto para ser exibido

# --- 1.5. O Cérebro do Oráculo: Os Prompts dos Especialistas ---

PROMPT_DIVISAO = """
Sua tarefa é analisar o texto fornecido e dividi-lo em uma lista de requisitos de software individuais e distintos.
Cada item na sua resposta deve ser um requisito completo e autocontido.
Responda APENAS com uma lista em formato JSON, onde cada item da lista é uma string contendo um requisito.

Exemplo de Saída:
["Como usuário, quero poder me cadastrar usando email e senha.", "A senha deve ter no mínimo 8 caracteres."]

NÃO adicione nenhum texto introdutório ou formatação extra. Sua resposta deve começar com '[' e terminar com ']'.
"""

PROMPT_ANALISE_INDIVIDUAL = """
Você é um Analista de QA Sênior, especialista em Engenharia de Requisitos.
Sua tarefa é analisar UM único requisito de software e retornar uma avaliação detalhada e estruturada em formato JSON.

**Regras:**
1.  **Seja Cético:** Procure ativamente por ambiguidades, omissões e termos vagos (como "rápido", "fácil", "seguro", "melhorar").
2.  **Seja Construtivo:** Se os Critérios de Aceitação estiverem faltando ou forem fracos, sugira exemplos claros no formato "Dado-Quando-Então".
3.  **Pense em Riscos:** Com base no requisito, identifique riscos potenciais em categorias como: Funcional, Performance, Segurança, Usabilidade.

**Formato de Saída JSON Obrigatório:**
Sua resposta DEVE ser um objeto JSON único, sem formatação extra ou texto introdutório.
O JSON deve ter a seguinte estrutura:
{
  "avaliacao_qualidade": {
    "clareza": "CLARO|AMBÍGUO|INCOMPLETO",
    "pontos_fortes": "Descreva o que está bem definido no requisito.",
    "pontos_ambiguos": ["Liste os termos ou frases vagas encontradas."],
    "sugestao_melhoria": "Ofereça uma sugestão de como o requisito poderia ser reescrito para ser mais objetivo."
  },
  "sugestao_criterios_aceite": [
    "Dado [contexto], Quando [ação], Então [resultado esperado]."
  ],
  "riscos_sugeridos": ["CATEGORIA: Descrição do risco."]
}
"""


PROMPT_ANALISE_CRUZADA = """
Você é um Arquiteto de Software Sênior. Sua tarefa é analisar uma lista de requisitos de software e identificar
quaisquer CONTRADIÇÕES lógicas ou SOBREPOSIÇÕES (funcionalidades duplicadas) entre eles.

Analise a lista de objetos JSON de requisitos fornecida abaixo. Cada objeto tem um 'id' e um 'texto'.

Sua resposta deve ser APENAS uma lista de objetos JSON, onde cada objeto representa um problema encontrado.
Se nenhum problema for encontrado, retorne uma lista vazia [].

A estrutura de cada objeto de problema deve ser:
{
  "tipo": "CONTRADIÇÃO" | "SOBREPOSIÇÃO",
  "descricao": "Uma explicação clara e concisa do problema encontrado.",
  "ids_envolvidos": [lista_de_IDs_dos_requisitos_com_problema]
}

NÃO adicione nenhum texto introdutório. Sua resposta deve começar com '[' e terminar com ']'.
"""


PROMPT_GERAR_RELATORIO = """
Você é um Escritor Técnico encarregado de criar um relatório de análise de requisitos claro e conciso.
Seu público são gerentes de produto, desenvolvedores e QAs. Use uma linguagem profissional, mas acessível.

Use os dados JSON fornecidos abaixo, que contêm a análise individual de cada requisito e uma análise cruzada de contradições e sobreposições, para gerar um relatório em formato Markdown.

**Estrutura do Relatório:**
1.  Comece com o título: `# Relatório de Análise do Oráculo de Requisitos`.
2.  Crie uma seção `## Resumo Geral` com um ou dois parágrafos resumindo os achados mais importantes.
3.  Crie uma seção `## Análise de Contradições e Sobreposições`. Se houver problemas, liste-os com emojis (❌ para contradições, ⚠️ para sobreposições). Se não houver, diga "Nenhum problema encontrado.".
4.  Crie uma seção `## Análise Detalhada dos Requisitos`. Para cada requisito:
    -   Use um subtítulo `### Requisito {id}: {texto do requisito}`.
    -   Liste os pontos fortes e os pontos ambíguos.
    -   Apresente a sugestão de melhoria e os critérios de aceite sugeridos.
    -   Liste os riscos identificados.

Seja bem organizado e use a formatação Markdown (títulos, negrito, listas) para melhorar a legibilidade.
"""


# --- 2. As Ferramentas: Definindo os Nós do Grafo ---
# Cada função abaixo representa uma etapa no nosso pipeline de análise.

def node_dividir_requisitos(state: AgentState) -> AgentState:
    """
    Nó 1: Pega o texto bruto do usuário e usa a IA para dividi-lo em uma lista de requisitos.
    """
    print("--- Executando Nó: Dividir Requisitos (com IA) ---")
    texto = state["texto_bruto"]
    
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.1})
    prompt_completo = f"{PROMPT_DIVISAO}\n\nTexto para dividir:\n---\n{texto}"
    response = model.generate_content(prompt_completo)
    
    lista_requisitos = []
    json_limpo = extrair_json_da_resposta(response.text)
    
    if json_limpo:
        try:
            lista_requisitos = json.loads(json_limpo)
            if not isinstance(lista_requisitos, list):
                print("⚠️ Alerta: A IA retornou um JSON que não é uma lista. Usando fallback.")
                lista_requisitos = [] # Reseta para acionar o fallback
        except json.JSONDecodeError:
            print("⚠️ Alerta: JSON inválido na divisão, mesmo após a limpeza. Usando fallback.")
            # Não faz nada, o fallback será acionado
            pass
            
    # Se a lista estiver vazia (seja por falha da IA ou do JSON), usa o fallback
    if not lista_requisitos:
        print("Usando divisão simples como fallback.")
        lista_requisitos = [req.strip() for req in texto.split('\n\n') if req.strip()]

    requisitos_formatados = [{"id": i + 1, "texto": texto} for i, texto in enumerate(lista_requisitos)]
    print(f"Divisão concluída. Encontrados {len(requisitos_formatados)} requisitos.")
    
    return {"requisitos_individuais": requisitos_formatados}


def node_analise_individual(state: AgentState) -> AgentState:
    """
    Nó 2: Itera sobre cada requisito e usa a IA para realizar a análise de qualidade.
    """
    print("--- Executando Nó: Análise Individual (com IA) ---")
    requisitos_para_analisar = state["requisitos_individuais"]
    
    model = genai.GenerativeModel('gemini-1.5-flash',generation_config={"temperature": 0.1})
    requisitos_analisados = []
    
    for req in requisitos_para_analisar:
        print(f"Analisando requisito {req['id']}: '{req['texto'][:50]}...'")
        
        prompt_completo = f"{PROMPT_ANALISE_INDIVIDUAL}\n\nRequisito para Análise:\n---\n{req['texto']}"
        response = model.generate_content(prompt_completo)
        
        json_limpo = extrair_json_da_resposta(response.text)
        
        if json_limpo:
            try:
                analise_json = json.loads(json_limpo)
                req['analise'] = analise_json
            except json.JSONDecodeError:
                print(f"⚠️ Alerta: JSON inválido para o requisito {req['id']} mesmo após a limpeza.")
                req['analise'] = {"erro": "Falha ao decodificar o JSON da análise."}
        else:
            print(f"⚠️ Alerta: Nenhum JSON encontrado na resposta da IA para o requisito {req['id']}.")
            req['analise'] = {"erro": "Nenhum JSON retornado pela IA."}
            
        requisitos_analisados.append(req)

    return {"requisitos_individuais": requisitos_analisados}


def node_analise_cruzada(state: AgentState) -> AgentState:
    """
    Nó 3: Compara todos os requisitos analisados para encontrar contradições.
    """
    print("--- Executando Nó: Análise Cruzada (com IA) ---")
    
    # Prepara os dados para a IA, enviando apenas o essencial (ID e Texto)
    requisitos_para_comparacao = [
        {"id": req["id"], "texto": req["texto"]} 
        for req in state["requisitos_individuais"]
    ]
    
    # Converte a lista de dicionários em uma string formatada para o prompt
    requisitos_str = json.dumps(requisitos_para_comparacao, indent=2, ensure_ascii=False)
    
    model = genai.GenerativeModel('gemini-1.5-flash',generation_config={"temperature": 0.1})
    
    prompt_completo = f"{PROMPT_ANALISE_CRUZADA}\n\nLista de Requisitos para Análise:\n---\n{requisitos_str}"
    
    response = model.generate_content(prompt_completo)
    
    analise_final = []
    json_limpo = extrair_json_da_resposta(response.text)
    
    if json_limpo:
        try:
            analise_final = json.loads(json_limpo)
        except json.JSONDecodeError:
            print("⚠️ Alerta: JSON inválido retornado pela análise cruzada.")
            # Se falhar, a análise cruzada simplesmente ficará vazia
            pass
            
    return {"analise_cruzada": analise_final}


def node_gerar_relatorio(state: AgentState) -> AgentState:
    """
    Nó 4: Consolida todas as informações em um relatório final em Markdown.
    """
    print("--- Executando Nó: Gerar Relatório Final (com IA) ---")
    
    # Prepara todo o contexto coletado para ser enviado à IA
    contexto_completo = {
        "analise_individual": state["requisitos_individuais"],
        "analise_cruzada": state["analise_cruzada"]
    }
    
    # Converte o dicionário de contexto em uma string JSON formatada
    contexto_str = json.dumps(contexto_completo, indent=2, ensure_ascii=False)
    
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"temperature": 0.2} # Um pouco mais de criatividade para escrita
    )
    
    prompt_completo = f"{PROMPT_GERAR_RELATORIO}\n\nDados para o Relatório:\n---\n{contexto_str}"
    
    response = model.generate_content(prompt_completo)
    
    return {"relatorio_final": response.text}

# --- 3. A Montagem: Construindo e Compilando o Grafo ---
workflow = StateGraph(AgentState)

# Adicionando os nós ao nosso workflow
workflow.add_node("divisor", node_dividir_requisitos)
workflow.add_node("analista_individual", node_analise_individual)
workflow.add_node("analista_cruzado", node_analise_cruzada)
workflow.add_node("gerador_relatorio", node_gerar_relatorio)

# Definindo as conexões (nosso pipeline linear)
workflow.add_edge(START, "divisor")
workflow.add_edge("divisor", "analista_individual")
workflow.add_edge("analista_individual", "analista_cruzado")
workflow.add_edge("analista_cruzado", "gerador_relatorio")
workflow.add_edge("gerador_relatorio", END)

# Compila o workflow em um objeto executável
grafo = workflow.compile()


# --- 4. A Execução: Rodando o Oráculo ---
if __name__ == "__main__":
    print("--- 🔮 Bem-vindo ao QA Oráculo de Requisitos (v2 - LangGraph) ---")
    
    REQUISITOS_EXEMPLO = """
    Como usuário, quero poder me cadastrar usando email e senha, com a senha tendo no mínimo 6 caracteres.

    Como administrador, quero poder ver a lista de todos os usuários.

    Como usuário de segurança, a política de senhas da empresa exige que todas as senhas tenham no mínimo 10 caracteres.
    """
    
    # O input inicial para o nosso grafo
    inputs = {"texto_bruto": REQUISITOS_EXEMPLO}
    
    # Invoca o grafo e executa o pipeline completo
    resultado_final = grafo.invoke(inputs)
    
    # Mostra o relatório final gerado pelo último nó
    print("\n--- Relatório Final ---")
    print(resultado_final.get("relatorio_final", "Nenhum relatório foi gerado."))
    print("---------------------")