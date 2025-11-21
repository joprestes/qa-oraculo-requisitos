import os
from unittest.mock import patch

import pytest

from qa_core.llm import LLMSettings, get_llm_client


from pydantic import ValidationError


@pytest.fixture(autouse=True)
def clear_env():
    with patch.dict(os.environ, {}, clear=True):
        yield


def test_settings_from_env_raises_without_key():
    """Testa se from_env lança erro quando não há chaves de API definidas."""
    with pytest.raises(ValidationError):
        LLMSettings.from_env()


def test_settings_google_uses_google_api_key():
    with patch.dict(
        os.environ, {"GOOGLE_API_KEY": "secret", "LLM_MODEL": "modelo"}, clear=True
    ):
        settings = LLMSettings.from_env()
    assert settings.api_key == "secret"
    assert settings.model == "modelo"
    assert settings.extra["google_api_key"] == "secret"


def test_factory_requires_known_provider():
    # Fornece uma chave dummy para passar na validação do Pydantic
    settings = LLMSettings(
        provider="desconhecido", model="m", api_key="dummy", extra={}
    )
    with pytest.raises(ValueError) as exc:
        get_llm_client(settings)
    assert "não suportado" in str(exc.value)


def test_google_settings_requires_api_key():
    with pytest.raises(ValidationError):
        LLMSettings(provider="google", model="m", api_key=None, extra={})


def test_openai_settings_requires_api_key():
    with pytest.raises(ValidationError):
        LLMSettings(provider="openai", model="m", api_key=None, extra={})


def test_llama_settings_requires_api_key():
    with pytest.raises(ValidationError):
        LLMSettings(provider="llama", model="m", api_key=None, extra={})
