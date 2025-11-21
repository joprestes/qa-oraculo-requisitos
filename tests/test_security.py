"""Testes para utilitários de segurança."""

from qa_core.security import (
    sanitize_for_logging,
    validate_user_input_length,
    sanitize_filename,
)


class TestSanitizeForLogging:
    """Testes para sanitização de logs."""

    def test_redacts_api_keys(self):
        """Deve remover API keys dos logs."""
        text = "API_KEY=sk-1234567890abcdef"
        result = sanitize_for_logging(text)
        assert "sk-1234567890abcdef" not in result
        assert "REDACTED" in result

    def test_redacts_tokens(self):
        """Deve remover tokens dos logs."""
        text = 'token: "ghp_1234567890abcdef"'
        result = sanitize_for_logging(text)
        assert "ghp_1234567890abcdef" not in result
        assert "REDACTED" in result

    def test_redacts_emails(self):
        """Deve remover emails dos logs."""
        text = "Contato: usuario@exemplo.com"
        result = sanitize_for_logging(text)
        assert "usuario@exemplo.com" not in result
        assert "EMAIL_REDACTED" in result

    def test_redacts_cpf(self):
        """Deve remover CPFs dos logs."""
        text = "CPF: 123.456.789-00"
        result = sanitize_for_logging(text)
        assert "123.456.789-00" not in result
        assert "CPF_REDACTED" in result

    def test_truncates_long_text(self):
        """Deve truncar textos longos."""
        text = "a" * 200
        result = sanitize_for_logging(text, max_length=50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_handles_none(self):
        """Deve lidar com None."""
        result = sanitize_for_logging(None)
        assert result == "<None>"


class TestValidateUserInputLength:
    """Testes para validação de comprimento de entrada."""

    def test_accepts_valid_input(self):
        """Deve aceitar entrada válida."""
        text = "User story válida"
        assert validate_user_input_length(text) is True

    def test_rejects_empty_input(self):
        """Deve rejeitar entrada vazia."""
        assert validate_user_input_length("") is False
        assert validate_user_input_length(None) is False

    def test_rejects_too_long_input(self):
        """Deve rejeitar entrada muito longa."""
        text = "a" * 60000
        assert validate_user_input_length(text, max_length=50000) is False

    def test_accepts_at_limit(self):
        """Deve aceitar entrada no limite."""
        text = "a" * 1000
        assert validate_user_input_length(text, max_length=1000) is True


class TestSanitizeFilename:
    """Testes para sanitização de nomes de arquivo."""

    def test_removes_dangerous_characters(self):
        """Deve remover caracteres perigosos."""
        filename = "test/../../../etc/passwd"
        result = sanitize_filename(filename)
        assert ".." not in result
        assert "/" not in result

    def test_replaces_spaces_with_underscores(self):
        """Deve substituir espaços por underscores."""
        filename = "meu arquivo teste.txt"
        result = sanitize_filename(filename)
        assert " " not in result
        assert "_" in result

    def test_preserves_extension(self):
        """Deve preservar extensão do arquivo."""
        filename = "documento.pdf"
        result = sanitize_filename(filename)
        assert result.endswith(".pdf")

    def test_limits_length(self):
        """Deve limitar comprimento do nome."""
        filename = "a" * 300 + ".txt"
        result = sanitize_filename(filename)
        assert len(result) <= 255

    def test_handles_empty_filename(self):
        """Deve lidar com nome vazio."""
        result = sanitize_filename("")
        assert result == "arquivo"

    def test_removes_multiple_dots(self):
        """Deve remover pontos múltiplos."""
        filename = "arquivo...teste.txt"
        result = sanitize_filename(filename)
        assert "..." not in result
