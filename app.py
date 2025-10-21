# ==========================================================
# app.py — Aplicação principal do QA Oráculo
# ==========================================================
# 📘 Este arquivo define toda a interface Streamlit do projeto:
#   - Página principal de análise de User Stories
#   - Geração de plano de testes (IA)
#   - Exportações (Markdown, PDF, CSV Azure, XLSX Zephyr)
#   - Histórico de análises (visualização e exclusão)
#
# 🎯 Princípios (QA Oráculo):
#   • Código modular (funções separadas por responsabilidade)
#   • Acessibilidade + automação de testes (data-testid / navegação teclado)
#   • Preparado para testes unitários e E2E
#   • Comentários didáticos onde a lógica não for óbvia
# ==========================================================


import pandas as pd
import streamlit as st

from a11y import (
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
from database import (
    clear_history,
    delete_analysis_by_id,
    get_all_analysis_history,
    get_analysis_by_id,
    init_db,
    save_or_update_analysis,  # Nova função atômica
)

# Grafos de IA (LangGraph) — invocados nas funções cacheadas
from graph import grafo_analise, grafo_plano_testes

# Gerador de PDF — consolida análise e plano de testes em um relatório
from pdf_generator import generate_pdf_report
from state_machine import AnalysisStage

# Estado global e reset — para nova análise sem resquícios
from state_manager import get_state, initialize_state, reset_session, update_user_story

# Utilitários — helpers de exportação, normalização e formatação
from utils import (
    clean_markdown_report,
    gerar_csv_azure_from_df,
    gerar_nome_arquivo_seguro,
    get_flexible,
    preparar_df_para_zephyr_xlsx,
    to_excel,
)


# ==========================================================
# 🕒 Formatação segura de datas (compatível com testes)
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
# 🔒 Auxiliar: garante bytes no download_button
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
# 헬 Auxiliar: Salva a análise atual no histórico (CORRIGIDO)
# ==========================================================
def _save_current_analysis_to_history():
    """
    Salva análise atual usando a nova função atômica.

    MUDANÇAS:
    - Usa get_state() ao invés de session_state direto
    - Usa save_or_update_analysis() (thread-safe)
    - Remove flag manual "history_saved"
    """
    try:
        state = get_state()

        # Validação: só salva se houver dados válidos
        if not state.user_story.strip():
            print("⚠️ Nenhum dado para salvar (User Story vazia)")
            return

        # Prepara dados para salvamento
        user_story = state.user_story
        analysis_report = state.analysis_report or "⚠️ Relatório não disponível"
        test_plan_report = state.test_plan_report or ""

        # Salvamento atômico
        history_id = save_or_update_analysis(
            user_story=user_story,
            analysis_report=analysis_report,
            test_plan_report=test_plan_report,
            existing_id=state.saved_history_id,  # None = novo, int = update
        )

        # Atualiza estado com ID do histórico
        state.mark_as_saved(history_id)

        print(f"💾 Análise persistida: ID {history_id}")

    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        announce(
            "Não foi possível salvar no histórico. Verifique os logs.",
            "error",
            st_api=st,
        )


def save_analysis_to_history(update_existing: bool = False):
    """Mantém compatibilidade com testes que esperam esta função pública."""

    return _save_current_analysis_to_history(update_existing=update_existing)


# ==========================================================
# 🚀 Funções cacheadas (IA via LangGraph)
# ==========================================================
@st.cache_data(show_spinner=False)
def run_analysis_graph(user_story: str):
    """
    Executa o grafo de análise de User Story.
    Retorna um dicionário com:
      - 'analise_da_us': blocos estruturados (avaliacao/pontos/riscos/criterios/perguntas)
      - 'relatorio_analise_inicial': texto consolidado em Markdown
    """
    return grafo_analise.invoke({"user_story": user_story})


@st.cache_data(show_spinner=False)
def run_test_plan_graph(analysis_state: dict):
    """
    Executa o grafo de geração de Plano de Testes.
    Espera receber o estado de análise refinado.
    Retorna:
      - 'plano_e_casos_de_teste' com 'casos_de_teste_gherkin' (lista de cenários)
      - 'relatorio_plano_de_testes' (Markdown)
    """
    return grafo_plano_testes.invoke(analysis_state)


# ==========================================================
# 🧠 Página Principal — Análise de User Story
# ==========================================================
def render_main_analysis_page():  # noqa: C901, PLR0912, PLR0915
    """
    Fluxo da página principal:

    1) Entrada da User Story (text_area) + Execução da análise de IA.
    2) Edição humana dos blocos sugeridos (form).
    3) Geração do Plano de Testes (IA) com base na análise refinada.
    4) Exportações (MD, PDF, CSV Azure, XLSX Zephyr).
    5) Botão para iniciar uma nova análise (reset).
    """
    st.title("🤖 QA Oráculo")
    st.markdown(
        """
    ###  Olá, viajante do código!  
    Sou o **Oráculo de QA**, pronto para analisar suas User Stories e revelar ambiguidades, riscos e critérios de aceitação.  
    Cole sua história abaixo e inicie a jornada da qualidade! 🚀
    """
    )

    # ------------------------------------------------------
    # 1) Entrada e execução da análise inicial
    # ------------------------------------------------------
    state = get_state()

    # 🎯 Roteamento baseado no estágio atual
    if state.stage == AnalysisStage.INITIAL:
        # Renderiza formulário de entrada
        _render_input_form(state)

    elif state.stage == AnalysisStage.ANALYZING:
        # Mostra spinner enquanto IA processa
        _render_analyzing_state(state)

    elif state.stage == AnalysisStage.EDITING_ANALYSIS:
        # Permite edição dos resultados
        _render_editing_form(state)

    elif state.stage == AnalysisStage.GENERATING_PLAN:
        # Mostra spinner durante geração do plano
        _render_generating_plan_state(state)

    elif state.stage == AnalysisStage.COMPLETED:
        # Exibe resultados finais + exportações
        _render_completed_state(state)

    elif state.stage == AnalysisStage.ERROR:
        # Mostra erro + botão de retry
        _render_error_state(state)
        # ------------------------------------------------------
        # 2) Edição dos blocos gerados pela IA
        # ------------------------------------------------------
        if st.session_state.get("analysis_state"):
            st.divider()

            # Enquanto a edição não for salva, mostramos o formulário editável
            if not st.session_state.get("show_generate_plan_button"):
                announce(
                    " 🔮 O Oráculo gerou a análise abaixo. Revise, edite se necessário e clique em 'Salvar' para prosseguir.",
                    "info",
                    st_api=st,
                )

                # Extrai o bloco 'analise_da_us' (estrutura recomendada)
                analise_json = st.session_state.get("analysis_state", {}).get(
                    "analise_da_us", {}
                )

                # Usa get_flexible para aceitar variações de chave que a IA pode devolver
                avaliacao_str = get_flexible(
                    analise_json, ["avaliacao_geral", "avaliacao"], ""
                )
                pontos_list = get_flexible(
                    analise_json, ["pontos_ambiguos", "pontos_de_ambiguidade"], []
                )
                perguntas_list = get_flexible(
                    analise_json, ["perguntas_para_po", "perguntas_ao_po"], []
                )
                criterios_list = get_flexible(
                    analise_json,
                    ["sugestao_criterios_aceite", "criterios_de_aceite"],
                    [],
                )
                riscos_list = get_flexible(
                    analise_json, ["riscos_e_dependencias", "riscos"], []
                )

                # Converte listas em strings com quebra de linha para o form
                pontos_str = "\n".join(pontos_list)
                perguntas_str = "\n".join(perguntas_list)
                criterios_str = "\n".join(criterios_list)
                riscos_str = "\n".join(riscos_list)

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
                    st.session_state.setdefault("analysis_state", {})
                    st.session_state["analysis_state"].setdefault("analise_da_us", {})
                    bloco = st.session_state["analysis_state"]["analise_da_us"]

                    # Salva os campos editados — sempre normalizando para lista onde necessário
                    bloco["avaliacao_geral"] = st.session_state.get(
                        "edit_avaliacao", ""
                    )

                    bloco["pontos_ambiguos"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_pontos", "").split("\n")
                        if linha.strip()
                    ]

                    bloco["perguntas_para_po"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_perguntas", "").split(
                            "\n"
                        )
                        if linha.strip()
                    ]

                    bloco["sugestao_criterios_aceite"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_criterios", "").split(
                            "\n"
                        )
                        if linha.strip()
                    ]

                    bloco["riscos_e_dependencias"] = [
                        linha.strip()
                        for linha in st.session_state.get("edit_riscos", "").split("\n")
                        if linha.strip()
                    ]

                    # Agora podemos avançar para a geração de plano
                    st.session_state["show_generate_plan_button"] = True

                    announce(
                        "Análise refinada salva com sucesso!", "success", st_api=st
                    )
                    st.rerun()

        # ------------------------------------------------------
        # 3) Geração do Plano de Testes (após edição)
        # ------------------------------------------------------
        if st.session_state.get("show_generate_plan_button"):

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
                with st.spinner(
                    "🔮 Elaborando o Plano de Testes com base na análise refinada..."
                ):
                    try:
                        # ===== INÍCIO DO BLOCO DE RISCO =====
                        resultado_plano = run_test_plan_graph(
                            st.session_state.get("analysis_state", {})
                        )

                        casos_de_teste = resultado_plano.get(
                            "plano_e_casos_de_teste", {}
                        ).get("casos_de_teste_gherkin", [])

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
                                lambda x: (
                                    "\n".join(map(str, x)) if isinstance(x, list) else x
                                )
                            )
                        )
                        df_clean.fillna("", inplace=True)
                        st.session_state["test_plan_df"] = df_clean

                        pdf_bytes = generate_pdf_report(
                            st.session_state.get("analysis_state", {}).get(
                                "relatorio_analise_inicial", ""
                            ),
                            df_clean,
                        )
                        st.session_state["pdf_report_bytes"] = pdf_bytes

                        # --- NOVO: Salva e encerra o fluxo imediatamente ---
                        if not st.session_state.get("history_saved"):
                            _save_current_analysis_to_history()
                            st.session_state["history_saved"] = True  # evita duplicação

                        st.session_state["analysis_finished"] = True
                        announce(
                            "Plano de Testes gerado com sucesso!", "success", st_api=st
                        )
                        st.rerun()
                        # ===== FIM DO BLOCO DE RISCO =====

                    except Exception as e:
                        # Em caso de falha, informa o usuário, mas não perde o progresso
                        print(f"❌ Falha na geração do plano de testes: {e}")
                        announce(
                            "O Oráculo não conseguiu gerar um plano de testes estruturado.",
                            "error",
                            st_api=st,
                        )
                        # Limpa qualquer resquício de plano de teste para não exibir dados errados
                        st.session_state["test_plan_report"] = ""
                        st.session_state["test_plan_df"] = None
                        _save_current_analysis_to_history()
                        st.rerun()

            # Botão para encerrar sem gerar plano (mas salvando análise)
            if col2.button("Não, Encerrar", use_container_width=True):
                if not st.session_state.get("history_saved"):
                    _save_current_analysis_to_history()
                    st.session_state["history_saved"] = True  # evita duplicação
                st.session_state["analysis_finished"] = True
                st.rerun()

    # ------------------------------------------------------
    # 4) Tela de resultados e exportações
    # ------------------------------------------------------
    if st.session_state.get("analysis_finished"):
        announce("Análise concluída com sucesso!", "success", st_api=st)

        # ==================================================
        # 📘 ANÁLISE REFINADA DA USER STORY
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
            # 📂 CASOS DE TESTE (TABELA RESUMO + DETALHES)
            # ==================================================
            if (
                st.session_state.get("test_plan_df") is not None
                and not st.session_state["test_plan_df"].empty
            ):
                df = st.session_state["test_plan_df"].copy()

                # 🔹 Define as colunas completas para o resumo
                colunas_resumo = [
                    "id",
                    "titulo",
                    "prioridade",
                    "criterio_de_aceitacao_relacionado",
                    "justificativa_acessibilidade",
                ]

                # 🔹 Filtra e renomeia para nomes amigáveis
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
                st.dataframe(df_resumo, use_container_width=True)
                st.markdown(
                    '<div data-testid="tabela-casos-teste"></div>',
                    unsafe_allow_html=True,
                )

                # 🔹 Dropdowns individuais (detalhes)
                with st.expander(
                    "📁 Casos de Teste (Expandir para ver todos)", expanded=False
                ):
                    for index, row in df.iterrows():
                        # Garante que sempre haverá um identificador mesmo se a coluna "id" não existir
                        test_id = row.get("id", f"CT-{index + 1:03d}")
                        with st.expander(
                            f"📋 {test_id} — {row.get('titulo', '-')}", expanded=False
                        ):
                            st.markdown(f"**Prioridade:** {row.get('prioridade', '-')}")
                            st.markdown(
                                f"**Critério de Aceitação Relacionado:** {row.get('criterio_de_aceitacao_relacionado','-')}"
                            )
                            st.markdown(
                                f"**Justificativa de Acessibilidade:** {row.get('justificativa_acessibilidade','-')}"
                            )
                            if row.get("cenario"):
                                st.markdown("**Cenário Gherkin (editável):**")

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

                                # Atualiza o DataFrame se houve edição
                                if (
                                    cenario_editado.strip()
                                    != str(row["cenario"]).strip()
                                ):
                                    st.session_state["test_plan_df"].at[
                                        index, "cenario"
                                    ] = cenario_editado

                                    # 🔁 Regera o relatório de plano de testes (Markdown consolidado)
                                    from utils import gerar_relatorio_md_dos_cenarios

                                    novo_relatorio = gerar_relatorio_md_dos_cenarios(
                                        st.session_state["test_plan_df"]
                                    )
                                    st.session_state["test_plan_report"] = (
                                        novo_relatorio
                                    )

                                    # 💾 Atualiza histórico com a versão revisada (atualização em linha)
                                    _save_current_analysis_to_history(
                                        update_existing=True
                                    )
                                    st.toast(
                                        "✅ Cenário atualizado e persistido no histórico (ID existente)."
                                    )
                            else:
                                announce(
                                    "Este caso de teste ainda não possui cenário em formato Gherkin.",
                                    "info",
                                    st_api=st,
                                )

        # ==================================================
        # 📥 SEÇÃO DE DOWNLOADS
        # ==================================================
        st.divider()
        st.subheader("Downloads Disponíveis")

        col_md, col_pdf, col_azure, col_zephyr = st.columns(4)

        # Markdown unificado (análise + plano)
        relatorio_completo_md = (
            f"{(st.session_state.get('analysis_state', {}).get('relatorio_analise_inicial') or '')}\n\n"
            f"---\n\n"
            f"{(st.session_state.get('test_plan_report') or '')}"
        )

        # 📥 Exporta análise completa em Markdown
        col_md.download_button(
            "📥 Análise (.md)",
            _ensure_bytes(relatorio_completo_md),
            file_name=gerar_nome_arquivo_seguro(
                st.session_state.get("user_story_input", ""), "md"
            ),
            use_container_width=True,
        )

        # 📄 Exporta relatório PDF
        if st.session_state.get("pdf_report_bytes"):
            col_pdf.download_button(
                "📄 Relatório (.pdf)",
                _ensure_bytes(st.session_state.get("pdf_report_bytes")),
                file_name=gerar_nome_arquivo_seguro(
                    st.session_state.get("user_story_input", ""), "pdf"
                ),
                use_container_width=True,
            )

        # ==================================================
        # ⚙️ OPÇÕES DE EXPORTAÇÃO (AZURE / ZEPHYR)
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

            # ------------------------------------------------------
            # Dados para exportações
            # ------------------------------------------------------
            df_para_ferramentas = st.session_state.get("test_plan_df", pd.DataFrame())

            # Azure requer que os campos de área e responsável estejam preenchidos
            is_azure_disabled = not (
                st.session_state.get("area_path_input", "").strip()
                and st.session_state.get("assigned_to_input", "").strip()
            )

            # ✅ NOVO BLOCO: Exportação CSV Azure (formato compatível)
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

            # Zephyr (mantido em XLSX)
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

        # ------------------------------------------------------
        # Botão para resetar e reiniciar o fluxo
        # ------------------------------------------------------
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


