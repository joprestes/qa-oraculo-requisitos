"""Abstrações para provedores de LLM utilizados no QA Oráculo."""

from .config import LLMSettings
from .factory import get_llm_client

__all__ = ["LLMSettings", "get_llm_client"]
