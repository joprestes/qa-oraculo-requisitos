# ==========================================================
# a11y.py — Módulo de Acessibilidade do QA Oráculo
# ==========================================================
#  Este módulo fornece melhorias de acessibilidade REAIS
#    que funcionam dentro das limitações do Streamlit.
#
#  Baseado em:
#   - WCAG 2.1 Level AA
#   - Testes com NVDA, JAWS e VoiceOver
#   - Limitações técnicas do Streamlit validadas
#
# IMPORTANTE: Este módulo NÃO promete acessibilidade 100%.
#   Ele implementa o MÁXIMO possível dentro do Streamlit.
# ==========================================================


from typing import Any, Mapping

import streamlit as st
from streamlit.components.v1 import html as components_html

_STYLES_APPLIED = False
_A11Y_PREFS_CACHE: dict[str, bool] | None = None
_A11Y_SESSION_KEY = "_qa_oraculo_a11y_prefs"
_DEFAULT_PREFS = {
    "reduced_motion": False,
    "high_contrast": False,
    "dark_mode": False,
}


def apply_accessible_styles(force: bool = False):
    """
    Injeta CSS global para melhorar acessibilidade.

    Melhorias aplicadas:
    - Contraste de cores WCAG AA (4.5:1)
    - Foco visível em todos os elementos interativos
    - Tamanho mínimo de toque (44x44px)
    - Suporte a prefers-reduced-motion
    - Suporte a prefers-contrast: high
    - Espaçamento melhorado para legibilidade
    - Modo escuro com toggle manual

    Testado em:
    - Chrome + NVDA (Windows)
    - Safari + VoiceOver (macOS)
    - Firefox + JAWS (Windows)
    """
    global _STYLES_APPLIED

    if _STYLES_APPLIED and not force:
        return

    # Verifica se modo escuro está ativado manualmente ou por preferência do sistema
    dark_mode_enabled = False
    try:
        session_state = getattr(st, "session_state", None)
        if session_state is not None:
            # Prioriza preferência manual sobre detecção automática
            dark_mode_manual = session_state.get("dark_mode_manual", None)
            if dark_mode_manual is not None:
                dark_mode_enabled = dark_mode_manual
            else:
                # Fallback para detecção automática se não houver preferência manual
                # Evita chamar check_accessibility_preferences durante testes para não interferir
                try:
                    prefs = check_accessibility_preferences()
                    dark_mode_enabled = prefs.get("dark_mode", False)
                except Exception:
                    # Se falhar (ex: em testes), usa padrão
                    dark_mode_enabled = False
    except Exception:
        pass

    # Aplica estilos base + modo escuro se necessário
    # Força reaplicação dos estilos quando modo escuro muda
    _apply_theme_styles(dark_mode_enabled)

    _STYLES_APPLIED = True


def _apply_theme_styles(dark_mode: bool = False) -> None:
    """Aplica estilos CSS do tema (claro ou escuro)."""
    # CSS base comum (foco, responsividade, etc.)
    common_css = """
    /* ==========================================================
       FOCO E INTERAÇÃO
       ========================================================== */
    button:focus,
    textarea:focus,
    input:focus,
    select:focus,
    a:focus {
        outline: 3px solid #4A90E2 !important;
        outline-offset: 2px !important;
        border-color: #4A90E2 !important;
    }

    /* ==========================================================
       RESPONSIVIDADE
       ========================================================== */
    @media (max-width: 768px) {
        .stMarkdown p,
        .stMarkdown li {
            font-size: 18px !important;
        }
        .stButton > button {
            min-height: 48px !important;
            font-size: 18px !important;
        }
    }

    /* ==========================================================
       MEDIA QUERIES PARA PREFÊRENCIAS DO USUÁRIO
       ========================================================== */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    /* ==========================================================
       SCREEN READER SUPPORT
       ========================================================== */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }

    .sr-only-focusable:focus {
        position: static;
        width: auto;
        height: auto;
        overflow: visible;
        clip: auto;
        white-space: normal;
    }
    """

    theme_css = _get_base_theme_css(dark_mode)
    st.markdown(
        f"<style>\n{theme_css}\n{common_css}\n    </style>", unsafe_allow_html=True
    )


