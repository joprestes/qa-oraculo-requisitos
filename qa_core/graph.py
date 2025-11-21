# Implementação dos grafos de estados usando LangGraph e provedores LLM configuráveis

import logging
import json
import time
from typing import Any, NotRequired, TypedDict

import streamlit as st
from langgraph.graph import END, StateGraph

from .config import CONFIG_GERACAO_ANALISE, CONFIG_GERACAO_RELATORIO
from .text_utils import extract_json_from_text
from .llm import LLMSettings, get_llm_client
from .llm.providers.base import LLMClient, LLMError, LLMRateLimitError
from .prompts import (
    PROMPT_ANALISE_US,
    PROMPT_CRIAR_PLANO_DE_TESTES,
    PROMPT_GERAR_RELATORIO_ANALISE,
    PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES,
)
from .observability import log_graph_event

logger = logging.getLogger(__name__)


# --- Funções Auxiliares e Estrutura de Dados ---
_llm_client: LLMClient | None = None


def _get_llm_client() -> LLMClient:
    """Obtém ou cria uma instância singleton do cliente LLM.

    Carrega as configurações do ambiente (.env) e cria um cliente LLM
    apropriado para o provedor configurado (Google, Azure, OpenAI, etc.).
    A instância é cacheada globalmente para reutilização.

    Returns:
        LLMClient: Cliente LLM configurado e pronto para uso.

    Raises:
        LLMError: Se as configurações estiverem inválidas ou o provedor
            não estiver disponível.
    """
    global _llm_client
    if _llm_client is None:
        settings = LLMSettings.from_env()
        _llm_client = get_llm_client(settings)
    return _llm_client


def chamar_modelo_com_retry(
    client: LLMClient,
    prompt_completo: str,
    tentativas: int = 3,
    espera: int = 60,
    *,
    config: dict[str, Any] | None = None,
    trace_id: str | None = None,
    node: str | None = None,
):
    """Chama o modelo LLM com lógica de retry automático.

    Encapsula a chamada à API do LLM com retry automático para lidar com
    limites de taxa (rate limiting) e erros temporários. Registra eventos
    de observabilidade para cada tentativa.

    Args:
        client: Cliente LLM configurado para fazer a chamada.
        prompt_completo: Prompt completo a ser enviado ao modelo.
        tentativas: Número máximo de tentativas em caso de falha. Padrão: 3.
        espera: Tempo de espera em segundos entre tentativas. Padrão: 60.
        config: Configurações adicionais para a geração (temperatura, etc.).
        trace_id: ID de rastreamento para correlação de logs.
        node: Nome do nó do grafo que está fazendo a chamada.

    Returns:
        Resposta do modelo LLM, ou None em caso de falha após todas as tentativas.

    Raises:
        Não lança exceções diretamente, retorna None em caso de erro.

    Note:
        - Em caso de LLMRateLimitError, aguarda o tempo especificado antes de retry.
        - Em caso de LLMError ou exceções genéricas, retorna None imediatamente.
        - Todos os eventos são registrados via log_graph_event para observabilidade.
    """
    log_graph_event(
        "model.call.start",
        trace_id=trace_id,
        node=node,
        payload={"tentativas": tentativas},
    )
    started_at = time.perf_counter()
    for tentativa in range(tentativas):
        tentativa_at = time.perf_counter()
        try:
            resposta = client.generate_content(
                prompt_completo,
                config=config,
                trace_id=trace_id,
                node=node,
            )
            log_graph_event(
                "model.call.success",
                trace_id=trace_id,
                node=node,
                payload={
                    "tentativa": tentativa + 1,
                    "duracao_ms": round((time.perf_counter() - tentativa_at) * 1000, 2),
                    "tempo_total_ms": round(
                        (time.perf_counter() - started_at) * 1000, 2
                    ),
                },
            )
            return resposta
        except LLMRateLimitError:
            print(
                f"⚠️ Limite de Requisições (Tentativa {tentativa + 1}/{tentativas}). Aguardando {espera}s..."
            )
            log_graph_event(
                "model.call.rate_limited",
                trace_id=trace_id,
                node=node,
                payload={
                    "tentativa": tentativa + 1,
                    "espera_s": espera,
                },
                level=logging.WARNING,
            )
            if tentativa < tentativas - 1:
                time.sleep(espera)
            else:
                logger.error("Esgotado o número de tentativas após rate limiting")
        except LLMError as e:
            logger.error(f"Erro ao chamar provedor LLM: {e}", exc_info=True)
            log_graph_event(
                "model.call.error",
                trace_id=trace_id,
                node=node,
                payload={
                    "tentativa": tentativa + 1,
                    "erro": repr(e),
                },
                level=logging.ERROR,
            )
            return None
        except Exception as e:  # pragma: no cover - salvaguarda final
            logger.error(f"Erro inesperado na comunicação com LLM: {e}", exc_info=True)
            log_graph_event(
                "model.call.error",
                trace_id=trace_id,
                node=node,
                payload={
                    "tentativa": tentativa + 1,
                    "erro": repr(e),
                },
                level=logging.ERROR,
            )
            return None
    log_graph_event(
        "model.call.failed",
        trace_id=trace_id,
        node=node,
        payload={
            "tentativas": tentativas,
            "tempo_total_ms": round((time.perf_counter() - started_at) * 1000, 2),
        },
        level=logging.ERROR,
    )
    return None


