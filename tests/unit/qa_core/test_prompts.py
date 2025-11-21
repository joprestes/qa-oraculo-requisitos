"""
Testes unitários para qa_core.prompts
"""

from qa_core import prompts


class TestPrompts:
    """Testes para os prompts definidos em prompts.py."""

    def test_prompt_analise_us_exists(self):
        """Testa que PROMPT_ANALISE_US está definido."""
        assert hasattr(prompts, "PROMPT_ANALISE_US")
        assert prompts.PROMPT_ANALISE_US
        assert isinstance(prompts.PROMPT_ANALISE_US, str)
        assert len(prompts.PROMPT_ANALISE_US) > 0

    def test_prompt_analise_us_contains_json_instructions(self):
        """Testa que PROMPT_ANALISE_US contém instruções sobre JSON."""
        assert "JSON" in prompts.PROMPT_ANALISE_US.upper()
        assert "avaliacao_geral" in prompts.PROMPT_ANALISE_US
        assert "pontos_ambiguos" in prompts.PROMPT_ANALISE_US

    def test_prompt_gerar_relatorio_analise_exists(self):
        """Testa que PROMPT_GERAR_RELATORIO_ANALISE está definido."""
        assert hasattr(prompts, "PROMPT_GERAR_RELATORIO_ANALISE")
        assert prompts.PROMPT_GERAR_RELATORIO_ANALISE
        assert isinstance(prompts.PROMPT_GERAR_RELATORIO_ANALISE, str)
        assert len(prompts.PROMPT_GERAR_RELATORIO_ANALISE) > 0

    def test_prompt_gerar_relatorio_analise_contains_markdown(self):
        """Testa que PROMPT_GERAR_RELATORIO_ANALISE contém instruções sobre Markdown."""
        assert "Markdown" in prompts.PROMPT_GERAR_RELATORIO_ANALISE
        assert "User Story" in prompts.PROMPT_GERAR_RELATORIO_ANALISE

    def test_prompt_criar_plano_de_testes_exists(self):
        """Testa que PROMPT_CRIAR_PLANO_DE_TESTES está definido."""
        assert hasattr(prompts, "PROMPT_CRIAR_PLANO_DE_TESTES")
        assert prompts.PROMPT_CRIAR_PLANO_DE_TESTES
        assert isinstance(prompts.PROMPT_CRIAR_PLANO_DE_TESTES, str)
        assert len(prompts.PROMPT_CRIAR_PLANO_DE_TESTES) > 0

    def test_prompt_criar_plano_de_testes_contains_gherkin(self):
        """Testa que PROMPT_CRIAR_PLANO_DE_TESTES contém instruções sobre Gherkin."""
        assert "Gherkin" in prompts.PROMPT_CRIAR_PLANO_DE_TESTES
        assert "casos_de_teste_gherkin" in prompts.PROMPT_CRIAR_PLANO_DE_TESTES

    def test_prompt_criar_plano_de_testes_contains_a11y(self):
        """Testa que PROMPT_CRIAR_PLANO_DE_TESTES contém instruções sobre acessibilidade."""
        assert "acessibilidade" in prompts.PROMPT_CRIAR_PLANO_DE_TESTES.lower()
        assert "WCAG" in prompts.PROMPT_CRIAR_PLANO_DE_TESTES

    def test_prompt_gerar_relatorio_completo_exists(self):
        """Testa que PROMPT_GERAR_RELATORIO_COMPLETO está definido."""
        assert hasattr(prompts, "PROMPT_GERAR_RELATORIO_COMPLETO")
        assert prompts.PROMPT_GERAR_RELATORIO_COMPLETO
        assert isinstance(prompts.PROMPT_GERAR_RELATORIO_COMPLETO, str)
        assert len(prompts.PROMPT_GERAR_RELATORIO_COMPLETO) > 0

    def test_prompt_gerar_relatorio_plano_de_testes_exists(self):
        """Testa que PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES está definido."""
        assert hasattr(prompts, "PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES")
        assert prompts.PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES
        assert isinstance(prompts.PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES, str)
        assert len(prompts.PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES) > 0

    def test_prompt_gerar_relatorio_plano_de_testes_contains_structure(self):
        """Testa que PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES contém estrutura."""
        assert (
            "Plano de Testes Sugerido" in prompts.PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES
        )
        assert "Markdown" in prompts.PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES

    def test_all_prompts_are_strings(self):
        """Testa que todos os prompts são strings não vazias."""
        prompt_names = [
            "PROMPT_ANALISE_US",
            "PROMPT_GERAR_RELATORIO_ANALISE",
            "PROMPT_CRIAR_PLANO_DE_TESTES",
            "PROMPT_GERAR_RELATORIO_COMPLETO",
            "PROMPT_GERAR_RELATORIO_PLANO_DE_TESTES",
        ]

        for prompt_name in prompt_names:
            prompt_value = getattr(prompts, prompt_name)
            assert isinstance(prompt_value, str), f"{prompt_name} não é string"
            assert len(prompt_value) > 0, f"{prompt_name} está vazio"
