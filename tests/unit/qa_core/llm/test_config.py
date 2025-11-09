import os
from unittest.mock import patch

import pytest

from qa_core.llm import LLMSettings, get_llm_client
from qa_core.llm.providers.base import LLMError


@pytest.fixture(autouse=True)
def clear_env():
    with patch.dict(os.environ, {}, clear=True):
        yield


def test_settings_default_to_google():
    settings = LLMSettings.from_env()
    assert settings.provider == "google"
    assert settings.api_key is None
    assert settings.model
    assert settings.extra == {}


def test_settings_google_uses_google_api_key():
    with patch.dict(
        os.environ, {"GOOGLE_API_KEY": "secret", "LLM_MODEL": "modelo"}, clear=True
    ):
        settings = LLMSettings.from_env()
    assert settings.api_key == "secret"
    assert settings.model == "modelo"
    assert settings.extra["google_api_key"] == "secret"


def test_factory_requires_known_provider():
    settings = LLMSettings(provider="desconhecido", model="m", api_key=None, extra={})
    with pytest.raises(ValueError):
        get_llm_client(settings)


def test_google_client_requires_api_key():
    settings = LLMSettings(provider="google", model="m", api_key=None, extra={})
    with pytest.raises(LLMError):
        get_llm_client(settings)


def test_openai_client_requires_api_key():
    settings = LLMSettings(provider="openai", model="m", api_key=None, extra={})
    with pytest.raises(LLMError) as exc:
        get_llm_client(settings)
    assert "OpenAI" in str(exc.value)


def test_llama_client_requires_api_key():
    settings = LLMSettings(provider="llama", model="m", api_key=None, extra={})
    with pytest.raises(LLMError) as exc:
        get_llm_client(settings)
    assert "LLaMA" in str(exc.value)
