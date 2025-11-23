from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


LOGGER_NAME = "qa_oraculo.observability"
_LOGGER = logging.getLogger(LOGGER_NAME)

if not _LOGGER.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
        )
    )
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)


def generate_trace_id() -> str:
    """Gera um identificador único para correlacionar eventos do LangGraph."""

    return uuid4().hex


def log_graph_event(
    event: str,
    *,
    trace_id: str | None = None,
    node: str | None = None,
    payload: Mapping[str, Any] | None = None,
    level: int = logging.INFO,
) -> None:
    """
    Registra eventos relacionados à execução dos grafos LangGraph.

    Args:
        event: Nome do evento (ex.: 'node.start', 'model.retry').
        trace_id: Identificador da execução atual.
        node: Nome lógico do nó LangGraph.
        payload: Dados adicionais serializáveis (ou representáveis como string).
        level: Nível do log (default: logging.INFO).
    """

    if not _LOGGER.isEnabledFor(level):
        return

    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
        "event": event,
        "trace_id": trace_id,
        "node": node,
    }

    if payload:
        record["data"] = _stringify_payload(payload)

    try:
        message = json.dumps(record, ensure_ascii=False, default=repr)
    except TypeError:
        message = repr(record)

    _LOGGER.log(level, message)


def _stringify_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Garante que todo o conteúdo do payload seja serializável via JSON,
    convertendo objetos desconhecidos para string com repr().
    """

    safe_payload: dict[str, Any] = {}
    for key, value in payload.items():
        try:
            json.dumps(value)
            safe_payload[key] = value
        except TypeError:
            safe_payload[key] = repr(value)
    return safe_payload