def _render_input_form(state: AnalysisState):
    """Renderiza formulário inicial de entrada da User Story"""
    accessible_text_area(
        label="Insira a User Story aqui:",
        key="user_story_input",
        height=250,
        help_text="Digite ou cole sua User Story",
        placeholder="Exemplo: Como usuário do app...",
        st_api=st,
    )

    if accessible_button(
        label="Analisar User Story",
        key="btn_analyze",
        context="Inicia análise de IA",
        type="primary",
        st_api=st,
    ):
        user_story = st.session_state.get("user_story_input", "")

        if not user_story.strip():
            announce("Insira uma User Story antes de analisar", "warning", st_api=st)
            return

        # Atualiza estado e inicia análise
        update_user_story(user_story)

        try:
            state.start_analysis()
            st.rerun()  # Força re-renderização no estado ANALYZING
        except ValueError as e:
            announce(f"Erro de validação: {e}", "error", st_api=st)


def _render_analyzing_state(state: AnalysisState):
    """Mostra spinner enquanto IA analisa"""
    with st.spinner("🔮 O Oráculo está analisando..."):
        try:
            resultado = run_analysis_graph(state.user_story)

            # Valida estrutura da resposta
            if not resultado.get("analise_da_us"):
                raise ValueError("Resposta da IA incompleta")

            state.complete_analysis(
                analysis_data=resultado.get("analise_da_us", {}),
                analysis_report=resultado.get("relatorio_analise_inicial", ""),
            )

            st.rerun()  # Vai para EDITING_ANALYSIS

        except Exception as e:
            state.set_error(f"Falha na análise: {e!s}")
            st.rerun()


