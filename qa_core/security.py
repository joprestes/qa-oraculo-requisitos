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
