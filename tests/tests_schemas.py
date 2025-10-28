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
    us = schemas.AnaliseUS(avaliacao_geral="Teste")
    assert us.avaliacao_geral == "Teste"
    assert isinstance(us.pontos_ambiguos, list)


def test_analiseus_invalid_type():
    with pytest.raises(TypeError):
        schemas.AnaliseUS(avaliacao_geral="Teste", pontos_ambiguos="não é lista")