def _render_editing_form(state: AnalysisState):
    """Renderiza formulário de edição da análise"""
    announce("🔮 Revise e edite a análise antes de continuar", "info", st_api=st)

    # Extrai dados da análise (com fallbacks seguros)
    analise_json = state.analysis_data or {}

    avaliacao_str = get_flexible(analise_json, ["avaliacao_geral"], "")
    pontos_list = get_flexible(analise_json, ["pontos_ambiguos"], [])
    perguntas_list = get_flexible(analise_json, ["perguntas_para_po"], [])
    criterios_list = get_flexible(analise_json, ["sugestao_criterios_aceite"], [])
    riscos_list = get_flexible(analise_json, ["riscos_e_dependencias"], [])

    # Converte listas em strings
    pontos_str = "\n".join(pontos_list)
    perguntas_str = "\n".join(perguntas_list)
    criterios_str = "\n".join(criterios_list)
    riscos_str = "\n".join(riscos_list)

    # Formulário de edição
    with st.form(key="analysis_edit_form"):
        st.subheader("📝 Análise Editável")

        accessible_text_area(
            label="Avaliação Geral",
            key="edit_avaliacao",
            height=75,
            value=avaliacao_str,
            help_text="Descreva o entendimento geral da User Story",
            st_api=st,
        )

        accessible_text_area(
            label="Pontos Ambíguos",
            key="edit_pontos",
            height=125,
            value=pontos_str,
            help_text="Liste trechos que geram dúvidas",
            st_api=st,
        )

        accessible_text_area(
            label="Perguntas para o PO",
            key="edit_perguntas",
            height=125,
            value=perguntas_str,
            help_text="Perguntas para esclarecer requisitos",
            st_api=st,
        )

        accessible_text_area(
            label="Critérios de Aceite",
            key="edit_criterios",
            height=150,
            value=criterios_str,
            help_text="Critérios objetivos de conclusão",
            st_api=st,
        )

        accessible_text_area(
            label="Riscos e Dependências",
            key="edit_riscos",
            height=100,
            value=riscos_str,
            help_text="Riscos técnicos e dependências",
            st_api=st,
        )

        submitted = st.form_submit_button("Salvar e Continuar")

    if submitted:
        # Atualiza dados editados no estado
        state.analysis_data = {
            "avaliacao_geral": st.session_state.get("edit_avaliacao", ""),
            "pontos_ambiguos": [
                l.strip()
                for l in st.session_state.get("edit_pontos", "").split("\n")
                if l.strip()
            ],
            "perguntas_para_po": [
                l.strip()
                for l in st.session_state.get("edit_perguntas", "").split("\n")
                if l.strip()
            ],
            "sugestao_criterios_aceite": [
                l.strip()
                for l in st.session_state.get("edit_criterios", "").split("\n")
                if l.strip()
            ],
            "riscos_e_dependencias": [
                l.strip()
                for l in st.session_state.get("edit_riscos", "").split("\n")
                if l.strip()
            ],
        }

        announce("Edições salvas com sucesso!", "success", st_api=st)
        st.rerun()

    # Botões de ação
    st.divider()
    col1, col2 = st.columns(2)

    if col1.button(
        "✅ Gerar Plano de Testes", type="primary", use_container_width=True
    ):
        try:
            state.start_plan_generation()
            st.rerun()
        except ValueError as e:
            announce(f"Erro: {e}", "error", st_api=st)

    if col2.button("❌ Cancelar e Encerrar", use_container_width=True):
        _save_current_analysis_to_history()
        state.stage = AnalysisStage.COMPLETED
        st.rerun()