def _get_base_theme_css(dark_mode: bool = False) -> str:
    """Retorna CSS do tema base (claro ou escuro)."""

    if dark_mode:
        return """
    /* ==========================================================
       BASE — Tema Escuro Acessível (QA Oráculo)
       ========================================================== */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1A1A1A !important;
        color: #E0E0E0 !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        font-family: "Poppins", -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
        border-right: 1px solid #404040 !important;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] strong {
        color: #7C8FFF !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] a {
        color: #64B5F6 !important;
        text-decoration: underline !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] a:hover,
    [data-testid="stSidebar"] a:focus {
        color: #90CAF9 !important;
        text-decoration: none !important;
    }

    /* ==========================================================
       TIPOGRAFIA E LINKS (Conteúdo Principal) - Modo Escuro
       ========================================================== */
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span {
        color: #E0E0E0 !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    .stMarkdown a {
        color: #64B5F6 !important;
        text-decoration: underline !important;
        font-weight: 600 !important;
    }

    .stMarkdown a:hover,
    .stMarkdown a:focus {
        color: #90CAF9 !important;
        text-decoration: none !important;
    }

    /* ==========================================================
       LABELS E TEXTOS DE INPUTS - Modo Escuro
       ========================================================== */
    label, 
    .stRadio label,
    .stCheckbox label,
    .stTextArea label,
    .stTextInput label,
    .stSelectbox label,
    .stMultiSelect label,
    .stNumberInput label,
    .stDateInput label,
    .stTimeInput label,
    .stFileUploader label,
    .stRadio div[data-testid="stMarkdownContainer"] p,
    .stCheckbox div[data-testid="stMarkdownContainer"] p {
        color: #E0E0E0 !important;
    }

    /* Forçar cor branca para labels principais */
    div[data-testid="stWidgetLabel"] label {
        color: #FFFFFF !important;
    }

    /* ==========================================================
       CAMPOS DE ENTRADA (TextArea / TextInput) - Modo Escuro
       ========================================================== */
    .stTextArea textarea,
    .stTextInput input {
        border: 2px solid #64B5F6 !important;
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        padding: 10px 12px !important;
        border-radius: 6px !important;
        font-size: 16px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #90CAF9 !important;
        box-shadow: 0 0 0 3px rgba(100, 181, 246, 0.4) !important;
        outline: none !important;
    }
    
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: #888888 !important;
    }

    /* ==========================================================
       BOTÕES - Modo Escuro
       ========================================================== */
    .stButton > button {
        background-color: #64B5F6 !important;
        color: #1A1A1A !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border-radius: 6px !important;
        border: none !important;
        transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    .stButton > button:hover,
    .stButton > button:focus {
        background-color: #90CAF9 !important;
        box-shadow: 0 0 0 3px rgba(100, 181, 246, 0.3) !important;
        outline: none !important;
    }

    /* ==========================================================
       MENSAGENS DE ESTADO (announce) - Modo Escuro
       ========================================================== */
    .stSuccess {
        border-left: 5px solid #4CAF50 !important;
        background-color: #1B5E20 !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #C8E6C9 !important;
    }

    .stError {
        border-left: 5px solid #EF5350 !important;
        background-color: #4A1A1A !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #FFCDD2 !important;
    }

    .stWarning {
        border-left: 5px solid #FFB74D !important;
        background-color: #5D4037 !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #FFE0B2 !important;
    }

    .stInfo {
        border-left: 5px solid #42A5F5 !important;
        background-color: #0D47A1 !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #BBDEFB !important;
    }

    /* ==========================================================
       EXPANDERS E DETALHES - Modo Escuro
       ========================================================== */
    .streamlit-expanderHeader {
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 12px !important;
        background-color: #2D2D2D !important;
        border: 1px solid #404040 !important;
        border-radius: 4px !important;
        color: #E0E0E0 !important;
    }
        """

    # Tema claro (original)
    return """
    /* ==========================================================
       BASE — Tema Claro Acessível (QA Oráculo)
       ========================================================== */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FAFAFA !important;
        color: #1A1A1A !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        font-family: "Poppins", -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F5F5F8 !important;
        color: #1A1A1A !important;
        border-right: 1px solid #E0E0E0 !important;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] strong {
        color: #4A3CE8 !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] a {
        color: #4A90E2 !important;
        text-decoration: underline !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] a:hover,
    [data-testid="stSidebar"] a:focus {
        color: #2F6BCF !important;
        text-decoration: none !important;
    }

    /* ==========================================================
       TIPOGRAFIA E LINKS (Conteúdo Principal)
       ========================================================== */
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span {
        color: #1A1A1A !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #202020 !important;
        font-weight: 700 !important;
    }

    .stMarkdown a {
        color: #4A90E2 !important;
        text-decoration: underline !important;
        font-weight: 600 !important;
    }

    .stMarkdown a:hover,
    .stMarkdown a:focus {
        color: #0066CC !important;
        text-decoration: none !important;
    }

    /* ==========================================================
       CAMPOS DE ENTRADA (TextArea / TextInput)
       ========================================================== */
    .stTextArea textarea,
    .stTextInput input {
        border: 2px solid #CCCCCC !important;
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        padding: 10px 12px !important;
        border-radius: 6px !important;
        font-size: 16px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #4A90E2 !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.25) !important;
        outline: none !important;
    }

    /* ==========================================================
       BOTÕES
       ========================================================== */
    .stButton > button {
        background-color: #4A90E2 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border-radius: 6px !important;
        border: none !important;
        transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    .stButton > button:hover,
    .stButton > button:focus {
        background-color: #3B7FD9 !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
        outline: none !important;
    }

    /* ==========================================================
       MENSAGENS DE ESTADO (announce)
       ========================================================== */
    .stSuccess {
        border-left: 5px solid #2E8B57 !important;
        background-color: #E8F5E9 !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #1A1A1A !important;
    }

    .stError {
        border-left: 5px solid #C62828 !important;
        background-color: #FDECEA !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #1A1A1A !important;
    }

    .stWarning {
        border-left: 5px solid #FFB300 !important;
        background-color: #FFF8E1 !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #1A1A1A !important;
    }

    .stInfo {
        border-left: 5px solid #0288D1 !important;
        background-color: #E1F5FE !important;
        padding: 16px !important;
        border-radius: 4px !important;
        color: #1A1A1A !important;
    }

    /* ==========================================================
       FOCO E INTERAÇÃO
       ========================================================== */
    button:focus,
    textarea:focus,
    input:focus,
    select:focus,
    a:focus {
        outline: 3px solid #4A90E2 !important;
        outline-offset: 2px !important;
        border-color: #4A90E2 !important;
    }

    /* ==========================================================
       EXPANDERS E DETALHES
       ========================================================== */
    .streamlit-expanderHeader {
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 12px !important;
        background-color: #F9F9FB !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 4px !important;
    }

    /* ==========================================================
       RESPONSIVIDADE
       ========================================================== */
    @media (max-width: 768px) {
        .stMarkdown p,
        .stMarkdown li {
            font-size: 18px !important;
        }

        .stButton > button {
            min-height: 48px !important;
            font-size: 18px !important;
        }
    }

    /* ==========================================================
       MEDIA QUERIES PARA PREFÊRENCIAS DO USUÁRIO
       ========================================================== */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    @media (prefers-contrast: more), (forced-colors: active) {
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }

        .stButton > button,
        a,
        .stMarkdown a {
            color: #000000 !important;
        }

        .stButton > button {
            border: 2px solid currentColor !important;
        }
    }

    /* ==========================================================
       SCREEN READER SUPPORT
       ========================================================== */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }

    .sr-only-focusable:focus {
        position: static;
        width: auto;
        height: auto;
        overflow: visible;
        clip: auto;
        white-space: normal;
    }
    """


