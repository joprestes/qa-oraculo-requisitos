"""
Testes unitários para cache do CachedLLMClient em qa_core.llm.factory
"""

from unittest.mock import Mock

from qa_core.llm.factory import CachedLLMClient
from qa_core.llm.providers.base import LLMClient


class TestCachedLLMClient:
    """Testes para CachedLLMClient."""

    def test_provider_name_property(self):
        """Testa que provider_name retorna o nome do cliente interno."""
        mock_client = Mock(spec=LLMClient)
        mock_client.provider_name = "google"

        cached = CachedLLMClient(mock_client)
        assert cached.provider_name == "google"

    def test_cache_hit_returns_cached_result(self):
        """Testa que cache hit retorna resultado do cache sem chamar o cliente."""
        mock_client = Mock(spec=LLMClient)
        mock_client.generate_content = Mock(return_value=Mock(text="cached"))

        cached = CachedLLMClient(mock_client, max_size=10)

        # Primeira chamada - não está no cache
        result1 = cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1

        # Segunda chamada - deve usar cache
        result2 = cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1  # Não chamou novamente
        assert result1 == result2

    def test_cache_clear_when_full(self):
        """Testa que cache é limpo quando atinge max_size."""
        mock_client = Mock(spec=LLMClient)
        mock_client.generate_content = Mock(return_value=Mock(text="result"))

        cached = CachedLLMClient(mock_client, max_size=3)

        # Preenche o cache até o limite
        for i in range(3):
            cached.generate_content(f"prompt {i}")
            assert mock_client.generate_content.call_count == i + 1

        # Próxima chamada deve limpar o cache
        cached.generate_content("prompt 3")
        assert mock_client.generate_content.call_count == 4
        assert len(cached._cache) == 1  # Cache foi limpo e agora tem apenas 1 item

    def test_cache_with_config(self):
        """Testa que cache funciona com diferentes configurações."""
        mock_client = Mock(spec=LLMClient)
        mock_client.generate_content = Mock(return_value=Mock(text="result"))

        cached = CachedLLMClient(mock_client)

        # Chamada com config
        config1 = {"temperature": 0.5}
        cached.generate_content("prompt", config=config1)
        assert mock_client.generate_content.call_count == 1

        # Chamada com mesmo config - deve usar cache
        cached.generate_content("prompt", config=config1)
        assert mock_client.generate_content.call_count == 1

        # Chamada com config diferente - não deve usar cache
        config2 = {"temperature": 0.7}
        cached.generate_content("prompt", config=config2)
        assert mock_client.generate_content.call_count == 2

    def test_cache_without_config(self):
        """Testa que cache funciona sem configuração."""
        mock_client = Mock(spec=LLMClient)
        mock_client.generate_content = Mock(return_value=Mock(text="result"))

        cached = CachedLLMClient(mock_client)

        # Chamada sem config
        cached.generate_content("prompt")
        assert mock_client.generate_content.call_count == 1

        # Chamada novamente sem config - deve usar cache
        cached.generate_content("prompt")
        assert mock_client.generate_content.call_count == 1

    def test_ttl_expires_entries(self):
        """Testa que entradas expiram após TTL configurado."""
        import time

        mock_client = Mock(spec=LLMClient)
        mock_response = Mock(text="result")
        mock_client.generate_content = Mock(return_value=mock_response)

        # Cache com TTL de 1 segundo
        cached = CachedLLMClient(mock_client, max_size=100, ttl_seconds=1)

        # Primeira chamada - adiciona ao cache
        result1 = cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1

        # Segunda chamada antes de expirar - deve usar cache
        result2 = cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1
        assert result1 == result2

        # Aguarda expiração (1.1 segundos para garantir)
        time.sleep(1.1)

        # Terceira chamada após expirar - deve fazer nova chamada
        cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 2

    def test_ttl_none_does_not_expire(self):
        """Testa que entradas não expiram quando TTL é None."""
        import time

        mock_client = Mock(spec=LLMClient)
        mock_response = Mock(text="result")
        mock_client.generate_content = Mock(return_value=mock_response)

        # Cache sem TTL (None)
        cached = CachedLLMClient(mock_client, max_size=100, ttl_seconds=None)

        # Primeira chamada
        result1 = cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1

        # Aguarda tempo (simula passagem de tempo)
        time.sleep(0.1)

        # Segunda chamada - ainda deve usar cache mesmo após tempo
        result2 = cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1
        assert result1 == result2

    def test_ttl_cleanup_expired_entries(self):
        """Testa que entradas expiradas são removidas automaticamente."""
        import time

        mock_client = Mock(spec=LLMClient)
        mock_response = Mock(text="result")
        mock_client.generate_content = Mock(return_value=mock_response)

        # Cache com TTL curto
        cached = CachedLLMClient(mock_client, max_size=100, ttl_seconds=0.5)

        # Adiciona múltiplas entradas
        cached.generate_content("prompt 1")
        cached.generate_content("prompt 2")
        cached.generate_content("prompt 3")

        assert len(cached._cache) == 3
        assert mock_client.generate_content.call_count == 3

        # Aguarda expiração
        time.sleep(0.6)

        # Limpa entradas expiradas (chamando generate_content novamente)
        cached.generate_content("prompt 4")

        # Cache deve ter apenas 1 entrada (a nova)
        assert len(cached._cache) == 1
        assert mock_client.generate_content.call_count == 4

    def test_ttl_returns_non_expired_entries(self):
        """Testa que entradas não expiradas ainda são retornadas do cache."""
        import time

        mock_client = Mock(spec=LLMClient)
        mock_response = Mock(text="result")
        mock_client.generate_content = Mock(return_value=mock_response)

        # Cache com TTL de 2 segundos
        cached = CachedLLMClient(mock_client, max_size=100, ttl_seconds=2)

        # Primeira chamada
        cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1

        # Aguarda menos que TTL (1 segundo)
        time.sleep(1)

        # Segunda chamada - ainda deve usar cache (não expirou)
        result = cached.generate_content("test prompt")
        assert mock_client.generate_content.call_count == 1
        assert result.text == "result"

    def test_ttl_removes_expired_entry_before_return(self):
        """Testa que entrada expirada é removida antes de fazer nova chamada."""
        import time

        mock_client = Mock(spec=LLMClient)
        mock_response = Mock(text="new result")
        mock_client.generate_content = Mock(return_value=mock_response)

        # Cache com TTL curto
        cached = CachedLLMClient(mock_client, max_size=100, ttl_seconds=0.3)

        # Primeira chamada
        cached.generate_content("test prompt")
        assert len(cached._cache) == 1
        assert mock_client.generate_content.call_count == 1

        # Aguarda expiração
        time.sleep(0.4)

        # Segunda chamada - entrada expirada deve ser removida
        # e nova chamada deve ser feita
        cached.generate_content("test prompt")
        assert (
            len(cached._cache) == 1
        )  # Ainda 1 porque removeu a expirada e adicionou nova
        assert mock_client.generate_content.call_count == 2

    def test_ttl_with_different_prompts(self):
        """Testa que TTL funciona independentemente para diferentes prompts."""
        import time

        mock_client = Mock(spec=LLMClient)
        mock_client.generate_content = Mock(
            side_effect=lambda p, **kwargs: Mock(text=f"result_{p}")
        )

        # Cache com TTL
        cached = CachedLLMClient(mock_client, max_size=100, ttl_seconds=1)

        # Adiciona dois prompts diferentes
        cached.generate_content("prompt 1")
        cached.generate_content("prompt 2")

        assert mock_client.generate_content.call_count == 2

        # Ambos devem estar no cache
        assert len(cached._cache) == 2

        # Aguarda expiração
        time.sleep(1.1)

        # Uma chamada nova deve limpar ambas as entradas expiradas
        cached.generate_content("prompt 3")
        assert len(cached._cache) == 1  # Apenas a nova entrada

    def test_ttl_default_is_none(self):
        """Testa que TTL padrão é None (sem expiração)."""
        mock_client = Mock(spec=LLMClient)
        cached = CachedLLMClient(mock_client)

        # Verifica que TTL padrão é None
        assert cached._ttl_seconds is None

    def test_ttl_cleanup_before_full_cache_clear(self):
        """Testa que limpeza de expirados ocorre antes de limpar cache cheio."""
        import time

        mock_client = Mock(spec=LLMClient)
        mock_client.generate_content = Mock(
            side_effect=lambda p, **kwargs: Mock(text=f"result_{p}")
        )

        # Cache pequeno com TTL
        cached = CachedLLMClient(mock_client, max_size=3, ttl_seconds=0.5)

        # Preenche cache
        cached.generate_content("prompt 1")
        cached.generate_content("prompt 2")
        cached.generate_content("prompt 3")

        assert len(cached._cache) == 3

        # Aguarda expiração
        time.sleep(0.6)

        # Adiciona nova entrada - deve limpar expiradas primeiro, não limpar tudo
        cached.generate_content("prompt 4")

        # Deve ter apenas 1 entrada (as expiradas foram removidas)
        assert len(cached._cache) == 1