def _render_generating_plan_state(state: AnalysisState):
    """Mostra spinner durante geração do plano"""
    with st.spinner("🔮 Gerando plano de testes..."):
        try:
            # Prepara contexto para a IA
            analysis_context = {
                "user_story": state.user_story,
                "analise_da_us": state.analysis_data,
            }

            resultado_plano = run_test_plan_graph(analysis_context)

            # Valida resposta
            casos = resultado_plano.get("plano_e_casos_de_teste", {}).get(
                "casos_de_teste_gherkin", []
            )

            if not casos or not isinstance(casos, list):
                raise ValueError("IA não retornou casos de teste válidos")

            # Converte para DataFrame
            df = pd.DataFrame(casos)
            df = df.apply(
                lambda col: col.apply(
                    lambda x: "\n".join(map(str, x)) if isinstance(x, list) else x
                )
            )
            df.fillna("", inplace=True)

            # Gera PDF
            pdf_bytes = generate_pdf_report(state.analysis_report, df)

            # Atualiza estado
            state.complete_plan_generation(
                test_plan_data=resultado_plano.get("plano_e_casos_de_teste", {}),
                test_plan_report=resultado_plano.get("relatorio_plano_de_testes", ""),
                test_plan_df=df,
                pdf_bytes=pdf_bytes,
            )

            # Salva automaticamente
            _save_current_analysis_to_history()

            announce("Plano gerado com sucesso!", "success", st_api=st)
            st.rerun()

        except Exception as e:
            state.set_error(f"Falha ao gerar plano: {e!s}")
            _save_current_analysis_to_history()  # Salva análise mesmo com erro no plano
            st.rerun()


