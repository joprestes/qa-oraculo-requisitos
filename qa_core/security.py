"""Utilitários de segurança para sanitização e validação."""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def sanitize_for_logging(data: Any, max_length: int = 100) -> str:
    """
    Sanitiza dados para logging, removendo informações sensíveis.

    Args:
        data: Dados a serem sanitizados
        max_length: Comprimento máximo do output

    Returns:
        String sanitizada segura para logging
    """
    if data is None:
        return "<None>"

    # Converte para string
    text = str(data)

    # Remove possíveis API keys (padrões comuns)
    text = re.sub(
        r'(api[_-]?key|token|secret|password)["\s:=]+[\w\-]{10,}',
        r"\1=<REDACTED>",
        text,
        flags=re.IGNORECASE,
    )

    # Remove emails
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "<EMAIL_REDACTED>", text
    )

    # Remove possíveis CPFs (formato XXX.XXX.XXX-XX)
    text = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "<CPF_REDACTED>", text)

    # Trunca se muito longo
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text


def validate_user_input_length(text: str, max_length: int = 50000) -> bool:
    """
    Valida o comprimento de entrada do usuário.

    Args:
        text: Texto a validar
        max_length: Comprimento máximo permitido

    Returns:
        True se válido, False caso contrário
    """
    if not text:
        return False

    if len(text) > max_length:
        logger.warning(f"Input excede comprimento máximo: {len(text)} > {max_length}")
        return False

    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres perigosos.

    Args:
        filename: Nome do arquivo original

    Returns:
        Nome de arquivo sanitizado
    """
    # Remove caracteres perigosos
    sanitized = re.sub(r"[^\w\s\-\.]", "", filename)

    # Remove espaços múltiplos
    sanitized = re.sub(r"\s+", "_", sanitized)

    # Remove pontos múltiplos
    sanitized = re.sub(r"\.+", ".", sanitized)

    # Limita comprimento
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        sanitized = name[:250] + ("." + ext if ext else "")

    return sanitized or "arquivo"


class RateLimiter:
    """
    Implementação simples de Rate Limiting (Token Bucket ou Janela Fixa).
    Para este MVP, usaremos uma janela fixa em memória.
    """

    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = []

    def is_allowed(self) -> bool:
        import time

        now = time.time()
        # Remove chamadas antigas fora da janela
        self.calls = [t for t in self.calls if now - t < self.period_seconds]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False


class SanitizedLogger:
    """
    Wrapper de logger que sanitiza mensagens antes de emitir.
    """
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(sanitize_for_logging(msg), *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(sanitize_for_logging(msg), *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(sanitize_for_logging(msg), *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(sanitize_for_logging(msg), *args, **kwargs)