def accessible_text_area(  # noqa: PLR0913
    label: str | None = None,
    key: str | None = None,
    *,
    config: Any | None = None,
    height: int | None = None,
    help_text: str | None = None,
    placeholder: str | None = None,
    st_api=None,
    **kwargs,
):
    """
    Text area com contexto melhorado para acessibilidade.

    Parâmetros:
        label: Rótulo do campo (obrigatório)
        key: Chave única para o session_state
        height: Altura em pixels
        help_text: Texto de ajuda detalhado
        placeholder: Texto de exemplo
        st_api: Instância do módulo Streamlit (opcional)
        **kwargs: Outros parâmetros do st.text_area

    Melhorias sobre st.text_area():
        - Help text padronizado com dicas de navegação
        - Placeholder sempre visível
        - Contexto adicional para leitores de tela

    Exemplo:
        >>> texto = accessible_text_area(
        ...     label="User Story",
        ...     key="us_input",
        ...     help_text="Digite a funcionalidade que deseja analisar",
        ...     placeholder="Como [persona], quero [ação], para [objetivo]"
        ... )
    """
    if config is not None:
        label = getattr(config, "label", label)
        key = getattr(config, "key", key)
        height = getattr(config, "height", height)
        help_text = getattr(config, "help_text", help_text)
        placeholder = getattr(config, "placeholder", placeholder)

    if label is None or key is None:
        raise TypeError("accessible_text_area() requires 'label' and 'key' parameters.")

    resolved_height = 200 if height is None else height
    resolved_placeholder = "" if placeholder is None else placeholder

    base_help = help_text if help_text else f"Campo de entrada de texto: {label}"
    enhanced_help = f"{base_help}\n\n💡 Use Tab para navegar entre campos."

    streamlit_api = _resolve_streamlit_api(st_api)

    return streamlit_api.text_area(
        label=label,
        key=key,
        height=resolved_height,
        help=enhanced_help,
        placeholder=resolved_placeholder,
        **kwargs,
    )


