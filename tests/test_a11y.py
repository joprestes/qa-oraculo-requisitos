# ==========================================================
# tests/test_a11y.py — Testes do Módulo de Acessibilidade
# ==========================================================
# Este arquivo valida que todas as funções de acessibilidade
# funcionam corretamente, inclusive com mocks do Streamlit.
# ==========================================================

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
import streamlit

import a11y

# ==========================================================
# Define Constantes para Testes
# ==========================================================
DEFAULT_TEXT_AREA_HEIGHT = 100
MIN_SIDEBAR_MARKDOWN_CALLS = 2  # Título + conteúdo


# ==========================================================
# CLASSE DE CONFIGURAÇÃO PARA TEXT AREA
# ==========================================================
@dataclass
class TextAreaConfig:
    """Configuração para text_area acessível."""

    label: str
    key: str
    height: int = 100
    help_text: str | None = None
    placeholder: str | None = None


# ==========================================================
# FUNÇÃO AUXILIAR PARA TEXT AREA
# ==========================================================
def accessible_text_area(config: TextAreaConfig, st_api=None) -> str:
    """
    Cria um text_area acessível com labels e instruções de navegação.

    Args:
        config: TextAreaConfig com as configurações do campo
        st_api: API do Streamlit (para testes)
    """
    st = st_api or streamlit

    help_text = config.help_text or f"Campo de entrada de texto: {config.label}"
    help_text = f"{help_text}. Use Tab para navegar entre campos."

    return st.text_area(
        label=config.label,
        key=config.key,
        height=config.height,
        help=help_text,
        placeholder=config.placeholder,
    )


# ==========================================================
# TESTES DE FUNÇÕES HELPER
# ==========================================================
def test_accessible_text_area_com_st_mockado():
    """Valida que accessible_text_area funciona com mock do Streamlit."""
    mock_st = MagicMock()
    mock_st.text_area.return_value = "texto de teste"

    result = a11y.accessible_text_area(
        label="Campo Teste",
        key="test_key",
        height=DEFAULT_TEXT_AREA_HEIGHT,
        help_text="Texto de ajuda",
        placeholder="Digite aqui",
        st_api=mock_st,
    )

    assert result == "texto de teste"

    # Valida que text_area foi chamado com parâmetros corretos
    call_args = mock_st.text_area.call_args
    assert call_args[1]["label"] == "Campo Teste"
    assert call_args[1]["key"] == "test_key"
    assert call_args[1]["height"] == DEFAULT_TEXT_AREA_HEIGHT
    assert "Use Tab para navegar" in call_args[1]["help"]


def test_accessible_text_area_sem_help_text():
    """Valida comportamento quando help_text não é fornecido."""
    mock_st = MagicMock()
    mock_st.text_area.return_value = "teste"

    config = TextAreaConfig(label="Campo", key="key1")

    a11y.accessible_text_area(config=config, st_api=mock_st)

    call_args = mock_st.text_area.call_args
    assert "Campo de entrada de texto" in call_args[1]["help"]
    assert "Use Tab" in call_args[1]["help"]


def test_accessible_text_area_exige_label_e_key():
    """label e key são obrigatórios para evitar componentes sem identificação."""

    with pytest.raises(
        TypeError,
        match=r"accessible_text_area\(\) requires 'label' and 'key' parameters.",
    ):
        a11y.accessible_text_area(label=None, key="informado", st_api=MagicMock())

    with pytest.raises(
        TypeError,
        match=r"accessible_text_area\(\) requires 'label' and 'key' parameters.",
    ):
        a11y.accessible_text_area(label="Rótulo", key=None, st_api=MagicMock())


def test_accessible_button_com_st_mockado():
    """Valida que accessible_button funciona com mock."""
    mock_st = MagicMock()
    mock_st.button.return_value = True

    result = a11y.accessible_button(
        label="Clique Aqui",
        key="btn_test",
        context="Descrição da ação",
        st_api=mock_st,
        type="primary",
    )

    assert result is True

    call_args = mock_st.button.call_args
    assert call_args[1]["label"] == "Clique Aqui"
    assert call_args[1]["key"] == "btn_test"
    assert call_args[1]["type"] == "primary"
    assert "Descrição da ação" in call_args[1]["help"]
    assert "Enter ou Espaço" in call_args[1]["help"]


def test_accessible_button_sem_context():
    """Valida comportamento padrão quando context não é fornecido."""
    mock_st = MagicMock()
    mock_st.button.return_value = False

    a11y.accessible_button(label="Botão", key="btn", st_api=mock_st)

    call_args = mock_st.button.call_args
    assert "Ação: Botão" in call_args[1]["help"]