class AgentState(TypedDict):
    """Define a estrutura de estado que flui através dos grafos."""

    user_story: str
    analise_da_us: dict[str, Any]
    relatorio_analise_inicial: str
    plano_e_casos_de_teste: dict[str, Any]
    relatorio_plano_de_testes: str
    trace_id: NotRequired[str]


# --- Nós do Grafo ---
def node_analisar_historia(state: AgentState) -> AgentState:
    """Nó do grafo que analisa a User Story fornecida.

    Primeiro nó do grafo de análise. Envia a User Story para o LLM com um
    prompt especializado e retorna uma análise estruturada em JSON contendo:
    - Avaliação de ambiguidades
    - Pontos de atenção
    - Riscos identificados
    - Critérios de aceite sugeridos
    - Perguntas para o Product Owner

    Args:
        state: Estado atual do grafo contendo:
            - user_story: Texto da User Story a ser analisada.
            - trace_id (opcional): ID para rastreamento de logs.

    Returns:
        Dicionário com a chave 'analise_da_us' contendo a análise estruturada
        em formato JSON, ou um dicionário com chave 'erro' em caso de falha.

    Note:
        Registra eventos de observabilidade (node.start, node.finish, node.error)
        para monitoramento e debugging.
    """
    print("--- Etapa 1: Analisando a User Story... ---")
    trace_id = state.get("trace_id")
    node_name = "analista_us"
    log_graph_event(
        "node.start",
        trace_id=trace_id,
        node=node_name,
        payload={"user_story_len": len(state.get("user_story", ""))},
    )
    started_at = time.perf_counter()
    us = state["user_story"]
    client = _get_llm_client()
    prompt_completo = f"{PROMPT_ANALISE_US}\n\nUser Story para Análise:\n---\n{us}"
    response = chamar_modelo_com_retry(
        client,
        prompt_completo,
        config=CONFIG_GERACAO_ANALISE,
        trace_id=trace_id,
        node=node_name,
    )

    if not response or not response.text:
        log_graph_event(
            "node.error",
            trace_id=trace_id,
            node=node_name,
            payload={"motivo": "resposta_vazia"},
            level=logging.ERROR,
        )
        return {
            "analise_da_us": {"erro": "Falha na comunicação com o serviço de análise."}
        }

    try:
        # Tenta decodificar diretamente, pois `response_mime_type` deve garantir JSON puro
        analise_json = json.loads(response.text)
    except json.JSONDecodeError:
        # Se falhar, tenta limpar a string como um fallback de segurança
        json_limpo = extract_json_from_text(response.text)
        if json_limpo:
            try:
                analise_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                analise_json = {
                    "erro": f"Falha ao decodificar a resposta da análise. Resposta recebida: {response.text}"
                }
        else:
            analise_json = {
                "erro": f"Nenhum dado estruturado encontrado na resposta. Resposta recebida: {response.text}"
            }

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    log_graph_event(
        "node.finish",
        trace_id=trace_id,
        node=node_name,
        payload={"duracao_ms": duration_ms, "tem_erro": "erro" in analise_json},
    )
    return {"analise_da_us": analise_json}