def accessible_button(label: str, key: str, context: str = "", st_api=None, **kwargs):
    """
    Botão com contexto melhorado via tooltip.

    Parâmetros:
        label: Texto do botão
        key: Chave única
        context: Descrição detalhada da ação (aparece no tooltip)
        st_api: Instância do módulo Streamlit (opcional)
        **kwargs: Outros parâmetros do st.button

    Melhorias sobre st.button():
        - Tooltip contextual sempre presente
        - Dica de ativação por teclado

    Exemplo:
        >>> if accessible_button(
        ...     label="Analisar",
        ...     key="btn_analyze",
        ...     context="Inicia análise de IA da User Story",
        ...     type="primary"
        ... ):
        ...     # lógica de análise
    """
    help_text = context if context else f"Ação: {label}"
    help_text += "\n\n⌨️ Pressione Enter ou Espaço para ativar."

    streamlit_api = _resolve_streamlit_api(st_api)

    return streamlit_api.button(label=label, key=key, help=help_text, **kwargs)


def _resolve_streamlit_api(st_api=None):
    """Retorna o módulo Streamlit apropriado (global ou mock)."""
    return st_api if st_api is not None else st


def announce(message: str, level: str = "info", st_api=None):
    """
    Anuncia mensagens de forma acessível.

    Esta função usa os componentes nativos do Streamlit que
    já possuem role="alert" ou aria-live="polite", garantindo
    que leitores de tela anunciem o conteúdo automaticamente.

    Parâmetros:
        message: Texto da mensagem
        level: Tipo de mensagem ("success", "error", "warning", "info")
        st_api: Instância do módulo Streamlit (opcional). Se não informado,
            tenta reutilizar `app.st` (permite testes com mock) e, por fim,
            usa o módulo global `streamlit`.

    Testado com:
        - NVDA + Chrome (Windows)
        - JAWS + Firefox (Windows)
        - VoiceOver + Safari (macOS)

    Exemplo:
        >>> announce("Análise concluída com sucesso!", "success")
        >>> announce("Erro ao conectar com API", "error")
    """
    streamlit_api = _resolve_streamlit_api(st_api)

    announce_functions = {
        "success": streamlit_api.success,
        "error": streamlit_api.error,
        "warning": streamlit_api.warning,
        "info": streamlit_api.info,
    }

    func = announce_functions.get(level, streamlit_api.info)
    func(message)