# ==========================================================
# TESTES DE ANNOUNCE
# ==========================================================
@pytest.mark.parametrize(
    "level,method",
    [
        ("success", "success"),
        ("error", "error"),
        ("warning", "warning"),
        ("info", "info"),
    ],
)
def test_announce_todos_os_niveis(level, method):
    """Valida que announce funciona com todos os níveis de mensagem."""
    mock_st = MagicMock()

    a11y.announce(f"Mensagem de {level}", level, st_api=mock_st)

    # Valida que o método correto foi chamado
    getattr(mock_st, method).assert_called_once_with(f"Mensagem de {level}")


def test_announce_nivel_invalido_usa_info():
    """Valida fallback para 'info' quando nível é inválido."""
    mock_st = MagicMock()

    a11y.announce("Teste", "nivel_invalido", st_api=mock_st)

    # Deve usar info como fallback
    mock_st.info.assert_called_once_with("Teste")


# ==========================================================
# TESTES DO BLOCO __main__
# ==========================================================
def test_a11y_main_block_imprime_comandos(capsys):
    """Executa o módulo como script para validar mensagens educativas."""

    import runpy

    runpy.run_module("a11y", run_name="__main__")

    captured = capsys.readouterr()
    assert "Módulo de acessibilidade" in captured.out
    assert "apply_accessible_styles" in captured.out


# ==========================================================
# TESTES DE ESTILOS
# ==========================================================
def test_apply_accessible_styles_injeta_css():
    """Valida que apply_accessible_styles injeta CSS no Streamlit."""
    with patch("a11y.st") as mock_st:
        a11y.apply_accessible_styles()

        # Deve chamar st.markdown com CSS
        mock_st.markdown.assert_called_once()

        # Valida conteúdo do CSS
        css_call = mock_st.markdown.call_args[0][0]
        assert "<style>" in css_call
        assert "</style>" in css_call
        assert "background-color" in css_call
        assert "focus" in css_call.lower()
        assert "contrast" in css_call.lower()

        # Valida que unsafe_allow_html=True
        assert mock_st.markdown.call_args[1]["unsafe_allow_html"] is True


def test_apply_accessible_styles_contem_seletores_importantes():
    """Valida que o CSS contém seletores essenciais."""
    with patch("a11y.st") as mock_st:
        a11y.apply_accessible_styles()

        css = mock_st.markdown.call_args[0][0]

        # Seletores obrigatórios
        assert ".stMarkdown" in css
        assert ".stButton" in css
        assert ".stTextArea" in css
        assert "focus" in css.lower()

        # Recursos de acessibilidade
        assert "prefers-reduced-motion" in css
        assert ".sr-only" in css


# ==========================================================
# TESTES DE RENDERIZAÇÃO DO SIDEBAR
# ==========================================================
def test_render_keyboard_shortcuts_guide():
    """Valida que o guia de atalhos é renderizado no sidebar."""
    with patch("a11y.st") as mock_st:
        a11y.render_keyboard_shortcuts_guide()

        # Deve chamar sidebar.markdown pelo menos para título e conteúdo
        assert mock_st.sidebar.markdown.call_count >= MIN_SIDEBAR_MARKDOWN_CALLS

        # Valida conteúdo
        calls = [str(call) for call in mock_st.sidebar.markdown.call_args_list]
        content = " ".join(calls)
        assert "Tab" in content
        assert "Enter" in content
        assert "teclado" in content.lower()


def test_render_accessibility_info():
    """Valida que informações de acessibilidade são exibidas."""
    with patch("a11y.st") as mock_st:
        mock_expander = MagicMock()
        mock_st.sidebar.expander.return_value.__enter__.return_value = mock_expander

        a11y.render_accessibility_info()

        # Valida que o expander foi criado e usado
        mock_st.sidebar.expander.assert_called_once()
        # Valida que o contexto do expander foi acessado
        mock_st.sidebar.expander.return_value.__enter__.assert_called()


def test_check_accessibility_preferences_injeta_script_e_retorna_padrao():
    """Garante que o script de detecção é injetado e retorna valores padrão."""
    with patch("a11y.st") as mock_st:
        resultado = a11y.check_accessibility_preferences()

        # Script deve ser injetado com unsafe_allow_html=True
        mock_st.markdown.assert_called_once()
        args, kwargs = mock_st.markdown.call_args
        assert "<script>" in args[0]
        assert "prefers-reduced-motion" in args[0]
        assert kwargs["unsafe_allow_html"] is True

        # Resultado padrão documentado
        assert resultado == {
            "reduced_motion": False,
            "high_contrast": False,
            "dark_mode": True,
        }