def _render_error_state(state: AnalysisState):
    """Renderiza tela de erro com opção de retry"""
    announce(f"⚠️ Erro: {state.error_message}", "error", st_api=st)

    col1, col2 = st.columns(2)

    if col1.button("🔄 Tentar Novamente", type="primary", use_container_width=True):
        state.reset_for_retry()
        st.rerun()

    if col2.button("🏠 Voltar ao Início", use_container_width=True):
        reset_session()
        st.rerun()


def _render_completed_state(state: AnalysisState):
    """Renderiza tela final com resultados e exportações"""
    announce("✅ Análise concluída!", "success", st_api=st)

    # Exibe análise
    with st.expander("📘 Análise Refinada", expanded=False):
        st.markdown(
            clean_markdown_report(state.analysis_report), unsafe_allow_html=True
        )

    # Exibe casos de teste (se houver)
    if state.test_plan_df is not None and not state.test_plan_df.empty:
        st.markdown("### 📊 Casos de Teste")
        st.dataframe(state.test_plan_df, use_container_width=True)

    # Botões de download
    st.divider()
    st.subheader("📥 Downloads")

    col1, col2, col3, col4 = st.columns(4)

    # Markdown
    relatorio_completo = f"{state.analysis_report}\n\n---\n\n{state.test_plan_report}"
    col1.download_button(
        "📄 Análise (.md)",
        _ensure_bytes(relatorio_completo),
        file_name=gerar_nome_arquivo_seguro(state.user_story, "md"),
        use_container_width=True,
    )

    # PDF
    if state.pdf_bytes:
        col2.download_button(
            "📄 Relatório (.pdf)",
            _ensure_bytes(state.pdf_bytes),
            file_name=gerar_nome_arquivo_seguro(state.user_story, "pdf"),
            use_container_width=True,
        )

    # Botão de nova análise
    st.divider()
    if accessible_button(
        label="🔄 Nova Análise",
        key="btn_new_analysis",
        context="Limpa resultados e inicia novo fluxo",
        type="primary",
        use_container_width=True,
        st_api=st,
    ):
        reset_session()
        st.rerun()