def node_gerar_relatorio_analise(state: AgentState) -> AgentState:
    """Nó do grafo que gera o relatório Markdown da análise.

    Segundo nó do grafo de análise. Recebe a análise estruturada (JSON) e
    gera um relatório em formato Markdown legível e bem formatado para
    apresentação ao usuário.

    Args:
        state: Estado atual do grafo contendo:
            - user_story: Texto original da User Story.
            - analise_da_us: Análise estruturada em JSON.
            - trace_id (opcional): ID para rastreamento de logs.

    Returns:
        Dicionário com a chave 'relatorio_analise_inicial' contendo o
        relatório em formato Markdown, ou mensagem de erro em caso de falha.

    Note:
        Utiliza PROMPT_GERAR_RELATORIO_ANALISE e CONFIG_GERACAO_RELATORIO
        para controlar a geração do relatório.
    """
    print("--- Etapa 2: Compilando relatório de análise... ---")
    trace_id = state.get("trace_id")
    node_name = "gerador_relatorio_analise"
    log_graph_event("node.start", trace_id=trace_id, node=node_name)
    started_at = time.perf_counter()
    contexto = {
        "user_story_original": state["user_story"],
        "analise": state.get("analise_da_us", {}),
    }
    contexto_str = json.dumps(contexto, indent=2, ensure_ascii=False)
    client = _get_llm_client()
    prompt_completo = f"{PROMPT_GERAR_RELATORIO_ANALISE}\n\nDados:\n---\n{contexto_str}"
    response = chamar_modelo_com_retry(
        client,
        prompt_completo,
        config=CONFIG_GERACAO_RELATORIO,
        trace_id=trace_id,
        node=node_name,
    )
    resultado = {
        "relatorio_analise_inicial": (
            response.text
            if response and response.text
            else "# Erro na Geração do Relatório"
        )
    }
    log_graph_event(
        "node.finish",
        trace_id=trace_id,
        node=node_name,
        payload={"duracao_ms": round((time.perf_counter() - started_at) * 1000, 2)},
    )
    return resultado


def node_criar_plano_e_casos_de_teste(state: AgentState) -> AgentState:
    """Nó do grafo que cria o plano de testes e cenários Gherkin.

    Primeiro nó do grafo de plano de testes. Recebe a análise da User Story
    e gera um plano de testes estruturado contendo:
    - Objetivo e escopo do plano
    - Estratégia de testes
    - Cenários de teste em formato Gherkin (Given-When-Then)
    - Priorização e justificativas de acessibilidade

    Args:
        state: Estado atual do grafo contendo:
            - user_story: Texto original da User Story.
            - analise_da_us: Análise estruturada da User Story.
            - trace_id (opcional): ID para rastreamento de logs.

    Returns:
        Dicionário com a chave 'plano_e_casos_de_teste' contendo:
            - plano_de_testes: Informações gerais do plano.
            - casos_de_teste_gherkin: Lista de cenários estruturados.
        Ou dicionário com chave 'erro' em caso de falha.

    Note:
        Os cenários são gerados em formato estruturado para facilitar
        exportação para ferramentas como Jira, Xray, Azure DevOps, etc.
    """
    print("--- Etapa Extra: Criando Plano de Testes... ---")
    trace_id = state.get("trace_id")
    node_name = "criador_plano_testes"
    log_graph_event("node.start", trace_id=trace_id, node=node_name)
    started_at = time.perf_counter()
    contexto_para_plano = {
        "user_story": state["user_story"],
        "analise_ambiguidade": state["analise_da_us"].get("analise_ambiguidade", {}),
    }
    contexto_str = json.dumps(contexto_para_plano, indent=2, ensure_ascii=False)
    client = _get_llm_client()
    prompt_completo = (
        f"{PROMPT_CRIAR_PLANO_DE_TESTES}\n\nContexto:\n---\n{contexto_str}"
    )
    response = chamar_modelo_com_retry(
        client,
        prompt_completo,
        config=CONFIG_GERACAO_ANALISE,
        trace_id=trace_id,
        node=node_name,
    )

    if not response or not response.text:
        log_graph_event(
            "node.error",
            trace_id=trace_id,
            node=node_name,
            payload={"motivo": "resposta_vazia"},
            level=logging.ERROR,
        )
        return {
            "plano_e_casos_de_teste": {
                "erro": "Falha na comunicação com o serviço de planejamento."
            }
        }

    try:
        plano_json = json.loads(response.text)
    except json.JSONDecodeError:
        json_limpo = extract_json_from_text(response.text)
        if json_limpo:
            try:
                plano_json = json.loads(json_limpo)
            except json.JSONDecodeError:
                plano_json = {
                    "erro": f"Falha ao decodificar a resposta do plano. Resposta recebida: {response.text}"
                }
        else:
            plano_json = {
                "erro": f"Nenhum dado estruturado encontrado na resposta. Resposta recebida: {response.text}"
            }

    log_graph_event(
        "node.finish",
        trace_id=trace_id,
        node=node_name,
        payload={
            "duracao_ms": round((time.perf_counter() - started_at) * 1000, 2),
            "tem_erro": "erro" in plano_json,
            "quantidade_casos": len(
                plano_json.get("casos_de_teste_gherkin", [])  # type: ignore[arg-type]
                if isinstance(plano_json, dict)
                else []
            ),
        },
    )
    return {"plano_e_casos_de_teste": plano_json}