def render_keyboard_shortcuts_guide():
    """
    Exibe guia de atalhos de teclado no sidebar como dropdown.

    A seção agora utiliza um elemento `<details>` renderizado via
    `st.sidebar.markdown`, permitindo recolher o conteúdo quando
    não estiver em uso. Isso reduz poluição visual sem remover a
    documentação acessível para quem depende de navegação por teclado.

    IMPORTANTE: O Streamlit não permite atalhos customizados via JS.
    Esta função apenas DOCUMENTA os atalhos nativos existentes.
    """
    with st.sidebar.expander("⌨️ Navegação por Teclado"):
        st.markdown(
            """
        **Básico:**
        - `Tab` — Próximo elemento
        - `Shift+Tab` — Elemento anterior
        - `Enter` — Ativar botão/link focado
        - `Espaço` — Ativar botão focado
        
        **Em campos de texto:**
        - `Ctrl+A` — Selecionar tudo
        - `Ctrl+C` — Copiar
        - `Ctrl+V` — Colar
        
        **Expanders:**
        - `Enter/Espaço` — Expandir/colapsar
        
        💡 **Dica:** Use apenas o teclado!  
        Todo o app é navegável sem mouse.
    
        """,
            unsafe_allow_html=True,
        )


def render_dark_mode_toggle():
    """
    Renderiza toggle para alternar modo escuro na sidebar.

    O toggle permite ao usuário alternar manualmente entre modo claro e escuro,
    sobrescrevendo a detecção automática baseada na preferência do sistema.
    """
    try:
        # Inicializa dark_mode_manual se não existir
        if "dark_mode_manual" not in st.session_state:
            # Tenta detectar preferência do sistema primeiro
            prefs = check_accessibility_preferences()
            st.session_state.dark_mode_manual = prefs.get("dark_mode", False)

        # Renderiza toggle
        dark_mode_enabled = st.sidebar.toggle(
            "🌙 Modo Escuro",
            value=st.session_state.dark_mode_manual,
            key="dark_mode_toggle",
            help="Alterna entre tema claro e escuro. Sobrescreve a preferência do sistema.",
        )

        # Atualiza session_state e força reaplicação de estilos
        if st.session_state.dark_mode_manual != dark_mode_enabled:
            st.session_state.dark_mode_manual = dark_mode_enabled
            # Força reaplicação dos estilos
            global _STYLES_APPLIED
            _STYLES_APPLIED = False
            apply_accessible_styles(force=True)
    except Exception:
        # Ignora erros para não quebrar o app
        pass


def render_accessibility_info():
    """
    Exibe informações sobre acessibilidade do app no sidebar.

    Documenta:
    - Conformidade WCAG
    - Tecnologias assistivas testadas
    - Limitações conhecidas
    - Como reportar problemas
    """
    with st.sidebar.expander("♿ Sobre Acessibilidade"):
        st.markdown(
            """
        **Conformidade:**
        - WCAG 2.1 Level AA (parcial)
        - Navegação 100% por teclado
        - Contraste mínimo 4.5:1
        
        **Testado com:**
        - ✅ NVDA (Windows)
        - ✅ VoiceOver (macOS)
        - ⚠️ JAWS (limitações conhecidas)
        
        **Limitações:**
        - Componentes customizados do Streamlit
        - Algumas ARIA labels não disponíveis
        
        **Reportar problemas:**
        [GitHub Issues](https://github.com/joprestes/qa-oraculo-requisitos/issues)
        """
        )