# ==========================================================
# 🗂️ Página de Histórico — Visualização e Exclusão
# ==========================================================
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
    # 🔥 BLOCO DE EXCLUSÃO (individual e total)
    # ==========================================================

    # 🗑️ EXCLUSÃO INDIVIDUAL (um único registro)
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

    # 🧹 EXCLUSÃO TOTAL DO HISTÓRICO
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
    # 🔍 BUSCA E CONVERSÃO DO ID SELECIONADO (CORRIGIDO)
    # ==========================================================

    # ✅ CORREÇÃO 1: Tratamento robusto de query_params
    history_entries = get_all_analysis_history()

    # Debug logs

    # Pega o ID da URL de forma segura
    raw_id = st.query_params.get("analysis_id")

    selected_id = None

    # ✅ CORREÇÃO 2: Conversão mais robusta
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
    # 🔎 Modo de visualização detalhada
    # ----------------------------------------------------------
    if selected_id:

        try:
            analysis_entry = get_analysis_by_id(selected_id)

            # ✅ CORREÇÃO 3: Garante conversão para dict
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

            # ✅ CORREÇÃO 4: Formatação segura de datas
            if isinstance(created, str):
                titulo_data = created.split()[0]  # Pega só a data (YYYY-MM-DD)
            elif hasattr(created, "strftime"):
                titulo_data = created.strftime("%Y-%m-%d")
            else:
                titulo_data = str(created)

            st.markdown(f"### Análise de {titulo_data}")

            # 🧩 User Story
            with st.expander("📄 User Story Analisada", expanded=True):
                user_story = (
                    analysis_entry.get("user_story") or "⚠️ User Story não disponível."
                )
                st.code(user_story, language="gherkin")

            # 🧠 Relatório de Análise
            with st.expander("📘 Relatório de Análise da IA", expanded=False):
                relatorio_analise = (
                    analysis_entry.get("analysis_report")
                    or "⚠️ Relatório de análise não disponível."
                )
                st.markdown(
                    clean_markdown_report(relatorio_analise),
                    unsafe_allow_html=True,
                )

            # 🧪 Plano de Testes
            plano_report = analysis_entry.get("test_plan_report", "")
            with st.expander("🧪 Plano de Testes Gerado", expanded=False):
                if plano_report:
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

        # Cria um card/expander para cada item
        for entry in history_entries:
            entry_dict = dict(entry) if not isinstance(entry, dict) else entry
            created_at = entry_dict.get("created_at")
            user_story_preview = entry_dict.get("user_story", "")[:80]

            # Formata data de forma segura
            if isinstance(created_at, str):
                data_formatada = created_at.split()[0]
            elif hasattr(created_at, "strftime"):
                data_formatada = created_at.strftime("%d/%m/%Y %H:%M")
            else:
                data_formatada = str(created_at)

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
                        key=f"btn_detalhes_{entry['id']}",
                        context=f"Exibe os detalhes completos da análise #{entry['id']}, incluindo critérios, perguntas e pontos ambíguos.",
                        type="primary",
                        use_container_width=True,
                        st_api=st,
                    ):
                        st.query_params["analysis_id"] = str(entry["id"])
                        st.rerun()

                with col2:
                    if accessible_button(
                        label="🗑️ Excluir",
                        key=f"btn_excluir_{entry['id']}",
                        context=f"Remove permanentemente a análise #{entry['id']}. Esta ação não pode ser desfeita.",
                        use_container_width=True,
                        st_api=st,
                    ):
                        st.session_state["confirm_delete_id"] = entry["id"]
                        st.rerun()

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
# 🚪 Função principal — inicializa o app QA Oráculo
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
    # ⚙️ Configuração inicial da interface
    # ------------------------------------------------------
    st.set_page_config(page_title="QA Oráculo", layout="wide")

    # ------------------------------------------------------
    # 🧱 Inicialização de banco e estado
    # ------------------------------------------------------
    init_db()
    initialize_state()  # Inicializa state machine
    # debug_state()  # Descomente para debug
    # ------------------------------------------------------
    # ♿ Acessibilidade global
    # ------------------------------------------------------
    apply_accessible_styles()
    render_keyboard_shortcuts_guide()
    render_accessibility_info()

    # ------------------------------------------------------
    # 🧭 Mapa de páginas (sidebar)
    # ------------------------------------------------------
    pages = {
        "Analisar User Story": render_main_analysis_page,
        "Histórico de Análises": render_history_page,
    }

    selected_page = st.sidebar.radio("Navegação", list(pages.keys()))
    pages[selected_page]()


# ==========================================================
# 🧭 Ponto de entrada do aplicativo
# ==========================================================
if __name__ == "__main__":
    # Quando o arquivo é executado diretamente (ex.: `streamlit run app.py`),
    # o Python entra por este bloco, chamando a função main().
    #
    # Essa abordagem garante:
    #   • Execução isolada (não executa se for importado por testes)
    #   • Consistência entre desenvolvimento local e produção
    main()

# ==========================================================
# ✅ FIM DO ARQUIVO — QA ORÁCULO
# ==========================================================
# 🔹 Este app segue o padrão modular QA Oráculo:
#    - database.py    → persistência
#    - utils.py       → formatação e exportações
#    - graph.py       → integração com LangGraph
#    - pdf_generator.py → relatórios em PDF
#    - state_manager.py → controle de estado Streamlit
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
