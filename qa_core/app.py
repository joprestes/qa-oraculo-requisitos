# ==========================================================
# app.py — Aplicação principal do QA Oráculo
# ==========================================================
#  Este arquivo define toda a interface Streamlit do projeto:
#   - Página principal de análise de User Stories
#   - Geração de plano de testes (IA)
#   - Exportações (Markdown, PDF, CSV Azure, XLSX Zephyr)
#   - Histórico de análises (visualização e exclusão)
#
# Princípios (QA Oráculo):
#   • Código modular (funções separadas por responsabilidade)
#   • Acessibilidade + automação de testes (data-testid / navegação teclado)
#   • Preparado para testes unitários e E2E
#   • Comentários didáticos onde a lógica não for óbvia
# ==========================================================

import datetime
import json
import logging
import sqlite3

import pandas as pd
import streamlit as st

from .a11y import (
    accessible_button,
    accessible_text_area,
    announce,
    apply_accessible_styles,
    render_accessibility_info,
    render_keyboard_shortcuts_guide,
)

# ===== Reexportações para compatibilidade com testes =====
# Os testes (tests/test_app_history_delete.py) fazem patch direto em:
# - app.delete_analysis_by_id
# - app.clear_history
# Por isso reexportamos estas funções do database aqui.
# Demais funções do banco: leitura/consulta e persistência no histórico
from .database import (
    clear_history,
    delete_analysis_by_id,
    get_all_analysis_history,
    get_analysis_by_id,
    init_db,
)

# Grafos de IA (LangGraph) — invocados nas funções cacheadas
from .graph import grafo_analise, grafo_plano_testes
from .observability import generate_trace_id

# Gerador de PDF — consolida análise e plano de testes em um relatório
from .pdf_generator import generate_pdf_report

# Estado global e reset — para nova análise sem resquícios
from .state_manager import initialize_state, reset_session

# Utilitários — helpers de exportação, normalização e formatação
from .text_utils import (
    clean_markdown_report,
    gerar_nome_arquivo_seguro,
    gerar_relatorio_md_dos_cenarios,
    get_flexible,
)
from .exports import (
    gerar_csv_azure_from_df,
    gerar_csv_xray_from_df,
    gerar_csv_testrail_from_df,
    preparar_df_para_zephyr_xlsx,
    to_excel,
)


# Métricas Prometheus (opcional)
# Métricas Prometheus (opcional)
from .metrics import track_analysis, track_export, start_metrics_server


@st.cache_resource
def init_metrics():
    """Inicializa o servidor de métricas (executa apenas uma vez)."""
    start_metrics_server(port=8000)


init_metrics()

logger = logging.getLogger(__name__)


# ==========================================================
#  Formatação segura de datas (compatível com testes)
# ==========================================================
def format_datetime(value):
    """Aceita datetime ou string ISO e retorna formato dd/mm/yyyy hh:mm."""
    from datetime import datetime

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M")
        except Exception:
            return value
    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y %H:%M")
    return str(value)


# ==========================================================
#  Auxiliar: garante bytes no download_button
# ==========================================================
def _ensure_bytes(data):
    """
    Garante que o conteúdo entregue ao st.download_button está em bytes.

    Por quê?
    - O Streamlit aceita bytes/bytearray como conteúdo binário.
    - Aqui convertemos strings, objetos com getvalue() (ex. BytesIO),
      e qualquer outro tipo para bytes de forma segura.
    """
    if isinstance(data, str):
        return data.encode("utf-8")

    if hasattr(data, "getvalue"):
        try:
            return data.getvalue()
        except Exception:
            # Se getvalue falhar, cai para as alternativas abaixo
            pass

    if isinstance(data, (bytes | bytearray)):
        return data

    # Fallback absoluto — converte para string e depois para bytes
    return bytes(str(data), "utf-8")