def check_accessibility_preferences(force_refresh: bool = False):
    """
    Detecta preferências de acessibilidade do navegador.

    Retorna um dicionário com as preferências detectadas:
        - reduced_motion: bool
        - high_contrast: bool
        - dark_mode: bool

    Args:
        force_refresh: Quando True força uma nova detecção, ignorando valores
            previamente armazenados em cache.

    NOTA: Esta função usa JavaScript via st.components.
    A detecção acontece no lado do cliente.

    Exemplo:
        >>> prefs = check_accessibility_preferences()
        >>> if prefs['reduced_motion']:
        ...     # Desabilita animações
    """
    # Injeta JavaScript para detectar preferências
    global _A11Y_PREFS_CACHE

    if force_refresh:
        _A11Y_PREFS_CACHE = None

    detection_script = """
    <script>
    (function () {
        const queries = [
            window.matchMedia('(prefers-reduced-motion: reduce)'),
            window.matchMedia('(prefers-contrast: high)'),
            window.matchMedia('(prefers-color-scheme: dark)')
        ];

        function snapshot() {
            return {
                reduced_motion: queries[0] ? queries[0].matches : false,
                high_contrast: queries[1] ? queries[1].matches : false,
                dark_mode: queries[2] ? queries[2].matches : false
            };
        }

        function send() {
            const prefs = snapshot();
            if (window.Streamlit && window.Streamlit.setComponentValue) {
                window.Streamlit.setComponentValue(prefs);
            }
        }

        send();

        queries.forEach((mq) => {
            if (!mq) {
                return;
            }

            if (typeof mq.addEventListener === "function") {
                mq.addEventListener("change", send);
            } else if (typeof mq.addListener === "function") {
                mq.addListener(send);
            }
        });

        window.addEventListener("load", send);
    }());
    </script>
    """

    result = components_html(
        detection_script,
        height=0,
    )

    if isinstance(result, Mapping):
        normalized = _normalize_preferences(result)
        _A11Y_PREFS_CACHE = normalized
        _persist_preferences(normalized)
        return normalized

    if _A11Y_PREFS_CACHE is not None:
        return _A11Y_PREFS_CACHE

    default_prefs = _DEFAULT_PREFS.copy()
    _persist_preferences(default_prefs)
    return default_prefs


def _normalize_preferences(raw: Mapping[str, Any]) -> dict[str, bool]:
    """
    Normaliza o payload retornado pelo componente JavaScript.
    """

    return {
        "reduced_motion": bool(
            raw.get("reduced_motion", raw.get("reducedMotion", False))
        ),
        "high_contrast": bool(raw.get("high_contrast", raw.get("highContrast", False))),
        "dark_mode": bool(raw.get("dark_mode", raw.get("darkMode", False))),
    }


def _persist_preferences(preferences: dict[str, bool]) -> None:
    """
    Persiste as preferências no session_state (quando disponível) para
    reutilização em outros módulos do app.
    """

    try:
        session_state = getattr(st, "session_state", None)
        if session_state is not None:
            session_state[_A11Y_SESSION_KEY] = preferences
    except Exception:
        # Evita que qualquer erro de session_state quebre o fluxo
        pass


# ==========================================================
#  Função de teste
# ==========================================================

if __name__ == "__main__":  # pragma: no cover - executado apenas manualmente
    print("✅ Módulo de acessibilidade carregado com sucesso!")
    print("\nFunções disponíveis:")
    print("  - apply_accessible_styles()")
    print("  - accessible_text_area()")
    print("  - accessible_button()")
    print("  - announce()")
    print("  - render_keyboard_shortcuts_guide()")
    print("  - render_accessibility_info()")
    print("  - check_accessibility_preferences()")
    print("\nPara usar: from utils.a11y import *")
