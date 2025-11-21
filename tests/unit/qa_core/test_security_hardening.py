import pytest
from pydantic import ValidationError
from qa_core.schemas import AnalysisEditInput, UserStoryInput
from qa_core.security import RateLimiter, sanitize_for_logging


def test_analysis_edit_input_validation():
    """Testa validação do schema AnalysisEditInput."""
    # Caso válido
    valid_data = {
        "avaliacao_geral": "Avaliação válida e completa.",
        "pontos_ambiguos": ["Ponto 1"],
        "perguntas_para_po": ["Pergunta 1"],
        "sugestao_criterios_aceite": ["Critério 1"],
        "riscos_e_dependencias": ["Risco 1"],
    }
    model = AnalysisEditInput(**valid_data)
    assert model.avaliacao_geral == "Avaliação válida e completa."

    # Caso inválido (avaliação muito curta)
    invalid_data = valid_data.copy()
    invalid_data["avaliacao_geral"] = "Cur"  # 3 chars < 5
    with pytest.raises(ValidationError):
        AnalysisEditInput(**invalid_data)


def test_user_story_input_sanitization():
    """Testa sanitização da User Story."""
    dirty_input = "Como usuário \x00 quero logar"
    model = UserStoryInput(content=dirty_input)
    assert "\x00" not in model.content
    assert "Como usuário  quero logar" in model.content


def test_rate_limiter():
    """Testa o limitador de taxa."""
    limiter = RateLimiter(max_calls=2, period_seconds=1)

    assert limiter.is_allowed() is True
    assert limiter.is_allowed() is True
    assert limiter.is_allowed() is False  # 3ª chamada bloqueada


def test_log_sanitization():
    """Testa sanitização de logs."""
    msg = "Erro na api_key=sk-1234567890abcdef1234567890"
    sanitized = sanitize_for_logging(msg)
    assert "sk-1234567890" not in sanitized
    assert "<REDACTED>" in sanitized
