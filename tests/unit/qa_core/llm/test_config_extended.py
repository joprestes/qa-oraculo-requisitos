import os
from unittest.mock import patch
from qa_core.llm.config import LLMSettings


def test_from_env_openai_with_base_url_and_org():
    """Testa from_env com OpenAI incluindo base_url e organization."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "openai",
        "LLM_MODEL": "gpt-4",
        "OPENAI_API_KEY": "sk-test",
        "OPENAI_BASE_URL": "https://custom.openai.com",
        "OPENAI_ORGANIZATION": "org-123"
    }, clear=True):
        settings = LLMSettings.from_env()
        assert settings.provider == "openai"
        assert settings.extra.get("base_url") == "https://custom.openai.com"
        assert settings.extra.get("organization") == "org-123"


def test_from_env_llama_with_endpoint_and_project():
    """Testa from_env com LLaMA incluindo endpoint e project_id."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "llama",
        "LLM_MODEL": "llama-2",
        "LLAMA_API_KEY": "llama-key",
        "LLAMA_ENDPOINT": "https://llama.endpoint.com",
        "LLAMA_PROJECT_ID": "proj-456"
    }, clear=True):
        settings = LLMSettings.from_env()
        assert settings.provider == "llama"
        assert settings.extra.get("endpoint") == "https://llama.endpoint.com"
        assert settings.extra.get("project_id") == "proj-456"


def test_from_env_google_with_specific_key():
    """Testa from_env com Google usando GOOGLE_API_KEY específica."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "google",
        "GOOGLE_API_KEY": "google-specific-key"
    }, clear=True):
        settings = LLMSettings.from_env()
        assert settings.api_key == "google-specific-key"
        assert settings.extra.get("google_api_key") == "google-specific-key"


def test_from_env_openai_fallback_to_specific_key():
    """Testa que OpenAI usa OPENAI_API_KEY se LLM_API_KEY não existir."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "openai-specific"
    }, clear=True):
        settings = LLMSettings.from_env()
        assert settings.api_key == "openai-specific"


def test_from_env_llama_fallback_to_specific_key():
    """Testa que LLaMA usa LLAMA_API_KEY se LLM_API_KEY não existir."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "llama",
        "LLAMA_API_KEY": "llama-specific"
    }, clear=True):
        settings = LLMSettings.from_env()
        assert settings.api_key == "llama-specific"


def test_validate_api_key_with_extra_google():
    """Testa validação usando google_api_key do extra."""
    settings = LLMSettings(
        provider="google",
        model="gemini",
        api_key=None,
        extra={"google_api_key": "key-from-extra"}
    )
    # Deve passar a validação
    assert settings.provider == "google"


def test_validate_api_key_with_extra_openai():
    """Testa validação usando openai_api_key do extra."""
    settings = LLMSettings(
        provider="openai",
        model="gpt-4",
        api_key=None,
        extra={"openai_api_key": "key-from-extra"}
    )
    assert settings.provider == "openai"


def test_validate_api_key_with_extra_llama():
    """Testa validação usando llama_api_key do extra."""
    settings = LLMSettings(
        provider="llama",
        model="llama-2",
        api_key=None,
        extra={"llama_api_key": "key-from-extra"}
    )
    assert settings.provider == "llama"


def test_from_env_gpt_provider_alias():
    """Testa que 'gpt' funciona como alias para 'openai'."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "gpt",
        "OPENAI_API_KEY": "gpt-key"
    }, clear=True):
        settings = LLMSettings.from_env()
        assert settings.provider == "gpt"
        assert settings.api_key == "gpt-key"
