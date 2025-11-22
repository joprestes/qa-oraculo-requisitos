# ==============================
# tests/test_schemas.py
# ==============================
import importlib

import pytest
from pydantic import ValidationError

from qa_core import schemas


def test_import_module_executes():
    # força execução do módulo sob cobertura
    importlib.reload(schemas)
    assert hasattr(schemas, "AnaliseUS")


def test_criacao_minima():
    us = schemas.AnaliseUS(avaliacao_geral="Boa análise")
    assert us.avaliacao_geral == "Boa análise"
    assert us.pontos_ambiguos == []
    assert us.perguntas_para_po == []
    assert us.sugestao_criterios_aceite == []
    assert us.riscos_e_dependencias == []


def test_criacao_completa():
    dados = {
        "avaliacao_geral": "Detalhada",
        "pontos_ambiguos": ["Ambiguidade 1"],
        "perguntas_para_po": ["Qual requisito X?"],
        "sugestao_criterios_aceite": ["Critério 1"],
        "riscos_e_dependencias": ["Dependência externa"],
    }
    us = schemas.AnaliseUS(**dados)
    for chave, valor in dados.items():
        assert getattr(us, chave) == valor


def test_validacao_tipos_invalidos():
    with pytest.raises(ValidationError):
        schemas.AnaliseUS(avaliacao_geral="Teste", pontos_ambiguos="não é lista")


def test_analiseus_minimal():
    obj = schemas.AnaliseUS(avaliacao_geral="Teste")
    assert obj.avaliacao_geral == "Teste"


def test_user_story_input_with_como_keyword():
    """Testa que UserStoryInput aceita user stories com 'como'."""
    from qa_core.schemas import UserStoryInput

    us = UserStoryInput(
        content="Como usuário, quero fazer login para acessar o sistema"
    )
    assert "Como usuário" in us.content


def test_user_story_input_without_como_keyword():
    """Testa que UserStoryInput aceita user stories sem 'como' (apenas sanitiza)."""
    from qa_core.schemas import UserStoryInput

    us = UserStoryInput(content="Eu quero fazer login no sistema")
    assert "Eu quero" in us.content


def test_user_story_input_sanitizes_control_chars():
    """Testa que UserStoryInput remove caracteres de controle."""
    from qa_core.schemas import UserStoryInput

    # Texto com caracteres de controle
    content = "Como usuário,\x00\x01quero fazer login\x02"
    us = UserStoryInput(content=content)
    assert "\x00" not in us.content
    assert "\x01" not in us.content
    assert "\x02" not in us.content
    assert "Como usuário" in us.content


def test_user_story_input_preserves_newlines():
    """Testa que UserStoryInput preserva newlines e tabs."""
    from qa_core.schemas import UserStoryInput

    content = "Como usuário,\n\tquero fazer login\r\npara testar"
    us = UserStoryInput(content=content)
    assert "\n" in us.content
    assert "\t" in us.content
    assert "\r\n" in us.content


def test_user_story_input_empty_string():
    """Testa que UserStoryInput rejeita string vazia (validação Pydantic)."""
    from qa_core.schemas import UserStoryInput
    from pydantic import ValidationError
    import pytest

    # Pydantic valida min_length antes do field_validator
    with pytest.raises(ValidationError):
        UserStoryInput(content="")


def test_user_story_input_whitespace_only():
    """Testa que UserStoryInput rejeita apenas espaços após sanitização."""
    from qa_core.schemas import UserStoryInput
    import pytest

    # String com 10+ espaços passa min_length do Pydantic,
    # mas field_validator faz .strip() e rejeita se vazio
    with pytest.raises(ValueError, match="não pode estar vazia"):
        UserStoryInput(content="          ")  # 10 espaços


def test_analysis_edit_input_sanitizes():
    """Testa que AnalysisEditInput sanitiza campos."""
    from qa_core.schemas import AnalysisEditInput

    data = AnalysisEditInput(
        avaliacao_geral="Avaliação\x00com controle",
        pontos_ambiguos=["Item\x01com controle", "Item normal"],
        perguntas_para_po=["Pergunta\x02"],
    )
    assert "\x00" not in data.avaliacao_geral
    assert "\x01" not in data.pontos_ambiguos[0]
    assert "Item normal" in data.pontos_ambiguos


def test_analysis_edit_input_filters_empty_items():
    """Testa que AnalysisEditInput remove itens vazios das listas."""
    from qa_core.schemas import AnalysisEditInput

    data = AnalysisEditInput(
        avaliacao_geral="Avaliação válida",
        pontos_ambiguos=["Item válido", "", "   ", "Outro válido"],
    )
    assert len(data.pontos_ambiguos) == 2
    assert "Item válido" in data.pontos_ambiguos
    assert "Outro válido" in data.pontos_ambiguos


def test_analysis_report_input_sanitizes():
    """Testa que AnalysisReportInput sanitiza campos de texto."""
    from qa_core.schemas import AnalysisReportInput

    data = AnalysisReportInput(
        user_story="US\x00com controle",
        analysis_report="Análise\x01com controle",
        test_plan_report="Plano\x02com controle",
    )
    assert "\x00" not in data.user_story
    assert "\x01" not in data.analysis_report
    assert "\x02" not in data.test_plan_report


def test_analysis_report_input_empty_strings():
    """Testa que AnalysisReportInput aceita strings vazias em campos opcionais."""
    from qa_core.schemas import AnalysisReportInput

    data = AnalysisReportInput(
        user_story="User story válida",
        analysis_report="Análise válida",
        test_plan_report="",
    )
    assert data.test_plan_report == ""