# ==========================================================
#  Auxiliar: Salva a análise atual no histórico (CORRIGIDO)
# ==========================================================
def _save_current_analysis_to_history(update_existing: bool = False):
    """
    Extrai os dados da sessão atual e salva ou atualiza no histórico.

    🔧 NOVO COMPORTAMENTO:
    - Se update_existing=False → cria um novo registro (modo padrão)
    - Se update_existing=True  → atualiza o registro já salvo no histórico

    💡 O ID do último registro salvo é armazenado em st.session_state["last_saved_id"].
    """

    try:
        user_story_from_input = st.session_state.get("user_story_input") or ""
        user_story_from_state = (
            st.session_state.get("analysis_state", {}).get("user_story") or ""
        )

        user_story_to_save = (
            user_story_from_input.strip()
            or user_story_from_state.strip()
            or "⚠️ User Story não disponível."
        )

        analysis_report = st.session_state.get("analysis_state", {}).get(
            "relatorio_analise_inicial"
        )
        analysis_report_to_save = (analysis_report or "").strip()

        test_plan_report = st.session_state.get("test_plan_report")
        test_plan_report_to_save = (test_plan_report or "").strip()
        test_plan_summary_to_save = _extract_plan_summary(
            st.session_state.get("test_plan_report_intro", test_plan_report_to_save)
        )

        test_plan_df_json_to_save = st.session_state.get("test_plan_df_json")
        if not test_plan_df_json_to_save:
            records = st.session_state.get("test_plan_df_records")
            if records:
                try:
                    test_plan_df_json_to_save = json.dumps(records, ensure_ascii=False)
                except (TypeError, ValueError):
                    test_plan_df_json_to_save = None

        # 🔍 Validação mínima
        if not any(
            [
                user_story_to_save
                and user_story_to_save != "⚠️ User Story não disponível.",
                analysis_report_to_save,
                test_plan_report_to_save,
            ]
        ):
            logger.warning("⚠️ Nenhum dado válido para salvar no histórico.")
            return

        from .database import get_db_connection  # evita dependência circular

        from contextlib import closing

        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            timestamp = datetime.datetime.now()

            # --- Se já houver registro e pedimos update_existing=True, atualiza ---
            if update_existing and st.session_state.get("last_saved_id"):
                cursor.execute(
                    """
                    UPDATE analysis_history
                    SET created_at = ?, user_story = ?, analysis_report = ?, test_plan_report = ?, test_plan_summary = ?, test_plan_df_json = ?
                    WHERE id = ?;
                    """,
                    (
                        timestamp,
                        user_story_to_save,
                        analysis_report_to_save,
                        test_plan_report_to_save,
                        test_plan_summary_to_save,
                        test_plan_df_json_to_save,
                        st.session_state["last_saved_id"],
                    ),
                )
                logger.info(
                    f"♻️ Registro existente atualizado (ID {st.session_state['last_saved_id']}) em {timestamp}"
                )
            else:
                # Caso contrário, cria um novo registro
                cursor.execute(
                    """
                    INSERT INTO analysis_history (
                        created_at,
                        user_story,
                        analysis_report,
                        test_plan_report,
                        test_plan_summary,
                        test_plan_df_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        timestamp,
                        user_story_to_save,
                        analysis_report_to_save,
                        test_plan_report_to_save,
                        test_plan_summary_to_save,
                        test_plan_df_json_to_save,
                    ),
                )
                st.session_state["last_saved_id"] = cursor.lastrowid
                st.session_state["history_saved"] = True
                logger.info(f"💾 Análise salva no histórico em {timestamp}")

            conn.commit()

    except sqlite3.Error as db_error:
        logger.error(f"❌ Erro de banco de dados ao salvar: {db_error}")
        announce(
            "Erro ao salvar no banco de dados. Verifique o arquivo de log.",
            "error",
            st_api=st,
        )
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao salvar no histórico: {e}")
        announce(
            "Ocorreu um erro ao salvar ou atualizar a análise no histórico, "
            "mas o fluxo principal não foi interrompido.",
            "warning",
            st_api=st,
        )


def save_analysis_to_history(update_existing: bool = False):
    """Mantém compatibilidade com testes que esperam esta função pública."""

    return _save_current_analysis_to_history(update_existing=update_existing)


# ==========================================================
#  Funções cacheadas (IA via LangGraph)
# ==========================================================
@track_analysis
@st.cache_data(show_spinner=False, ttl=3600)
def run_analysis_graph(user_story: str):
    """
    Executa o grafo de análise de User Story.
    Retorna um dicionário com:
      - 'analise_da_us': blocos estruturados (avaliacao/pontos/riscos/criterios/perguntas)
      - 'relatorio_analise_inicial': texto consolidado em Markdown
    """
    estado_inicial = {
        "user_story": user_story,
        "trace_id": generate_trace_id(),
    }
    return grafo_analise.invoke(estado_inicial)


@st.cache_data(show_spinner=False, ttl=3600)
def run_test_plan_graph(analysis_state: dict):
    """
    Executa o grafo de geração de Plano de Testes.
    Espera receber o estado de análise refinado.
    Retorna:
      - 'plano_e_casos_de_teste' com 'casos_de_teste_gherkin' (lista de cenários)
      - 'relatorio_plano_de_testes' (Markdown)
    """
    estado_inicial = {**analysis_state}
    estado_inicial.setdefault("trace_id", generate_trace_id())
    return grafo_plano_testes.invoke(estado_inicial)


# ==========================================================
#  Funções Auxiliares da Página Principal (Refatoradas)
# ==========================================================


def _evaluate_user_story_completeness(user_story: str) -> tuple[bool, list[str]]:
    """
    Avalia se a User Story possui informações mínimas para análise automática.

    Args:
        user_story: Texto informado pelo usuário.

    Returns:
        tuple[bool, list[str]]: (está_completa, lista_de_partes_em_falta)
    """
    text = (user_story or "").strip()
    missing_parts: list[str] = []

    if not text:
        return False, [
            'persona ("Como …")',
            'ação ("quero/preciso …")',
            'objetivo ("para …")',
        ]

    normalized = text.lower()
    if "como " not in normalized:
        missing_parts.append('persona ("Como …")')

    if not any(
        token in normalized
        for token in [" quero ", " desejo ", " preciso ", " gostaria "]
    ):
        missing_parts.append('ação ("quero/preciso …")')

    if not any(
        token in normalized
        for token in [" para ", " pra ", " para que", " para poder", " para poder "]
    ):
        missing_parts.append('objetivo ("para …")')

    word_count = len(
        [word for word in text.replace(",", " ").replace(".", " ").split() if word]
    )
    if word_count < 8 or len(text) < 40:
        missing_parts.append("detalhes complementares (ao menos 8 palavras)")

    return len(missing_parts) == 0, missing_parts


def _render_user_story_input():
    """
    Renderiza o campo de entrada da User Story e o botão de análise.

    Returns:
        bool: True se a análise foi iniciada, False caso contrário.
    """
    with st.form(key="user_story_form"):
        accessible_text_area(
            label="Insira a User Story aqui:",
            key="user_story_input",
            height=250,
            help_text="Digite ou cole sua User Story no formato: Como [persona], quero [ação], para [objetivo].",
            placeholder="Exemplo: Como usuário do app, quero redefinir minha senha via email...",
            st_api=st,
        )

        # Botão de submit do formulário
        submitted = st.form_submit_button(
            label="Analisar User Story",
            type="primary",
            help="Inicia a análise de IA da User Story fornecida.",
        )

    if submitted:
        user_story_txt = st.session_state.get("user_story_input", "")

        # Validação com Pydantic
        from .schemas import UserStoryInput
        from pydantic import ValidationError

        try:
            # Valida e sanitiza
            validated_input = UserStoryInput(content=user_story_txt)
            user_story_txt = validated_input.content
        except ValidationError as e:
            # Traduz mensagens de erro do Pydantic para português
            error_data = e.errors()[0] if e.errors() else {}
            raw_msg = error_data.get("msg", str(e))

            if "String should have at least" in raw_msg:
                min_len = error_data.get("ctx", {}).get("min_length", 10)
                friendly_msg = f"A User Story é muito curta. Digite pelo menos {min_len} caracteres."
            elif "String should have at most" in raw_msg:
                friendly_msg = "A User Story excedeu o limite máximo de caracteres."
            elif "Field required" in raw_msg:
                friendly_msg = "Por favor, preencha o campo da User Story."
            else:
                friendly_msg = f"Erro de validação: {raw_msg}"

            announce(friendly_msg, "warning", st_api=st)
            return True

        if user_story_txt:
            is_complete, missing_sections = _evaluate_user_story_completeness(
                user_story_txt
            )
            if not is_complete:
                missing_msg = ", ".join(missing_sections)
                exemplos_recomendados = (
                    "- Como gerente de contas, quero validar faturas atrasadas para priorizar cobranças.\n"
                    "- Como usuário do app bancário, quero redefinir minha senha via email para recuperar acesso.\n"
                    "- Como analista de QA, quero exportar relatórios em CSV para enviar ao time de negócios."
                )
                announce(
                    (
                        "A User Story parece incompleta. "
                        f"Informe {missing_msg} para iniciar a análise automática."
                    ),
                    "warning",
                    st_api=st,
                )
                announce(
                    "Exemplos esperados para uma boa análise:\n"
                    f"{exemplos_recomendados}",
                    "info",
                    st_api=st,
                )
                st.session_state.pop("analysis_state", None)
                st.session_state["show_generate_plan_button"] = False
                return True

            with st.status("🔮 O Oráculo está trabalhando...", expanded=True) as status:
                st.write("🔍 Analisando requisitos da User Story...")
                resultado_analise = run_analysis_graph(user_story_txt)
                st.write("✅ Análise concluída!")
                status.update(
                    label="✨ Análise Finalizada!", state="complete", expanded=False
                )

                # Guarda o resultado bruto da IA para edição posterior
                st.session_state["analysis_state"] = resultado_analise

                # Enquanto a edição não é confirmada, não mostramos o botão de gerar o plano
                st.session_state["show_generate_plan_button"] = False

                # Re-renderiza a página para exibir a seção de edição
                st.rerun()
        else:
            announce(
                "Por favor, insira uma User Story antes de analisar.",
                "warning",
                st_api=st,
            )
        return True
    return False


def _extract_analysis_fields():
    """
    Extrai os campos da análise do session_state e os converte para formato editável.

    Returns:
        tuple: (avaliacao_str, pontos_str, perguntas_str, criterios_str, riscos_str)
    """
    analise_json = st.session_state.get("analysis_state", {}).get("analise_da_us", {})

    # Tenta recuperar do estado de edição (caso o usuário tenha digitado e a página recarregado)
    # Se não houver edição em andamento, pega do JSON original

    # Avaliação
    if "edit_avaliacao" in st.session_state:
        avaliacao_str = st.session_state["edit_avaliacao"]
    else:
        avaliacao_str = get_flexible(analise_json, ["avaliacao_geral", "avaliacao"], "")

    # Pontos
    if "edit_pontos" in st.session_state:
        pontos_str = st.session_state["edit_pontos"]
    else:
        pontos_list = get_flexible(
            analise_json, ["pontos_ambiguos", "pontos_de_ambiguidade"], []
        )
        pontos_str = "\n".join(pontos_list)

    # Perguntas
    if "edit_perguntas" in st.session_state:
        perguntas_str = st.session_state["edit_perguntas"]
    else:
        perguntas_list = get_flexible(
            analise_json, ["perguntas_para_po", "perguntas_ao_po"], []
        )
        perguntas_str = "\n".join(perguntas_list)

    # Critérios
    if "edit_criterios" in st.session_state:
        criterios_str = st.session_state["edit_criterios"]
    else:
        criterios_list = get_flexible(
            analise_json, ["sugestao_criterios_aceite", "criterios_de_aceite"], []
        )
        criterios_str = "\n".join(criterios_list)

    # Riscos
    if "edit_riscos" in st.session_state:
        riscos_str = st.session_state["edit_riscos"]
    else:
        riscos_list = get_flexible(
            analise_json, ["riscos_e_dependencias", "riscos"], []
        )
        riscos_str = "\n".join(riscos_list)

    return avaliacao_str, pontos_str, perguntas_str, criterios_str, riscos_str


def _save_edited_analysis_fields():
    """
    Salva os campos editados do formulário de volta no session_state.
    """
    st.session_state.setdefault("analysis_state", {})
    st.session_state["analysis_state"].setdefault("analise_da_us", {})
    bloco = st.session_state["analysis_state"]["analise_da_us"]

    # Validação com Pydantic
    from .schemas import AnalysisEditInput
    from pydantic import ValidationError

    try:
        validated_data = AnalysisEditInput(
            avaliacao_geral=st.session_state.get("edit_avaliacao", ""),
            pontos_ambiguos=[
                line.strip()
                for line in st.session_state.get("edit_pontos", "").split("\n")
                if line.strip()
            ],
            perguntas_para_po=[
                line.strip()
                for line in st.session_state.get("edit_perguntas", "").split("\n")
                if line.strip()
            ],
            sugestao_criterios_aceite=[
                line.strip()
                for line in st.session_state.get("edit_criterios", "").split("\n")
                if line.strip()
            ],
            riscos_e_dependencias=[
                line.strip()
                for line in st.session_state.get("edit_riscos", "").split("\n")
                if line.strip()
            ],
        )

        # Atualiza o bloco com dados validados e sanitizados
        bloco["avaliacao_geral"] = validated_data.avaliacao_geral
        bloco["pontos_ambiguos"] = validated_data.pontos_ambiguos
        bloco["perguntas_para_po"] = validated_data.perguntas_para_po
        bloco["sugestao_criterios_aceite"] = validated_data.sugestao_criterios_aceite
        bloco["riscos_e_dependencias"] = validated_data.riscos_e_dependencias

        # Agora podemos avançar para a geração de plano
        st.session_state["show_generate_plan_button"] = True

    except ValidationError as e:
        announce(f"Erro de validação: {e}", "error", st_api=st)


def _render_analysis_edit_form():
    """
    Renderiza o formulário de edição da análise gerada pela IA.
    """
    announce(
        " 🔮 O Oráculo gerou a análise abaixo. Revise, edite se necessário e clique em 'Salvar' para prosseguir.",
        "info",
        st_api=st,
    )

    # Extrai os campos para edição
    avaliacao_str, pontos_str, perguntas_str, criterios_str, riscos_str = (
        _extract_analysis_fields()
    )

    # Formulário de edição — decisão de UX:
    #   editar tudo numa única tela para facilitar a revisão humana.
    with st.form(key="analysis_edit_form"):
        st.subheader("📝 Análise Editável")

        accessible_text_area(
            label="Avaliação Geral",
            key="edit_avaliacao",
            height=75,
            value=avaliacao_str,
            help_text="Descreva o entendimento geral da User Story — clareza, coerência e completude.",
            placeholder="Exemplo: A User Story apresenta objetivo claro, mas falta detalhar critérios de sucesso.",
            st_api=st,
        )

        accessible_text_area(
            label="Pontos Ambíguos",
            key="edit_pontos",
            height=125,
            value=pontos_str,
            help_text="Liste trechos da User Story que podem gerar múltiplas interpretações ou dúvidas.",
            placeholder="Exemplo: O termo 'processar pagamento' não especifica o meio de pagamento utilizado.",
            st_api=st,
        )

        accessible_text_area(
            label="Perguntas para o PO",
            key="edit_perguntas",
            height=125,
            value=perguntas_str,
            help_text="Inclua perguntas que o QA faria ao PO para esclarecer requisitos e expectativas.",
            placeholder="Exemplo: O campo de CPF será validado no backend ou apenas no frontend?",
            st_api=st,
        )

        accessible_text_area(
            label="Critérios de Aceite",
            key="edit_criterios",
            height=150,
            value=criterios_str,
            help_text="Defina os critérios objetivos para considerar a User Story concluída com sucesso.",
            placeholder="Exemplo: O usuário deve receber um email de confirmação após redefinir a senha.",
            st_api=st,
        )

        accessible_text_area(
            label="Riscos e Dependências",
            key="edit_riscos",
            height=100,
            value=riscos_str,
            help_text="Aponte riscos técnicos, dependências entre times ou pré-condições para execução.",
            placeholder="Exemplo: Depende da API de autenticação, ainda em desenvolvimento pelo time backend.",
            st_api=st,
        )

        submitted = st.form_submit_button("Salvar Análise e Continuar")

    # Quando o form é submetido, persistimos as edições no estado
    if submitted:
        _save_edited_analysis_fields()
        announce("Análise refinada salva com sucesso!", "success", st_api=st)
        st.rerun()


def _render_test_plan_generation():
    """
    Renderiza a seção de geração do plano de testes.
    """
    # Mostra o relatório de análise (texto da IA)
    with st.expander("📘 Análise Refinada da User Story", expanded=False):
        relatorio = st.session_state.get("analysis_state", {}).get(
            "relatorio_analise_inicial", ""
        )
        st.markdown(clean_markdown_report(relatorio), unsafe_allow_html=True)

    announce(
        "Deseja que o Oráculo gere um Plano de Testes com base na análise refinada?",
        "info",
        st_api=st,
    )

    col1, col2, _ = st.columns([1, 1, 2])

    # Botão para gerar o plano de testes com LangGraph
    if col1.button(
        "Sim, Gerar Plano de Testes", type="primary", use_container_width=True
    ):
        with st.status("🔮 Elaborando o Plano de Testes...", expanded=True) as status:
            st.write("🧠 Refinando cenários Gherkin...")
            try:
                resultado_plano = run_test_plan_graph(
                    st.session_state.get("analysis_state", {})
                )
                st.write("✅ Plano gerado com sucesso!")
                status.update(
                    label="✨ Plano de Testes Pronto!", state="complete", expanded=False
                )

                casos_de_teste = resultado_plano.get("plano_e_casos_de_teste", {}).get(
                    "casos_de_teste_gherkin", []
                )

                if not casos_de_teste or not isinstance(casos_de_teste, list):
                    # Força a entrada no 'except' se a IA não retornar o formato esperado
                    raise ValueError(
                        "O Oráculo não conseguiu gerar um plano de testes estruturado."
                    )

                st.session_state["test_plan_report"] = resultado_plano.get(
                    "relatorio_plano_de_testes"
                )
                df = pd.DataFrame(casos_de_teste)
                df_clean = df.apply(
                    lambda col: col.apply(
                        lambda x: ("\n".join(map(str, x)) if isinstance(x, list) else x)
                    )
                )
                df_clean.fillna("", inplace=True)
                st.session_state["test_plan_df"] = df_clean
                st.session_state["test_plan_report_intro"] = (
                    st.session_state.get("test_plan_report") or ""
                )
                records = df_clean.to_dict(orient="records")
                st.session_state["test_plan_df_records"] = records
                st.session_state["test_plan_df_json"] = (
                    json.dumps(records, ensure_ascii=False) if records else None
                )
                st.session_state["test_plan_report"] = _compose_test_plan_report(
                    st.session_state.get("test_plan_report_intro", ""),
                    df_clean,
                )

                pdf_bytes = generate_pdf_report(
                    st.session_state.get("analysis_state", {}).get(
                        "relatorio_analise_inicial", ""
                    ),
                    df_clean,
                )
                st.session_state["pdf_report_bytes"] = pdf_bytes

                if not st.session_state.get("history_saved"):
                    _save_current_analysis_to_history()
                    st.session_state["history_saved"] = True  # evita duplicação

                st.session_state["analysis_finished"] = True
                announce("Plano de Testes gerado com sucesso!", "success", st_api=st)
                st.rerun()

            except Exception as e:
                # Em caso de falha, informa o usuário, mas não perde o progresso
                logger.error(f"❌ Falha na geração do plano de testes: {e}")
                announce(
                    "O Oráculo não conseguiu gerar um plano de testes estruturado.",
                    "error",
                    st_api=st,
                )
                # Limpa qualquer resquício de plano de teste para não exibir dados errados
                st.session_state["test_plan_report"] = ""
                st.session_state["test_plan_df"] = None
                st.session_state.pop("test_plan_df_records", None)
                st.session_state.pop("test_plan_df_json", None)
                st.session_state.pop("test_plan_report_intro", None)
                _save_current_analysis_to_history()
                st.rerun()

    # Botão para encerrar sem gerar plano (mas salvando análise)
    if col2.button("Não, Encerrar", use_container_width=True):
        if not st.session_state.get("history_saved"):
            _save_current_analysis_to_history()
            st.session_state["history_saved"] = True  # evita duplicação
        st.session_state["analysis_finished"] = True
        st.rerun()


def _compose_test_plan_report(summary_text: str, df: pd.DataFrame) -> str:
    """
    Combina o sumário original do plano de testes com os cenários atuais.

    Motivações:
    • O sumário inicial é gerado pela IA com objetivo, escopo e estratégia.
    • Os cenários Gherkin retornam em uma estrutura tabular (DataFrame).
    • Durante edições/exclusões, precisamos atualizar apenas a seção de cenários
      sem perder as partes redigidas pela IA.
    """

    summary = (summary_text or "").strip()
    scenarios_md = (gerar_relatorio_md_dos_cenarios(df) or "").strip()

    if not summary:
        return scenarios_md
    if not scenarios_md:
        return summary

    marker = "### 🧩"
    if marker in summary:
        header = summary.split(marker, 1)[0].rstrip()
        if header:
            return f"{header}\n\n{scenarios_md}"
        return scenarios_md

    return f"{summary}\n\n---\n\n{scenarios_md}"


def _extract_plan_summary(report_text: str) -> str:
    """
    Extrai apenas o cabeçalho/introdução do plano de testes.

    Motivo:
    • Evitar que os cenários apareçam duplicados no resumo principal.
    • Permitir salvar o sumário gerado pela IA separadamente no banco (test_plan_summary).
    """
    if not report_text:
        return ""

    marker = "### 🧩"
    if marker in report_text:
        return report_text.split(marker, 1)[0].rstrip()
    return report_text.strip()


def _get_plan_summary_from_state() -> str:
    """
    Obtém o sumário do plano armazenado no session_state.

    Estratégia:
    • Usa `test_plan_report_intro` quando disponível (persistido na geração inicial via IA).
    • Caso contrário, extrai do `test_plan_report` já existente.
    • Armazena o resultado para acessos subsequentes (evita retrabalho).
    """
    summary = st.session_state.get("test_plan_report_intro")
    if summary:
        return summary
    full_report = st.session_state.get("test_plan_report", "")
    summary = _extract_plan_summary(full_report)
    st.session_state["test_plan_report_intro"] = summary
    return summary


def _update_test_plan_outputs(updated_df: pd.DataFrame):
    """
    Atualiza DataFrame, relatório Markdown e PDF após modificações nos cenários.

    Responsabilidades principais:
    • Persistir DataFrame atualizado em memoria/JSON (para histórico/exportações).
    • Remontar o markdown do plano sem perder o sumário introdutório.
    • Regenerar o PDF para downloads imediatos.
    • Deixar `test_plan_df_json` pronto para salvar no histórico.
    """
    st.session_state["test_plan_df"] = updated_df
    records = updated_df.fillna("").to_dict(orient="records")
    st.session_state["test_plan_df_records"] = records
    st.session_state["test_plan_df_json"] = (
        json.dumps(records, ensure_ascii=False) if records else None
    )
    intro = _get_plan_summary_from_state()
    st.session_state["test_plan_report"] = _compose_test_plan_report(intro, updated_df)

    analysis_report = st.session_state.get("analysis_state", {}).get(
        "relatorio_analise_inicial", ""
    )
    try:
        st.session_state["pdf_report_bytes"] = generate_pdf_report(
            analysis_report, updated_df
        )
    except Exception as pdf_error:
        logger.error(f"❌ Erro ao regenerar PDF após atualização do plano: {pdf_error}")
        st.session_state["pdf_report_bytes"] = b""


def _delete_test_case(pending_case: dict):
    """
    Remove um cenário específico do DataFrame e atualiza derivados.

    Funciona por múltiplas pistas:
    • Índice da linha (row_index) — mais rápido quando disponível.
    • ID amigável do caso (ex.: "CT-1") — apoio quando índices mudam.
    • Título — fallback em situações onde não há ID estável.

    Após a remoção:
    • Reconstrói DF/Markdown/PDF.
    • Atualiza o registro no histórico (update_existing=True).
    • Exibe feedback acessível (announce + toast).
    """
    df_original = st.session_state.get("test_plan_df")

    if df_original is None or df_original.empty:
        announce(
            "Nenhum cenário disponível para exclusão no momento.",
            "warning",
            st_api=st,
        )
        st.session_state.pop("pending_case_deletion", None)
        st.rerun()
        return

    row_index = pending_case.get("row_index")
    index_label = None

    if row_index is not None and row_index in df_original.index:
        index_label = row_index
    else:
        # Tenta converter para posição numérica (ex.: strings "0", numpy.int64, etc.)
        try:
            row_position = int(row_index)  # type: ignore[arg-type]
            if 0 <= row_position < len(df_original.index):
                index_label = df_original.index[row_position]
        except (TypeError, ValueError):
            index_label = None

    if index_label is None:
        test_id = pending_case.get("test_id")
        if test_id is not None and "id" in df_original.columns:
            matches = df_original.index[df_original["id"].astype(str) == str(test_id)]
            if len(matches) == 1:
                index_label = matches[0]

    if index_label is None:
        title = pending_case.get("title")
        if title is not None and "titulo" in df_original.columns:
            matches = df_original.index[df_original["titulo"] == title]
            if len(matches) == 1:
                index_label = matches[0]

    if index_label is None:
        announce(
            "Não foi possível localizar o cenário selecionado para exclusão.",
            "error",
            st_api=st,
        )
        st.session_state.pop("pending_case_deletion", None)
        st.rerun()
        return

    updated_df = df_original.drop(index=index_label).reset_index(drop=True)

    _update_test_plan_outputs(updated_df)
    st.session_state.pop("pending_case_deletion", None)

    _save_current_analysis_to_history(update_existing=True)
    announce(
        "Cenário removido do plano de testes e histórico atualizado.",
        "success",
        st_api=st,
    )
    st.toast("🗑️ Cenário excluído com sucesso.")
    st.rerun()


def _save_scenario_edit(index: int, new_scenario: str) -> None:
    """
    Salva edição de cenário e atualiza persistência no histórico.

    Args:
        index: Índice do cenário no DataFrame
        new_scenario: Novo conteúdo do cenário editado
    """
    # Converte para string para evitar problemas com mocks em testes
    cenario_str = str(new_scenario).strip()

    # Atualiza DataFrame
    st.session_state["test_plan_df"].at[index, "cenario"] = cenario_str

    # Atualiza JSON para persistência
    updated_df = st.session_state["test_plan_df"]
    records = updated_df.fillna("").to_dict(orient="records")
    st.session_state["test_plan_df_records"] = records
    st.session_state["test_plan_df_json"] = (
        json.dumps(records, ensure_ascii=False) if records else None
    )

    # Atualiza relatório markdown
    intro = _get_plan_summary_from_state()
    st.session_state["test_plan_report"] = _compose_test_plan_report(intro, updated_df)

    # Salva no histórico
    _save_current_analysis_to_history(update_existing=True)

    st.toast("✅ Cenário atualizado e salvo!")


def _render_test_cases_table():
    """
    Renderiza a tabela de casos de teste com expanderes individuais.

    Destaques da UX:
    • Resumo tabular para leitura rápida.
    • Expanders com edição de cenários e botões de excluir.
    • Quando há exclusão pendente, a confirmação aparece dentro do expander
      correspondente (contexto visual + acessibilidade).
    """
    if (
        st.session_state.get("test_plan_df") is None
        or st.session_state["test_plan_df"].empty
    ):
        return

    df = st.session_state["test_plan_df"].copy()

    #  Define as colunas completas para o resumo
    colunas_resumo = [
        "id",
        "titulo",
        "prioridade",
        "criterio_de_aceitacao_relacionado",
        "justificativa_acessibilidade",
    ]

    #  Filtra e renomeia para nomes amigáveis
    df_resumo = (
        df[[c for c in colunas_resumo if c in df.columns]]
        .rename(
            columns={
                "id": "ID",
                "titulo": "Título",
                "prioridade": "Prioridade",
                "criterio_de_aceitacao_relacionado": "Critério de Aceitação Relacionado",
                "justificativa_acessibilidade": "Justificativa de Acessibilidade",
            }
        )
        .fillna("")  # evita None
    )

    st.markdown("### 📊 Resumo dos Casos de Teste")
    st.dataframe(df_resumo, width="stretch")
    st.markdown(
        '<div data-testid="tabela-casos-teste"></div>',
        unsafe_allow_html=True,
    )

    pending_case = st.session_state.get("pending_case_deletion")

    #  Dropdowns individuais (detalhes)
    with st.expander("📁 Casos de Teste (Expandir para ver todos)", expanded=False):
        for index, row in df.iterrows():
            # Garante que sempre haverá um identificador mesmo se a coluna "id" não existir
            test_id = row.get("id", f"CT-{index + 1:03d}")
            with st.expander(
                f"📋 {test_id} — {row.get('titulo', '-')}", expanded=False
            ):
                is_pending_case = False
                if pending_case:
                    is_pending_case = any(
                        [
                            pending_case.get("row_index") == row.name,
                            pending_case.get("test_id")
                            and str(pending_case["test_id"]) == str(row.get("id")),
                            pending_case.get("title") == row.get("titulo"),
                        ]
                    )

                if is_pending_case:
                    with st.container(border=True):
                        announce(
                            f"Tem certeza que deseja remover o cenário '{pending_case.get('label', '-')}' do plano de testes?",
                            "warning",
                            st_api=st,
                        )
                        col_confirm, col_cancel = st.columns(2)

                        with col_confirm:
                            if accessible_button(
                                label="✅ Sim, remover cenário",
                                key=f"confirm_delete_case_{row.name}",
                                context="Confirma a exclusão permanente do cenário selecionado.",
                                type="primary",
                                use_container_width=True,
                                st_api=col_confirm,
                            ):
                                _delete_test_case(pending_case)
                                return

                        with col_cancel:
                            if accessible_button(
                                label="❌ Não, manter cenário",
                                key=f"cancel_delete_case_{row.name}",
                                context="Cancela a exclusão e mantém o cenário no plano de testes.",
                                type="secondary",
                                use_container_width=True,
                                st_api=col_cancel,
                            ):
                                st.session_state.pop("pending_case_deletion", None)
                                announce(
                                    f"Cenário {index + 1}",  # type: ignore
                                    "info",
                                    st_api=st,
                                )
                                st.rerun()
                                return

                st.markdown(f"**Prioridade:** {row.get('prioridade', '-')}")
                st.markdown(
                    f"**Critério de Aceitação Relacionado:** {row.get('criterio_de_aceitacao_relacionado','-')}"
                )
                st.markdown(
                    f"**Justificativa de Acessibilidade:** {row.get('justificativa_acessibilidade','-')}"
                )

                # Verifica se este cenário está em modo de edição
                editing_index = st.session_state.get("editing_scenario_index")
                is_editing = editing_index == index

                if row.get("cenario"):
                    if is_editing:
                        # MODO DE EDIÇÃO
                        st.markdown("**Cenário Gherkin (editando):**")

                        cenario_editado = accessible_text_area(
                            label=f"Editar Cenário {test_id}",
                            key=f"edit_cenario_{test_id}",
                            value=row["cenario"],
                            height=220,
                            help_text="Edite o cenário de teste mantendo a estrutura Gherkin (Dado, Quando, Então).",
                            placeholder=(
                                "Exemplo:\n"
                                "Dado que o usuário possui um cartão válido\n"
                                "Quando ele realiza a compra\n"
                                "Então o sistema deve gerar um token de pagamento com sucesso"
                            ),
                            st_api=st,
                        )

                        col1, col2 = st.columns(2)
                        with col1:
                            if accessible_button(
                                label="✅ Confirmar Edição",
                                key=f"confirm_edit_{test_id}",
                                context="Salva as alterações no cenário e atualiza o histórico.",
                                type="primary",
                                use_container_width=True,
                                st_api=col1,
                            ):
                                _save_scenario_edit(index, cenario_editado)
                                st.session_state["editing_scenario_index"] = None
                                st.rerun()

                        with col2:
                            if accessible_button(
                                label="❌ Cancelar",
                                key=f"cancel_edit_{test_id}",
                                context="Descarta as alterações e volta para o modo de visualização.",
                                type="secondary",
                                use_container_width=True,
                                st_api=col2,
                            ):
                                st.session_state["editing_scenario_index"] = None
                                st.rerun()
                    else:
                        # MODO DE VISUALIZAÇÃO
                        st.markdown("**Cenário Gherkin:**")
                        st.code(row["cenario"], language="gherkin")

                        col1, col2 = st.columns(2)
                        with col1:
                            if accessible_button(
                                label="✏️ Editar Cenário",
                                key=f"edit_btn_{test_id}",
                                context="Ativa o modo de edição para este cenário.",
                                type="secondary",
                                use_container_width=True,
                                st_api=col1,
                            ):
                                st.session_state["editing_scenario_index"] = index
                                st.rerun()

                        with col2:
                            if accessible_button(
                                label="🗑️ Excluir Cenário",
                                key=f"delete_btn_{test_id}",
                                context="Remove este cenário do plano de testes.",
                                type="secondary",
                                use_container_width=True,
                                st_api=col2,
                            ):
                                st.session_state["pending_case_deletion"] = {
                                    "row_index": row.name,
                                    "label": f"{test_id} — {row.get('titulo', '-')}",
                                    "test_id": row.get("id"),
                                    "title": row.get("titulo"),
                                }
                                st.rerun()
                                return
                else:
                    announce(
                        "Este caso de teste ainda não possui cenário em formato Gherkin.",
                        "info",
                        st_api=st,
                    )


def _render_history_test_cases_table(df: pd.DataFrame):
    """
    Renderiza os casos de teste em modo somente leitura (histórico).

    Objetivos:
    • Reaproveitar o mesmo layout principal do fluxo ativo.
    • Permitir consulta aos cenários (incluindo Gherkin) diretamente no histórico.
    • Evitar ações editáveis — aqui o usuário apenas visualiza.
    """
    if df is None or df.empty:
        return

    df = df.copy().fillna("")
    colunas_resumo = [
        "id",
        "titulo",
        "prioridade",
        "criterio_de_aceitacao_relacionado",
        "justificativa_acessibilidade",
    ]
    df_resumo = (
        df[[c for c in colunas_resumo if c in df.columns]]
        .rename(
            columns={
                "id": "ID",
                "titulo": "Título",
                "prioridade": "Prioridade",
                "criterio_de_aceitacao_relacionado": "Critério de Aceitação Relacionado",
                "justificativa_acessibilidade": "Justificativa de Acessibilidade",
            }
        )
        .fillna("")
    )

    st.markdown("### 📊 Resumo dos Casos de Teste")
    st.dataframe(df_resumo, width="stretch")
    st.markdown(
        '<div data-testid="tabela-casos-teste-historico"></div>',
        unsafe_allow_html=True,
    )

    with st.expander("📁 Casos de Teste (Expandir para ver todos)", expanded=False):
        for index, row in df.iterrows():
            test_id = row.get("id", f"CT-{int(index) + 1:03d}")  # type: ignore
            titulo = row.get("titulo", "-")
            with st.expander(f"📋 {test_id} — {titulo}", expanded=False):
                st.markdown(f"**Prioridade:** {row.get('prioridade', '-')}")
                st.markdown(
                    f"**Critério de Aceitação Relacionado:** {row.get('criterio_de_aceitacao_relacionado','-')}"
                )
                st.markdown(
                    f"**Justificativa de Acessibilidade:** {row.get('justificativa_acessibilidade','-')}"
                )
                cenario = row.get("cenario", "")
                if isinstance(cenario, list):
                    cenario = "\n".join(str(item) for item in cenario)
                cenario = str(cenario).strip()
                if cenario:
                    st.markdown("**Cenário Gherkin:**")
                    st.code(cenario, language="gherkin")
                else:
                    announce(
                        "Este caso de teste não possui cenário Gherkin salvo.",
                        "info",
                        st_api=st,
                    )


def _render_history_test_plan(analysis_entry: dict):
    """
    Exibe o plano de testes armazenado no histórico com resumo e cenários.

    Contém:
    • Sumário em Markdown (introdução do plano).
    • Tabela + expanders somente leitura, quando dispomos dos dados em JSON.
    • Como fallback, mostra o markdown completo salvo, garantindo compatibilidade
      com registros antigos (anteriores à migração).
    """
    summary_text = analysis_entry.get("test_plan_summary") or _extract_plan_summary(
        analysis_entry.get("test_plan_report", "")
    )

    if summary_text:
        with st.expander(
            "🧪 Plano de Testes Gerado (Resumo em Markdown)", expanded=False
        ):
            st.markdown(
                clean_markdown_report(summary_text),
                unsafe_allow_html=True,
            )

    df_json = analysis_entry.get("test_plan_df_json")
    records: list[dict] = []
    if df_json:
        try:
            records = json.loads(df_json)
        except (TypeError, ValueError, json.JSONDecodeError):
            records = []

    if records:
        df = pd.DataFrame(records)
        _render_history_test_cases_table(df)
        return

    plano_report = analysis_entry.get("test_plan_report", "")
    if plano_report:
        with st.expander("🧪 Plano de Testes (Markdown Completo)", expanded=False):
            st.markdown(
                clean_markdown_report(plano_report),
                unsafe_allow_html=True,
            )
    else:
        announce(
            "Nenhum plano de testes foi gerado para esta análise.",
            "info",
            st_api=st,
        )


def _render_results_section():
    """
    Renderiza a seção de resultados da análise e plano de testes.
    """
    announce("Análise concluída com sucesso!", "success", st_api=st)

    # ==================================================
    #  ANÁLISE REFINADA DA USER STORY
    # ==================================================
    if st.session_state.get("analysis_state"):
        with st.expander("📘 Análise Refinada da User Story", expanded=False):
            relatorio_analise = st.session_state.get("analysis_state", {}).get(
                "relatorio_analise_inicial", ""
            )
            st.markdown(
                clean_markdown_report(relatorio_analise), unsafe_allow_html=True
            )

        # ==================================================
        #  RELATÓRIO DO PLANO DE TESTES (VISÃO GERAL)
        # ==================================================
        if st.session_state.get("test_plan_report"):
            with st.expander(
                "🧪 Plano de Testes Gerado (Resumo em Markdown)", expanded=True
            ):
                summary_md = _get_plan_summary_from_state()
                if summary_md:
                    st.markdown(
                        clean_markdown_report(summary_md),
                        unsafe_allow_html=True,
                    )
                else:
                    st.info(
                        "Resumo do plano de testes não disponível. Consulte os cenários abaixo.",
                        icon="ℹ️",
                    )

        # ==================================================
        # 📂 CASOS DE TESTE (TABELA RESUMO + DETALHES)
        # ==================================================
        _render_test_cases_table()


# ==========================================================
#  Wrappers de Exportação com Métricas
# ==========================================================
@track_export(format="markdown")
def _prepare_markdown_export(analysis_report: str, test_plan_report: str) -> bytes:
    """Prepara o conteúdo Markdown para exportação, registrando métricas."""
    content = f"{analysis_report or ''}\n\n---\n\n{test_plan_report or ''}"
    return _ensure_bytes(content)


@track_export(format="pdf")
def _prepare_pdf_export(analysis_report: str, test_plan_df) -> bytes:
    """Gera o PDF para exportação, registrando métricas."""
    # Se já tivermos os bytes em cache (session_state), poderíamos retornar direto,
    # mas para registrar a métrica de 'exportação realizada', vamos chamar o gerador
    # ou apenas registrar que foi feito.
    # Aqui, vamos assumir que se chama esta função, é para gerar/obter o PDF.
    return generate_pdf_report(analysis_report, test_plan_df)


def _render_basic_exports():
    """
    Renderiza os botões de exportação básicos (MD, PDF) e avançados (Cucumber, Postman).
    """
    col_md, col_pdf, col_cucumber, col_postman = st.columns(4)

    # 📝 Exporta relatório Markdown
    # Preparamos o conteúdo sob demanda (lazy) seria ideal, mas o st.download_button
    # pede os dados já prontos ou uma função callback.
    # Para simplificar e garantir o tracking, vamos preparar os dados aqui.
    # Nota: O tracking ocorrerá a cada re-render se chamarmos a função aqui.
    # O ideal para download_button é usar o callback, mas ele não permite retornar dados,
    # apenas executar ações.
    # Abordagem: Vamos preparar os dados (o que dispara a métrica) apenas se o usuário clicar?
    # O Streamlit não facilita isso no download_button padrão sem recarregar.
    # Vamos manter a geração prévia, mas cuidado com métricas duplicadas a cada render.
    # Melhoria: Usar st.cache_data nos wrappers se quisermos evitar re-processamento,
    # mas queremos contar EXPORTAÇÕES (cliques).
    # Com download_button, a contagem de cliques é difícil via backend puro do Streamlit.
    # Vamos aceitar que a métrica será "geração de arquivo para exportação" por enquanto.

    md_content = _prepare_markdown_export(
        st.session_state.get("analysis_state", {}).get("relatorio_analise_inicial", ""),
        st.session_state.get("test_plan_report", ""),
    )

    col_md.download_button(
        "📝 Relatório (.md)",
        md_content,
        file_name=gerar_nome_arquivo_seguro(
            st.session_state.get("analysis_state", {}).get("user_story", ""), "md"
        ),
        help="Baixa a análise e o plano de testes em Markdown",
    )

    # 📄 Exporta relatório PDF
    # O PDF pode ser pesado para gerar a cada render.
    # Vamos usar o que está no session_state se existir, mas para tracking
    # precisaríamos saber quando baixou.
    # Como limitação do Streamlit, vamos registrar a métrica quando o PDF é GERADO/ATUALIZADO
    # (que acontece no _update_test_plan_outputs ou na geração inicial).
    # A função _prepare_pdf_export acima pode ser usada lá.
    # AQUI apenas entregamos os bytes.

    pdf_bytes = st.session_state.get("pdf_report_bytes")
    if not pdf_bytes:
        # Tenta gerar se não existir
        try:
            pdf_bytes = _prepare_pdf_export(
                st.session_state.get("analysis_state", {}).get(
                    "relatorio_analise_inicial", ""
                ),
                st.session_state.get("test_plan_df"),
            )
            st.session_state["pdf_report_bytes"] = pdf_bytes
        except Exception:
            pdf_bytes = b""

    col_pdf.download_button(
        "📄 Relatório (.pdf)",
        pdf_bytes,
        file_name=gerar_nome_arquivo_seguro(
            st.session_state.get("analysis_state", {}).get("user_story", ""), "pdf"
        ),
        help="Baixa um relatório PDF formatado",
        disabled=not pdf_bytes,
    )

    # 🥒 Exporta para Cucumber Studio (ZIP de .feature files)
    df_para_cucumber = st.session_state.get("test_plan_df")
    if df_para_cucumber is not None and not df_para_cucumber.empty:
        from .utils.exporters import export_to_cucumber_zip

        try:
            cucumber_zip = export_to_cucumber_zip(df_para_cucumber)
            col_cucumber.download_button(
                "🥒 Cucumber (.zip)",
                cucumber_zip,
                file_name=gerar_nome_arquivo_seguro(
                    st.session_state.get("user_story_input", ""), "cucumber.zip"
                ),
                mime="application/zip",
                use_container_width=True,
                help="Baixa um ZIP com arquivos .feature para Cucumber Studio",
            )
        except Exception as e:
            logger.error(f"Erro ao gerar Cucumber ZIP: {e}")
            col_cucumber.button(
                "🥒 Cucumber (.zip)",
                disabled=True,
                use_container_width=True,
                help="Erro ao gerar exportação",
            )

    # 📮 Exporta para Postman Collection (JSON)
    df_para_postman = st.session_state.get("test_plan_df")
    if df_para_postman is not None and not df_para_postman.empty:
        from .utils.exporters import export_to_postman_collection

        try:
            user_story = st.session_state.get("user_story_input", "")
            postman_json = export_to_postman_collection(df_para_postman, user_story)
            col_postman.download_button(
                "📮 Postman (.json)",
                postman_json.encode("utf-8"),
                file_name=gerar_nome_arquivo_seguro(
                    st.session_state.get("user_story_input", ""), "postman.json"
                ),
                mime="application/json",
                use_container_width=True,
                help="Baixa uma Postman Collection com os cenários de teste",
            )
        except Exception as e:
            logger.error(f"Erro ao gerar Postman Collection: {e}")
            col_postman.button(
                "📮 Postman (.json)",
                disabled=True,
                use_container_width=True,
                help="Erro ao gerar exportação",
            )

    # Retorna as colunas para Azure, Zephyr e Xray (mantém compatibilidade)
    col_azure, col_zephyr, col_xray = st.columns(3)
    return col_azure, col_zephyr, col_xray


def _render_export_previews():
    """
    Renderiza previews dos arquivos de exportação em um expander com abas.
    Permite ao usuário verificar o conteúdo antes de baixar.
    """
    if not st.session_state.get("test_plan_df") is not None:
        return

    with st.expander("👁️ Visualizar Arquivos de Exportação (Preview)", expanded=False):
        tabs = st.tabs(
            ["Markdown", "Azure CSV", "TestRail CSV", "Xray CSV", "Zephyr (Dados)"]
        )

        # 1. Markdown Preview
        with tabs[0]:
            content = (
                f"{(st.session_state.get('analysis_state', {}).get('relatorio_analise_inicial') or '')}\n\n"
                f"---\n\n"
                f"{(st.session_state.get('test_plan_report') or '')}"
            )
            st.caption(f"Total: {len(content)} caracteres")
            st.code(content, language="markdown")

        # 2. Azure CSV Preview
        with tabs[1]:
            try:
                csv_azure_bytes = gerar_csv_azure_from_df(
                    st.session_state.get("test_plan_df"),
                    st.session_state.get("area_path_input", ""),
                    st.session_state.get("assigned_to_input", ""),
                )
                csv_azure_str = csv_azure_bytes.decode("utf-8-sig")
                st.caption("Preview das primeiras 50 linhas")
                st.code("\n".join(csv_azure_str.splitlines()[:50]), language="csv")
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o preview do Azure: {e}")

        # 3. TestRail CSV Preview
        with tabs[2]:
            try:
                csv_testrail_bytes = gerar_csv_testrail_from_df(
                    st.session_state.get("test_plan_df"),
                    st.session_state.get("testrail_section", ""),
                    st.session_state.get("testrail_priority", "Medium"),
                    "Test Case (Steps)",
                    st.session_state.get("testrail_references", ""),
                )
                csv_testrail_str = csv_testrail_bytes.decode("utf-8")
                st.caption("Preview das primeiras 50 linhas")
                st.code("\n".join(csv_testrail_str.splitlines()[:50]), language="csv")
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o preview do TestRail: {e}")

        # 4. Xray CSV Preview
        with tabs[3]:
            try:
                # Recria lógica de campos do Xray (simplificada para preview)
                xray_fields = {}
                if st.session_state.get("xray_labels"):
                    xray_fields["Labels"] = st.session_state.get("xray_labels")
                if st.session_state.get("xray_priority"):
                    xray_fields["Priority"] = st.session_state.get("xray_priority")

                # Campos customizados
                custom_text = st.session_state.get("xray_custom_fields", "").strip()
                if custom_text:
                    for raw_line in custom_text.split("\n"):
                        if "=" in raw_line:
                            key, value = raw_line.split("=", 1)
                            xray_fields[key.strip()] = value.strip()

                csv_xray_bytes = gerar_csv_xray_from_df(
                    st.session_state.get("test_plan_df"),
                    st.session_state.get("xray_test_folder", "Preview_Folder"),
                    xray_fields,
                )
                csv_xray_str = csv_xray_bytes.decode("utf-8")
                st.caption("Preview das primeiras 50 linhas")
                st.code("\n".join(csv_xray_str.splitlines()[:50]), language="csv")
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o preview do Xray: {e}")

        # 5. Zephyr Preview (mostra DataFrame preparado)
        with tabs[4]:
            try:
                df_zephyr = preparar_df_para_zephyr_xlsx(
                    st.session_state.get("test_plan_df"),
                    st.session_state.get("jira_priority", "Medium"),
                    st.session_state.get("jira_labels", ""),
                    st.session_state.get("jira_description", ""),
                )
                st.dataframe(df_zephyr.head(20), use_container_width=True)
                st.caption(
                    "Mostrando primeiras 20 linhas dos dados preparados para Excel"
                )
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o preview do Zephyr: {e}")


def _render_export_section():  # noqa: C901, PLR0915
    """
    Renderiza a seção de downloads e exportações.
    Inclui suporte para: Markdown, PDF, Azure DevOps, Jira Zephyr e Xray.
    Todos os formulários seguem padrões de acessibilidade WCAG 2.1 Level AA.
    """
    st.divider()
    st.subheader("Downloads Disponíveis")

    # Preview dos arquivos antes do download
    _render_export_previews()

    col_azure, col_zephyr, col_xray = _render_basic_exports()

    # ==================================================
    #  OPÇÕES DE EXPORTAÇÃO (AZURE / ZEPHYR)
    # ==================================================
    if (
        st.session_state.get("test_plan_df") is not None
        and not st.session_state.get("test_plan_df").empty
    ):
        with st.expander(
            "⚙️ Opções de Exportação para Ferramentas Externas", expanded=False
        ):
            # Azure DevOps
            st.markdown("##### Azure DevOps")
            az_col1, az_col2 = st.columns(2)
            az_col1.text_input("Area Path:", key="area_path_input")
            az_col2.text_input("Atribuído a:", key="assigned_to_input")

            st.divider()

            # Jira Zephyr
            st.markdown("##### Jira Zephyr")
            st.selectbox(
                "Prioridade Padrão:",
                ["Medium", "High", "Low"],
                key="jira_priority",
            )
            st.text_input(
                "Labels (separadas por vírgula):",
                "QA-Oraculo",
                key="jira_labels",
            )
            accessible_text_area(
                label="Descrição Padrão",
                key="jira_description",
                height=100,
                help_text=(
                    "Descrição padrão enviada ao Jira ao criar o caso de teste. "
                    "Você pode editar para adicionar detalhes específicos da funcionalidade."
                ),
                placeholder="Exemplo: Caso de teste gerado automaticamente a partir da análise de requisitos.",
                st_api=st,
            )

            st.divider()

            # TestRail
            st.markdown("##### TestRail")
            tr_col1, tr_col2 = st.columns(2)
            tr_col1.text_input("Section:", key="testrail_section")
            tr_col2.selectbox(
                "Prioridade:",
                ["Medium", "High", "Low"],
                key="testrail_priority",
            )
            st.text_input(
                "References:",
                key="testrail_references",
                placeholder="PROJ-123,PROJ-456",
            )

            st.divider()

            # ======================================================================
            # Xray (Jira Test Management) - COM ACESSIBILIDADE COMPLETA
            # ======================================================================
            st.markdown("##### 🧪 Xray (Jira Test Management)")
            announce(
                "Xray: Ferramenta de gerenciamento de testes do Jira. Requer Test Repository Folder.",
                "info",
                st_api=st,
            )
            st.markdown(
                "⚠️ **Importante:** O diretório especificado em Test Repository Folder "
                "deve ser criado previamente no Xray antes da importação."
            )

            # Campo obrigatório com acessibilidade
            st.text_input(
                "Test Repository Folder (Obrigatório):",
                placeholder="Exemplo: TED, Pagamentos, Login",
                key="xray_test_folder",
                help=(
                    "Nome do diretório no Xray onde TODOS os testes deste arquivo serão salvos. "
                    "Este diretório deve existir no Xray. Campo obrigatório para exportação."
                ),
            )

            # Campos opcionais padrão do Xray
            with st.expander(
                "⚙️ Configurações Adicionais do Xray (Opcional)", expanded=False
            ):
                st.markdown("**📋 Campos Padrão do Xray/Jira:**")

                col1, col2 = st.columns(2)

                with col1:
                    st.text_input(
                        "Labels:",
                        placeholder="Ex: Automation, Regression",
                        key="xray_labels",
                        help="Etiquetas para todos os testes (separadas por vírgula). Melhora organização e filtros.",
                    )
                    st.text_input(
                        "Component:",
                        placeholder="Ex: Pagamentos",
                        key="xray_component",
                        help="Componente do Jira associado aos testes. Ajuda na rastreabilidade.",
                    )
                    st.text_input(
                        "Fix Version:",
                        placeholder="Ex: 1.0.0",
                        key="xray_fix_version",
                        help="Versão de correção do Jira. Indica em qual release o teste será executado.",
                    )

                with col2:
                    st.selectbox(
                        "Priority:",
                        ["", "Highest", "High", "Medium", "Low", "Lowest"],
                        key="xray_priority",
                        help="Prioridade padrão para todos os testes. Vazio = usar prioridade individual de cada teste.",
                    )
                    st.text_input(
                        "Assignee:",
                        placeholder="Ex: joao.silva",
                        key="xray_assignee",
                        help="Responsável pelos testes (username do Jira). Opcional.",
                    )
                    st.text_input(
                        "Test Set:",
                        placeholder="Ex: Sprint 10",
                        key="xray_test_set",
                        help="Test Set onde os testes serão agrupados. Útil para organizar por sprint ou release.",
                    )

                st.divider()

                st.markdown("**🔧 Campos Customizados do Seu Jira:**")
                st.markdown("Formato: `Nome_do_Campo=Valor` (um por linha)")

                accessible_text_area(
                    label="Campos Personalizados:",
                    key="xray_custom_fields",
                    height=120,
                    help_text=(
                        "Adicione campos customizados do seu Jira, um por linha.\n\n"
                        "Formato: NomeDoCampo=Valor\n\n"
                        "Exemplos práticos:\n"
                        "• Epic Link=PROJ-123\n"
                        "• Sprint=Sprint 10\n"
                        "• Story Points=5\n"
                        "• Team=Squad Core\n\n"
                        "Esses campos serão adicionados a TODOS os testes exportados."
                    ),
                    placeholder="Epic Link=PROJ-123\nSprint=Sprint 10\nTeam=QA Core",
                    st_api=st,
                )

        # ------------------------------------------------------
        # Dados para exportações
        # ------------------------------------------------------
        df_para_ferramentas = st.session_state.get("test_plan_df", pd.DataFrame())

        # Azure requer que os campos de área e responsável estejam preenchidos
        is_azure_disabled = not (
            st.session_state.get("area_path_input", "").strip()
            and st.session_state.get("assigned_to_input", "").strip()
        )

        csv_azure = gerar_csv_azure_from_df(
            df_para_ferramentas,
            st.session_state.get("area_path_input", ""),
            st.session_state.get("assigned_to_input", ""),
        )

        col_azure.download_button(
            "🚀 Azure (.csv)",
            _ensure_bytes(csv_azure),
            file_name=gerar_nome_arquivo_seguro(
                st.session_state.get("user_story_input", ""), "azure.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            disabled=is_azure_disabled,
            help="Preencha os campos no expander acima para habilitar.",
        )

        # Zephyr
        df_zephyr = preparar_df_para_zephyr_xlsx(
            df_para_ferramentas,
            st.session_state.get("jira_priority", "Medium"),
            st.session_state.get("jira_labels", ""),
            st.session_state.get("jira_description", ""),
        )
        excel_zephyr = to_excel(df_zephyr, sheet_name="Zephyr Import")
        excel_zephyr_bytes = _ensure_bytes(excel_zephyr)

        col_zephyr.download_button(
            "📊 Jira Zephyr (.xlsx)",
            excel_zephyr_bytes,
            file_name=gerar_nome_arquivo_seguro(
                st.session_state.get("user_story_input", ""), "zephyr.xlsx"
            ),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        # TestRail CSV
        csv_testrail = gerar_csv_testrail_from_df(
            df_para_ferramentas,
            st.session_state.get("testrail_section", ""),
            st.session_state.get("testrail_priority", "Medium"),
            "Test Case (Steps)",
            st.session_state.get("testrail_references", ""),
        )

        col_zephyr.download_button(
            "🧪 TestRail (.csv)",
            _ensure_bytes(csv_testrail),
            file_name=gerar_nome_arquivo_seguro(
                st.session_state.get("user_story_input", ""), "testrail.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

        # ======================================================================
        # EXPORTAÇÃO XRAY - Requer Test Repository Folder
        # ======================================================================
        xray_folder = st.session_state.get("xray_test_folder", "").strip()
        is_xray_disabled = not xray_folder

        # Monta dicionário de campos para o Xray CSV
        xray_fields = {}

        # Campos padrão do Xray (ordem importa no CSV!)
        if st.session_state.get("xray_labels", "").strip():
            xray_fields["Labels"] = st.session_state.get("xray_labels", "").strip()

        if st.session_state.get("xray_priority", "").strip():
            xray_fields["Priority"] = st.session_state.get("xray_priority", "").strip()

        if st.session_state.get("xray_component", "").strip():
            xray_fields["Component"] = st.session_state.get(
                "xray_component", ""
            ).strip()

        if st.session_state.get("xray_fix_version", "").strip():
            xray_fields["Fix Version"] = st.session_state.get(
                "xray_fix_version", ""
            ).strip()

        if st.session_state.get("xray_assignee", "").strip():
            xray_fields["Assignee"] = st.session_state.get("xray_assignee", "").strip()

        if st.session_state.get("xray_test_set", "").strip():
            xray_fields["Test Set"] = st.session_state.get("xray_test_set", "").strip()

        # Campos customizados do usuário (formato: Campo=Valor)
        custom_text = st.session_state.get("xray_custom_fields", "").strip()
        if custom_text:
            for raw_line in custom_text.split("\n"):
                stripped_line = raw_line.strip()
                if "=" in stripped_line:
                    key, value = stripped_line.split("=", 1)
                    xray_fields[key.strip()] = value.strip()

        csv_xray = gerar_csv_xray_from_df(
            df_para_ferramentas,
            xray_folder,
            custom_fields=xray_fields if xray_fields else None,
        )

        col_xray.download_button(
            "🧪 Xray (.csv)",
            _ensure_bytes(csv_xray),
            file_name=gerar_nome_arquivo_seguro(
                st.session_state.get("user_story_input", ""), "xray.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            disabled=is_xray_disabled,
            help=(
                "Preencha o Test Repository Folder no expander acima para habilitar. "
                "O formato é compatível com Xray Test Case Importer (CSV). "
                "Use navegação por teclado (Tab) para acessar o formulário acima."
            ),
        )


def _render_new_analysis_button():
    """
    Renderiza o botão de nova análise com função de reset.
    """
    st.divider()

    def resetar_fluxo():
        """Reseta o estado completo da sessão, incluindo a flag de histórico."""
        # Remove explicitamente a flag antes de chamar reset_session
        st.session_state.pop("history_saved", None)
        reset_session()  # já limpa user_story_input, analysis_state, etc.

    accessible_button(
        label="🔄 Realizar Nova Análise",
        key="nova_analise_button",
        context="Limpa os resultados anteriores e reinicia o fluxo de análise da User Story.",
        type="primary",
        use_container_width=True,
        on_click=resetar_fluxo,
        st_api=st,
    )


# ==========================================================
#  Página Principal — Análise de User Story (Refatorada)
# ==========================================================
def render_main_analysis_page():  # noqa: C901, PLR0912, PLR0915
    """
    Fluxo da página principal (refatorado em funções menores):

    1) Entrada da User Story (text_area) + Execução da análise via IA.
    2) Edição humana dos blocos sugeridos (form).
    3) Geração do Plano de Testes com base na análise refinada (IA).
    4) Exportações (MD, PDF, CSV Azure, XLSX Zephyr).
    5) Botão para iniciar uma nova análise (reset).
    """
    # ------------------------------------------------------
    # 1) Entrada e execução da análise inicial
    # ------------------------------------------------------
    if not st.session_state.get("analysis_finished", False):

        # Container de cabeçalho para garantir ordem
        with st.container():
            st.title("🤖 QA Oráculo")
            st.markdown(
                """
            ###  Olá, viajante do código!  
            Sou o **Oráculo de QA**, pronto para analisar suas User Stories e revelar ambiguidades, riscos e critérios de aceitação.  
            Cole sua história abaixo e inicie a jornada da qualidade! 🚀
            """
            )

        # Se ainda não há análise no estado, exibimos o input inicial
        if not st.session_state.get("analysis_state"):
            with st.container():
                _render_user_story_input()

        # ------------------------------------------------------
        # 2) Edição dos blocos gerados pela IA
        # ------------------------------------------------------
        if st.session_state.get("analysis_state"):
            st.divider()

            # Enquanto a edição não for salva, mostramos o formulário editável
            if not st.session_state.get("show_generate_plan_button"):
                _render_analysis_edit_form()

        # ------------------------------------------------------
        # 3) Geração do Plano de Testes (após edição)
        # ------------------------------------------------------
        if st.session_state.get("show_generate_plan_button"):
            _render_test_plan_generation()

    # ------------------------------------------------------
    # 4) Tela de resultados e exportações
    # ------------------------------------------------------
    if st.session_state.get("analysis_finished"):
        _render_results_section()
        _render_export_section()

        # ------------------------------------------------------
        # Botão para resetar e reiniciar o fluxo
        # ------------------------------------------------------
        _render_new_analysis_button()


# ==========================================================
#  Página de Histórico
# ==========================================================
def _render_history_filters():
    """Renderiza filtros de histórico."""
    with st.expander("🔍 Filtros e Busca", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            search_text = st.text_input(
                "Buscar",
                placeholder="Digite palavras-chave...",
                help="Busca em User Story, análise e plano de testes",
            )

        with col2:
            date_filter = st.selectbox(
                "Período",
                options=["Todos", "Última semana", "Último mês", "Últimos 3 meses"],
                help="Filtrar por data de criação",
            )

        with col3:
            type_filter = st.multiselect(
                "Tipo",
                options=["Com análise", "Com plano de testes"],
                default=[],
                help="Filtrar por tipo de conteúdo (vazio = todos)",
                placeholder="Selecione as opções",
            )

        return {
            "search_text": search_text.lower() if search_text else "",
            "date_filter": date_filter,
            "type_filter": type_filter,
        }


def _apply_history_filters(entries: list, filters: dict) -> list:
    """Aplica filtros aos registros do histórico."""
    if not filters:
        return entries

    filtered = entries

    # Filtro de texto
    if filters["search_text"]:
        search = filters["search_text"]
        filtered = [
            e
            for e in filtered
            if search in (e.get("user_story", "") or "").lower()
            or search in (e.get("analysis_report", "") or "").lower()
            or search in (e.get("test_plan_report", "") or "").lower()
        ]

    # Filtro de data
    if filters["date_filter"] != "Todos":
        from datetime import datetime, timedelta

        now = datetime.now()

        if filters["date_filter"] == "Última semana":
            cutoff = now - timedelta(days=7)
        elif filters["date_filter"] == "Último mês":
            cutoff = now - timedelta(days=30)
        else:  # Últimos 3 meses
            cutoff = now - timedelta(days=90)

        filtered = [
            e for e in filtered if _parse_date_safe(dict(e).get("created_at")) >= cutoff
        ]

    # Filtro de tipo
    if filters["type_filter"]:
        if "Com análise" in filters["type_filter"]:
            filtered = [e for e in filtered if dict(e).get("analysis_report")]
        if "Com plano de testes" in filters["type_filter"]:
            filtered = [e for e in filtered if dict(e).get("test_plan_report")]

    return filtered


def _parse_date_safe(date_str):
    """Converte string de data para datetime de forma segura."""
    from datetime import datetime

    try:
        if isinstance(date_str, datetime):
            return date_str
        if not date_str:
            return datetime.min
        return datetime.fromisoformat(date_str)
    except Exception:
        return datetime.min


def _render_history_page_impl():  # noqa: C901, PLR0912, PLR0915
    """
    Exibe o histórico de análises realizadas e permite:
      • Visualizar detalhes de cada análise
      • Excluir análises individuais
      • Excluir todo o histórico

    CORREÇÕES APLICADAS:
    - Conversão robusta de query_params para int
    - Tratamento de None/string vazia
    - Logs de debug para rastreamento
    - Fallback para dict() em sqlite3.Row
    """

    st.title("📖 Histórico de Análises")
    st.markdown(
        "Aqui você pode rever todas as análises de User Stories já realizadas pelo Oráculo."
    )

    # ==========================================================
    #  BLOCO DE EXCLUSÃO (individual e total)
    # ==========================================================

    #  EXCLUSÃO INDIVIDUAL (um único registro)
    if st.session_state.get("confirm_delete_id"):
        with st.container(border=True):
            announce(
                f"Tem certeza que deseja excluir a análise ID {st.session_state['confirm_delete_id']}?",
                "warning",
                st_api=st,
            )

            col_del_1, col_del_2 = st.columns(2)

            if col_del_1.button(
                "✅ Confirmar Exclusão",
                key="confirmar_delete",
                use_container_width=True,
            ):
                analysis_id = st.session_state["confirm_delete_id"]
                result = delete_analysis_by_id(analysis_id)
                st.session_state.pop("confirm_delete_id", None)

                if result:
                    announce(
                        f"Análise {analysis_id} removida com sucesso.",
                        "success",
                        st_api=st,
                    )
                else:
                    announce(
                        "Não foi possível excluir a análise selecionada.",
                        "error",
                        st_api=st,
                    )

                st.rerun()

            if col_del_2.button(
                "❌ Cancelar", key="cancelar_delete", use_container_width=True
            ):
                st.session_state.pop("confirm_delete_id", None)
                announce("Nenhuma exclusão foi realizada.", "info", st_api=st)
                st.rerun()

    #  EXCLUSÃO TOTAL DO HISTÓRICO
    if st.session_state.get("confirm_clear_all"):
        with st.container(border=True):
            announce(
                "Tem certeza que deseja excluir TODO o histórico de análises?",
                "warning",
                st_api=st,
            )
            col_all_1, col_all_2 = st.columns(2)

            if col_all_1.button(
                "🗑️ Confirmar exclusão total",
                key="confirmar_delete_all",
                use_container_width=True,
            ):
                removed_count = clear_history()
                st.session_state.pop("confirm_clear_all", None)
                if removed_count:
                    announce(
                        f"{removed_count} análises foram removidas.",
                        "success",
                        st_api=st,
                    )
                else:
                    announce(
                        "Nenhuma análise foi removida.",
                        "warning",
                        st_api=st,
                    )
                st.rerun()

            if col_all_2.button(
                "❌ Cancelar", key="cancelar_delete_all", use_container_width=True
            ):
                st.session_state.pop("confirm_clear_all", None)
                announce("Nenhuma exclusão foi realizada.", "info", st_api=st)
                st.rerun()

    # ==========================================================
    #  BUSCA E CONVERSÃO DO ID SELECIONADO (CORRIGIDO)
    # ==========================================================

    history_entries = get_all_analysis_history()

    # Filtros de busca e data
    filters = _render_history_filters()
    history_entries = _apply_history_filters(history_entries, filters)

    # Debug logs

    # Pega o ID da URL de forma segura
    raw_id = st.query_params.get("analysis_id")

    selected_id = None

    if raw_id:
        # query_params pode retornar lista, string ou None
        if isinstance(raw_id, list):
            raw_id = raw_id[0] if raw_id else None

        if raw_id:
            try:
                selected_id = int(raw_id)
            except (ValueError, TypeError):
                selected_id = None

    # Cria container vazio no topo para manter compatibilidade com testes
    with st.container():
        pass

    # ----------------------------------------------------------
    #  Modo de visualização detalhada
    # ----------------------------------------------------------
    if selected_id:

        try:
            analysis_entry = get_analysis_by_id(selected_id)

            if analysis_entry and not isinstance(analysis_entry, dict):
                analysis_entry = dict(analysis_entry)

        except (TypeError, ValueError):
            analysis_entry = None

        if analysis_entry:
            accessible_button(
                label="⬅️ Voltar para a Lista",
                key="btn_voltar_lista",
                context="Retorna à lista principal de análises, limpando os filtros e parâmetros atuais.",
                type="secondary",
                on_click=lambda: st.query_params.clear(),
                st_api=st,
            )

            created = analysis_entry.get("created_at")

            if isinstance(created, str):
                titulo_data = created.split()[0]
            elif hasattr(created, "strftime"):
                titulo_data = created.strftime("%Y-%m-%d")
            else:
                titulo_data = str(created)

            st.markdown(f"### Análise de {titulo_data}")

            #  User Story
            with st.expander("📄 User Story Analisada", expanded=True):
                user_story = (
                    analysis_entry.get("user_story") or "⚠️ User Story não disponível."
                )
                st.code(user_story, language="gherkin")

            #  Relatório de Análise
            with st.expander("📘 Relatório de Análise da IA", expanded=False):
                relatorio_analise = (
                    analysis_entry.get("analysis_report")
                    or "⚠️ Relatório de análise não disponível."
                )
                st.markdown(
                    clean_markdown_report(relatorio_analise),
                    unsafe_allow_html=True,
                )

            #  Plano de Testes
            _render_history_test_plan(analysis_entry)

            st.divider()

            st.markdown(
                "<p style='color:gray;font-size:13px;'>Use TAB para navegar entre seções.</p>",
                unsafe_allow_html=True,
            )

        else:
            announce("Análise não encontrada.", "error", st_api=st)
            accessible_button(
                label="⬅️ Voltar para a Lista",
                key="btn_voltar_lista",
                context="Retorna à lista principal de análises e limpa os parâmetros de busca atuais.",
                type="secondary",
                on_click=lambda: st.query_params.clear(),
                st_api=st,
            )

    # ----------------------------------------------------------
    # 📚 Modo de listagem geral (todas as análises)
    # ----------------------------------------------------------
    else:
        if not history_entries:
            announce(
                "Ainda não há análises no histórico. Realize uma nova análise para começar.",
                "info",
                st_api=st,
            )

            return

        # ==========================================================
        # 🔍 Busca e Filtros
        # ==========================================================
        # Aplica filtros (já aplicados acima, apenas mantendo a referência)
        filtered_entries = history_entries

        st.divider()

        # 🧹 Excluir todo histórico
        if accessible_button(
            label="🗑️ Excluir TODO o Histórico",
            key="btn_limpar_historico",
            context="Remove todos os registros de análises armazenados. Esta ação é irreversível.",
            st_api=st,
        ):
            st.session_state["confirm_clear_all"] = True
            st.rerun()

        st.divider()
        st.markdown("### 📜 Histórico de Análises Realizadas")

        # Se não há resultados após filtros
        if not filtered_entries:
            announce(
                "Nenhuma análise encontrada com os filtros aplicados.",
                "info",
                st_api=st,
            )
            return

        # ==========================================================
        #  COMPARADOR DE ANÁLISES E EXPORTAÇÃO EM LOTE
        # ==========================================================

        # Checkbox para ativar modo de comparação ou exportação em lote
        col_actions_1, col_actions_2, col_actions_3 = st.columns([1, 1, 2])
        with col_actions_1:
            comparison_mode = st.checkbox(
                "🔄 Modo de Comparação", key="comparison_mode_active"
            )
        with col_actions_2:
            batch_export_mode = st.checkbox(
                "📦 Exportação em Lote", key="batch_export_mode_active"
            )

        selected_for_comparison = []
        selected_for_batch = []

        if comparison_mode:
            st.info("Selecione exatamente 2 análises abaixo para comparar.")
        if batch_export_mode:
            st.info("Selecione uma ou mais análises para exportar em lote (ZIP).")

        # Cria um card/expander para cada item filtrado
        for entry in filtered_entries:
            entry_dict = dict(entry) if not isinstance(entry, dict) else entry
            created_at = entry_dict.get("created_at")
            user_story_preview = entry_dict.get("user_story", "")[:80]
            entry_id = entry_dict.get("id")

            # Formata data de forma segura
            if isinstance(created_at, str):
                data_formatada = created_at.split()[0]
            elif hasattr(created_at, "strftime"):
                data_formatada = created_at.strftime("%d/%m/%Y %H:%M")
            else:
                data_formatada = str(created_at)

            # Lógica de seleção para comparação e exportação em lote
            is_selected_comparison = False
            is_selected_batch = False

            if comparison_mode:
                is_selected_comparison = st.checkbox(
                    f"Comparar #{entry_id}",
                    key=f"chk_compare_{entry_id}",
                    value=entry_id in st.session_state.get("comparison_ids", []),
                )
                if is_selected_comparison:
                    selected_for_comparison.append(entry_dict)

            if batch_export_mode:
                is_selected_batch = st.checkbox(
                    f"Exportar #{entry_id}",
                    key=f"chk_batch_{entry_id}",
                    value=entry_id in st.session_state.get("batch_export_ids", []),
                )
                if is_selected_batch:
                    selected_for_batch.append(entry_id)

            with st.expander(
                f"🧩 {data_formatada} — {user_story_preview}...",
                expanded=False,
            ):
                st.markdown(f"**🕒 Data:** {data_formatada}")
                st.markdown(f"**📘 User Story:**\n\n> {user_story_preview}...")
                st.markdown(
                    '<div data-testid="card-historico"></div>', unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)

                with col1:
                    if accessible_button(
                        label="🔍 Ver Detalhes",
                        key=f"btn_detalhes_{entry_id}",
                        context=f"Exibe os detalhes completos da análise #{entry_id}, incluindo critérios, perguntas e pontos ambíguos.",
                        type="primary",
                        use_container_width=True,
                        st_api=st,
                    ):
                        st.query_params["analysis_id"] = str(entry_id)
                        st.rerun()

                with col2:
                    if accessible_button(
                        label="🗑️ Excluir",
                        key=f"btn_excluir_{entry_id}",
                        context=f"Remove permanentemente a análise #{entry_id}. Esta ação não pode ser desfeita.",
                        use_container_width=True,
                        st_api=st,
                    ):
                        st.session_state["confirm_delete_id"] = entry_id
                        st.rerun()

        # Renderiza a comparação se 2 itens forem selecionados
        if comparison_mode and len(selected_for_comparison) == 2:
            st.divider()
            st.markdown("### ⚖️ Comparação de Análises")

            item_a = selected_for_comparison[0]
            item_b = selected_for_comparison[1]

            col_comp_1, col_comp_2 = st.columns(2)

            with col_comp_1:
                st.subheader(f"Análise #{item_a['id']}")
                st.caption(f"Data: {item_a.get('created_at')}")
                st.markdown("#### User Story")
                st.code(item_a.get("user_story"), language="gherkin")
                st.markdown("#### Relatório")
                with st.container(height=300):
                    st.markdown(
                        clean_markdown_report(item_a.get("analysis_report", "")),
                        unsafe_allow_html=True,
                    )

            with col_comp_2:
                st.subheader(f"Análise #{item_b['id']}")
                st.caption(f"Data: {item_b.get('created_at')}")
                st.markdown("#### User Story")
                st.code(item_b.get("user_story"), language="gherkin")
                st.markdown("#### Relatório")
                with st.container(height=300):
                    st.markdown(
                        clean_markdown_report(item_b.get("analysis_report", "")),
                        unsafe_allow_html=True,
                    )

            st.divider()
            st.markdown("### 🔍 Diferenças (Diff)")

            # Importação lazy para evitar dependência circular no topo
            from .utils.diff import generate_html_diff

            tab_diff_us, tab_diff_report = st.tabs(
                ["User Story", "Relatório de Análise"]
            )

            with tab_diff_us:
                diff_html_us = generate_html_diff(
                    item_a.get("user_story", ""), item_b.get("user_story", "")
                )
                st.components.v1.html(diff_html_us, height=400, scrolling=True)

            with tab_diff_report:
                diff_html_report = generate_html_diff(
                    item_a.get("analysis_report", ""), item_b.get("analysis_report", "")
                )
                st.components.v1.html(diff_html_report, height=600, scrolling=True)

                st.code(item_b.get("user_story"), language="gherkin")
                st.markdown("#### Relatório")
                with st.container(height=300):
                    st.markdown(
                        clean_markdown_report(item_b.get("analysis_report", "")),
                        unsafe_allow_html=True,
                    )

        elif comparison_mode and len(selected_for_comparison) > 2:
            st.warning("⚠️ Selecione apenas 2 análises para comparar.")

        # Renderiza o botão de exportação em lote se houver seleções
        if batch_export_mode and len(selected_for_batch) > 0:
            st.divider()
            st.markdown(
                f"### 📦 Exportação em Lote ({len(selected_for_batch)} análises selecionadas)"
            )

            from .utils.exporters import export_batch_zip
            from .progress import track_progress

            try:
                # Cria lista de steps para o progresso
                steps = [
                    f"Exportando análise {i+1}/{len(selected_for_batch)}"
                    for i in range(len(selected_for_batch))
                ]

                # Usa track_progress para mostrar barra de progresso
                with track_progress(steps, "Exportação em lote") as tracker:
                    # Define callback que atualiza o tracker
                    def progress_callback(step_name):
                        tracker.update(step_name)

                    batch_zip = export_batch_zip(selected_for_batch, progress_callback)

                st.download_button(
                    label=f"📥 Baixar ZIP com {len(selected_for_batch)} análises",
                    data=batch_zip,
                    file_name=f"qa_oraculo_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    help="Baixa um arquivo ZIP contendo Markdown e PDF de todas as análises selecionadas",
                )
            except Exception as e:
                logger.error(f"Erro ao gerar batch export: {e}")
                st.error(f"❌ Erro ao gerar exportação em lote: {e}")

        st.markdown(
            "<p style='color:gray;font-size:13px;'>Pressione TAB para navegar pelos registros ou ENTER para expandir.</p>",
            unsafe_allow_html=True,
        )


def _render_history_page_test_mode(st_api):  # noqa: C901, PLR0911, PLR0912, PLR0915
    """Versão simplificada do histórico para testes unitários legados."""

    st_api.title("📖 Histórico de Análises")
    st_api.markdown(
        "Aqui você pode rever todas as análises de User Stories já realizadas pelo Oráculo."
    )

    confirm_id = st_api.session_state.get("confirm_delete_id")
    if confirm_id:
        if st_api.button("✅ Confirmar Exclusão", key="confirmar_delete"):
            resultado = delete_analysis_by_id(confirm_id)
            st_api.session_state.pop("confirm_delete_id", None)
            if resultado:
                st_api.success(f"Análise {confirm_id} removida com sucesso.")
            else:
                st_api.error("Não foi possível excluir a análise selecionada.")
            return

        if st_api.button("❌ Cancelar", key="cancelar_delete"):
            st_api.session_state.pop("confirm_delete_id", None)
            st_api.info("Nenhuma exclusão foi realizada.")
            return

        st_api.info("Nenhuma exclusão foi realizada.")
        return

    confirm_all = st_api.session_state.get("confirm_clear_all")
    if confirm_all:
        if st_api.button("🗑️ Confirmar exclusão total", key="confirmar_delete_all"):
            removidos = clear_history()
            st_api.session_state.pop("confirm_clear_all", None)
            if removidos:
                st_api.success(f"{removidos} análises foram removidas.")
            else:
                st_api.warning("Nenhuma análise foi removida.")
            return

        if st_api.button("❌ Cancelar", key="cancelar_delete_all"):
            st_api.session_state.pop("confirm_clear_all", None)
            st_api.info("Nenhuma exclusão foi realizada.")
            return

    history_entries = get_all_analysis_history()

    raw_id = (
        st_api.query_params.get("analysis_id")
        if hasattr(st_api, "query_params")
        else None
    )
    selected_id = None
    if raw_id:
        if isinstance(raw_id, list):
            raw_id = raw_id[0] if raw_id else None
        try:
            selected_id = int(raw_id) if raw_id else None
        except (TypeError, ValueError):
            selected_id = None

    if selected_id:
        entry = get_analysis_by_id(selected_id)
        if entry:
            entry_dict = dict(entry) if not isinstance(entry, dict) else entry
            created = entry_dict.get("created_at", "-")
            st_api.markdown(f"### Análise de {created}")
            st_api.code(entry_dict.get("user_story", ""), language="gherkin")
            if entry_dict.get("analysis_report"):
                st_api.markdown(entry_dict["analysis_report"])
            if entry_dict.get("test_plan_report"):
                st_api.markdown(entry_dict["test_plan_report"])
            else:
                st_api.info("Nenhum plano de testes foi gerado para esta análise.")
        else:
            st_api.error("Análise não encontrada.")
        return

    if not history_entries:
        st_api.info(
            "Ainda não há análises no histórico. Realize uma nova análise para começar."
        )
        return

    st_api.container()
    for entry in history_entries:
        entry_dict = dict(entry) if not isinstance(entry, dict) else entry
        created = entry_dict.get("created_at", "-")
        st_api.markdown(f"### Análise de {created}")


def render_history_page(st_api=None):
    """Wrapper público que mantém compatibilidade com testes antigos."""

    if st_api is not None:
        return _render_history_page_test_mode(st_api)

    return _render_history_page_impl()


# ==========================================================
#  Função principal — inicializa o app QA Oráculo
# ==========================================================
def main():
    """
    Função principal da aplicação Streamlit.

    Responsabilidades:
    ------------------
    • Configura layout e título da página.
    • Inicializa o banco de dados (SQLite).
    • Inicializa o estado global (session_state).
    • Aplica estilos e informações de acessibilidade.
    • Cria o menu lateral de navegação.
    • Carrega dinamicamente a página selecionada.
    """
    # ------------------------------------------------------
    #  Configuração inicial da interface
    # ------------------------------------------------------
    st.set_page_config(page_title="QA Oráculo", layout="wide")

    # ------------------------------------------------------
    #  Inicialização de banco e estado
    # ------------------------------------------------------
    init_db()
    initialize_state()
    # ------------------------------------------------------
    # ♿ Acessibilidade global
    # ------------------------------------------------------
    apply_accessible_styles()

    # ------------------------------------------------------
    #  Mapa de páginas (sidebar)
    # ------------------------------------------------------
    pages = {
        "Analisar User Story": render_main_analysis_page,
        "Histórico de Análises": render_history_page,
    }

    selected_page = st.sidebar.radio("Navegação", list(pages.keys()))

    # Toggle de modo escuro removido por decisão de design
    # from .a11y import render_dark_mode_toggle
    # render_dark_mode_toggle()

    st.sidebar.divider()

    render_keyboard_shortcuts_guide()
    render_accessibility_info()
    pages[selected_page]()


# ==========================================================
# Ponto de entrada do aplicativo
# ==========================================================
if __name__ == "__main__":  # pragma: no cover - entrada manual via streamlit
    # NOTA: Para executar o app, use `streamlit run main.py` na raiz do projeto.
    # Não execute este arquivo diretamente (`streamlit run qa_core/app.py`).
    #
    # Este bloco é mantido para:
    #   • Compatibilidade com testes que importam o módulo
    #   • Execução via main.py (entry point correto)
    main()

# ==========================================================
# ✅ FIM DO ARQUIVO — QA ORÁCULO
# ==========================================================
# 🔹 Este app segue o padrão modular QA Oráculo:
#    - qa_core/database.py     → persistência
#    - qa_core/utils.py        → formatação e exportações
#    - qa_core/graph.py        → integração com LangGraph
#    - qa_core/pdf_generator.py → relatórios em PDF
#    - qa_core/state_manager.py → controle de estado Streamlit
#
# 🔹 Funções críticas cobertas por testes unitários (pytest):
#    - Testes de fluxo (criação → edição → exportação)
#    - Testes de histórico (exclusão individual e total)
#    - Testes de geração de CSV (Azure) e XLSX (Zephyr)
#
# 🔹 Requisitos de qualidade QA Oráculo:
#    • PEP8 + Black
#    • A11Y (acessibilidade) — labels e navegação por teclado
#    • data-testid únicos para automação E2E
#    • Banco testável em memória (SQLite :memory:)
# ==========================================================
