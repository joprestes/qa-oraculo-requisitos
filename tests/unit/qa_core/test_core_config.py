"""
Testes unitários para qa_core.config
"""

from qa_core import config


class TestConfig:
    """Testes para as configurações centrais do projeto."""

    def test_nome_modelo_exists(self):
        """Testa que NOME_MODELO está definido."""
        assert hasattr(config, "NOME_MODELO")
        assert config.NOME_MODELO
        assert isinstance(config.NOME_MODELO, str)
        assert len(config.NOME_MODELO) > 0

    def test_nome_modelo_has_valid_value(self):
        """Testa que NOME_MODELO tem um valor válido."""
        assert "gemini" in config.NOME_MODELO.lower()

    def test_config_geracao_analise_exists(self):
        """Testa que CONFIG_GERACAO_ANALISE está definido."""
        assert hasattr(config, "CONFIG_GERACAO_ANALISE")
        assert config.CONFIG_GERACAO_ANALISE
        assert isinstance(config.CONFIG_GERACAO_ANALISE, dict)

    def test_config_geracao_analise_has_required_keys(self):
        """Testa que CONFIG_GERACAO_ANALISE tem as chaves necessárias."""
        required_keys = [
            "temperature",
            "top_p",
            "top_k",
            "max_output_tokens",
            "response_mime_type",
        ]
        for key in required_keys:
            assert key in config.CONFIG_GERACAO_ANALISE, f"Chave '{key}' não encontrada"

    def test_config_geracao_analise_has_json_mime_type(self):
        """Testa que CONFIG_GERACAO_ANALISE força saída em JSON."""
        assert config.CONFIG_GERACAO_ANALISE["response_mime_type"] == "application/json"

    def test_config_geracao_analise_temperature(self):
        """Testa que temperatura está configurada corretamente."""
        assert isinstance(config.CONFIG_GERACAO_ANALISE["temperature"], (int, float))
        assert 0 <= config.CONFIG_GERACAO_ANALISE["temperature"] <= 2

    def test_config_geracao_relatorio_exists(self):
        """Testa que CONFIG_GERACAO_RELATORIO está definido."""
        assert hasattr(config, "CONFIG_GERACAO_RELATORIO")
        assert config.CONFIG_GERACAO_RELATORIO
        assert isinstance(config.CONFIG_GERACAO_RELATORIO, dict)

    def test_config_geracao_relatorio_has_required_keys(self):
        """Testa que CONFIG_GERACAO_RELATORIO tem as chaves necessárias."""
        required_keys = [
            "temperature",
            "top_p",
            "top_k",
            "max_output_tokens",
        ]
        for key in required_keys:
            assert (
                key in config.CONFIG_GERACAO_RELATORIO
            ), f"Chave '{key}' não encontrada"

    def test_config_geracao_relatorio_temperature_lower(self):
        """Testa que temperatura do relatório é menor que da análise."""
        assert (
            config.CONFIG_GERACAO_RELATORIO["temperature"]
            < config.CONFIG_GERACAO_ANALISE["temperature"]
        )

    def test_config_geracao_relatorio_no_json_mime_type(self):
        """Testa que CONFIG_GERACAO_RELATORIO não força JSON (permite Markdown)."""
        # Não deve ter response_mime_type ou deve ser diferente de JSON
        assert "response_mime_type" not in config.CONFIG_GERACAO_RELATORIO

    def test_config_values_are_valid(self):
        """Testa que valores de configuração são válidos."""
        # Temperature deve estar entre 0 e 2
        assert 0 <= config.CONFIG_GERACAO_ANALISE["temperature"] <= 2
        assert 0 <= config.CONFIG_GERACAO_RELATORIO["temperature"] <= 2

        # top_p deve ser entre 0 e 1 ou 1
        assert config.CONFIG_GERACAO_ANALISE["top_p"] == 1
        assert config.CONFIG_GERACAO_RELATORIO["top_p"] == 1

        # top_k deve ser positivo
        assert config.CONFIG_GERACAO_ANALISE["top_k"] > 0
        assert config.CONFIG_GERACAO_RELATORIO["top_k"] > 0

        # max_output_tokens deve ser positivo
        assert config.CONFIG_GERACAO_ANALISE["max_output_tokens"] > 0
        assert config.CONFIG_GERACAO_RELATORIO["max_output_tokens"] > 0
