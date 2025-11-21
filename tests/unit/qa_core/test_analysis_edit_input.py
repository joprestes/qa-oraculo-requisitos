import pytest
from pydantic import ValidationError
from qa_core.schemas import AnalysisEditInput


def test_analysis_edit_input_sanitizes_avaliacao():
    """Testa que AnalysisEditInput sanitiza avaliacao_geral."""
    data = AnalysisEditInput(
        avaliacao_geral="Avaliação\x00com\x01caracteres\x02de\x03controle",
        pontos_ambiguos=[],
        perguntas_para_po=[],
        sugestao_criterios_aceite=[],
        riscos_e_dependencias=[],
    )
    assert "\x00" not in data.avaliacao_geral
    assert "Avaliação" in data.avaliacao_geral


def test_analysis_edit_input_sanitizes_lists():
    """Testa que AnalysisEditInput sanitiza listas."""
    data = AnalysisEditInput(
        avaliacao_geral="Teste",
        pontos_ambiguos=["Ponto\x001", "Ponto 2"],
        perguntas_para_po=["Pergunta\x011"],
        sugestao_criterios_aceite=["Critério\x021"],
        riscos_e_dependencias=["Risco\x031"],
    )
    assert all("\x00" not in item for item in data.pontos_ambiguos)
    assert all("\x01" not in item for item in data.perguntas_para_po)


def test_analysis_edit_input_filters_empty_strings():
    """Testa que AnalysisEditInput filtra strings vazias das listas."""
    data = AnalysisEditInput(
        avaliacao_geral="Teste",
        pontos_ambiguos=["Ponto 1", "", "  ", "Ponto 2"],
        perguntas_para_po=[],
        sugestao_criterios_aceite=[],
        riscos_e_dependencias=[],
    )
    assert len(data.pontos_ambiguos) == 2
    assert "Ponto 1" in data.pontos_ambiguos
    assert "Ponto 2" in data.pontos_ambiguos
