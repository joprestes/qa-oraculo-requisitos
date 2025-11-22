from qa_core.utils.diff import generate_html_diff


def test_generate_html_diff_basic():
    text1 = "Line 1\nLine 2"
    text2 = "Line 1\nLine 2 modified"

    diff_html = generate_html_diff(text1, text2)

    assert "<table" in diff_html
    # O diff pode estar em modo contexto, então verificamos a estrutura HTML
    assert "diff" in diff_html.lower()


def test_generate_html_diff_empty():
    text1 = ""
    text2 = ""

    diff_html = generate_html_diff(text1, text2)

    assert "<table" in diff_html


def test_generate_html_diff_none():
    # Deve tratar None como string vazia
    diff_html = generate_html_diff(None, None)
    assert "<table" in diff_html


def test_generate_html_diff_add():
    text1 = "Line 1"
    text2 = "Line 1\nLine 2"

    diff_html = generate_html_diff(text1, text2)
    assert "diff_add" in diff_html


def test_generate_html_diff_sub():
    text1 = "Line 1\nLine 2"
    text2 = "Line 1"

    diff_html = generate_html_diff(text1, text2)
    assert "diff_sub" in diff_html