def node_gerar_relatorio_plano_de_testes(state: AgentState) -> AgentState:
    """Gera o relatório final do plano de testes (Markdown)."""
    print("--- Etapa 4: Compilando relatório do plano... ---")
    trace_id = state.get("trace_id")
    node_name = "gerador_relatorio_plano_de_testes"
    log_graph_event("node.start", trace_id=trace_id, node=node_name)
    started_at = time.perf_counter()

    # Reduz o contexto para evitar overload (mantém só resumo textual)
    contexto_completo = state.get("plano_e_casos_de_teste", {})
    plano_resumido = contexto_completo.get("plano_de_testes", {})
    casos = contexto_completo.get("casos_de_teste_gherkin", [])

    # Mantém apenas títulos e IDs no prompt, não todo o conteúdo Gherkin
    resumo_casos = [
        {
            "id": c.get("id", ""),
            "titulo": c.get("titulo", ""),
            "prioridade": c.get("prioridade", ""),
        }
        for c in casos[:10]  # envia no máximo 10 para evitar erro 500
    ]

    contexto_reduzido = {
        "plano_de_testes": plano_resumido,
        "resumo_casos": resumo_casos,
    }
    contexto_str = json.dumps(contexto_reduzido, indent=2, ensure_ascii=False)

    print(f"Tamanho do contexto enviado: {len(contexto_str)} caracteres")

    # Chamada ao modelo
    client = _get_llm_client()
    prompt_completo = (
        f"{PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES}\n\nDados:\n---\n{contexto_str}"
    )
    response = chamar_modelo_com_retry(
        client,
        prompt_completo,
        config=CONFIG_GERACAO_RELATORIO,
        trace_id=trace_id,
        node=node_name,
    )

    # Fallback local em caso de falha
    if not response or not getattr(response, "text", None):
        print("⚠️ Gemini falhou — gerando relatório simplificado localmente.")
        log_graph_event(
            "node.error",
            trace_id=trace_id,
            node=node_name,
            payload={"motivo": "resposta_vazia"},
            level=logging.ERROR,
        )
        resumo_fallback = (
            "# 🧪 Plano de Testes Gerado\n\n"
            "⚠️ Erro: não foi possível gerar o relatório detalhado via IA neste momento.\n\n"
            "Os casos de teste foram criados e estão disponíveis abaixo."
        )
        log_graph_event(
            "node.finish",
            trace_id=trace_id,
            node=node_name,
            payload={
                "duracao_ms": round((time.perf_counter() - started_at) * 1000, 2),
                "tem_erro": True,
            },
        )
        return {"relatorio_plano_de_testes": resumo_fallback}

    # Retorno normal (sucesso)
    resultado = {
        "relatorio_plano_de_testes": (
            response.text
            if response and response.text
            else "### Erro na Geração do Plano de Testes"
        )
    }
    log_graph_event(
        "node.finish",
        trace_id=trace_id,
        node=node_name,
        payload={"duracao_ms": round((time.perf_counter() - started_at) * 1000, 2)},
    )
    return resultado


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
    workflow_plano_testes.add_node(
        "criador_plano_testes", node_criar_plano_e_casos_de_teste
    )
    workflow_plano_testes.add_node(
        "gerador_relatorio_plano_de_testes", node_gerar_relatorio_plano_de_testes
    )
    workflow_plano_testes.set_entry_point("criador_plano_testes")
    workflow_plano_testes.add_edge(
        "criador_plano_testes", "gerador_relatorio_plano_de_testes"
    )
    workflow_plano_testes.add_edge("gerador_relatorio_plano_de_testes", END)
    return workflow_plano_testes.compile()


# --- Instanciação dos Grafos ---
grafo_analise = get_analysis_graph()
grafo_plano_testes = get_test_plan_graph()
