# ==========================================================
# diff.py — Utilitário de Comparação de Texto
# ==========================================================
import difflib


def generate_html_diff(text1: str, text2: str) -> str:
    """
    Gera uma representação HTML das diferenças entre dois textos.

    Args:
        text1: Texto original (lado esquerdo/antigo).
        text2: Texto novo (lado direito/novo).

    Returns:
        String contendo HTML com as diferenças destacadas.
    """
    if text1 is None:
        text1 = ""
    if text2 is None:
        text2 = ""

    # Garante que são strings
    text1 = str(text1)
    text2 = str(text2)

    # Divide em linhas para comparação
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()

    diff = difflib.HtmlDiff(wrapcolumn=80)

    # Gera a tabela HTML de diff
    # context=True mostra apenas as linhas com mudanças e contexto próximo
    # numlines=2 define quantas linhas de contexto mostrar
    html_diff = diff.make_table(
        lines1, lines2, context=True, numlines=2, fromdesc="Original", todesc="Novo"
    )

    # Customização básica de CSS para o Streamlit
    style = """
    <style>
        table.diff {font-family:Courier; border:medium;}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#aaffaa}
        .diff_chg {background-color:#ffff77}
        .diff_sub {background-color:#ffaaaa}
    </style>
    """

    return style + html_diff
