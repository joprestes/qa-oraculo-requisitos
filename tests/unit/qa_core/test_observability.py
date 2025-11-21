import logging
from unittest.mock import patch
from qa_core.observability import (
    generate_trace_id,
    log_graph_event,
    _stringify_payload,
)


def test_generate_trace_id_returns_hex_string():
    """Testa que generate_trace_id retorna uma string hexadecimal."""
    trace_id = generate_trace_id()
    assert isinstance(trace_id, str)
    assert len(trace_id) == 32  # UUID4 hex tem 32 caracteres
    # Verifica que é hexadecimal
    int(trace_id, 16)


def test_log_graph_event_basic():
    """Testa log_graph_event com parâmetros básicos."""
    with patch("qa_core.observability._LOGGER") as mock_logger:
        mock_logger.isEnabledFor.return_value = True
        log_graph_event("test.event", trace_id="abc123", node="test_node")
        mock_logger.log.assert_called_once()
        args = mock_logger.log.call_args
        assert args[0][0] == logging.INFO
        assert "test.event" in args[0][1]
        assert "abc123" in args[0][1]


def test_log_graph_event_with_payload():
    """Testa log_graph_event com payload."""
    with patch("qa_core.observability._LOGGER") as mock_logger:
        mock_logger.isEnabledFor.return_value = True
        log_graph_event(
            "test.event",
            trace_id="xyz",
            node="node1",
            payload={"key": "value", "num": 42},
        )
        mock_logger.log.assert_called_once()
        args = mock_logger.log.call_args
        message = args[0][1]
        assert "key" in message
        assert "value" in message


def test_log_graph_event_disabled_level():
    """Testa que log não é emitido se o nível estiver desabilitado."""
    with patch("qa_core.observability._LOGGER") as mock_logger:
        mock_logger.isEnabledFor.return_value = False
        log_graph_event("test.event", trace_id="abc")
        mock_logger.log.assert_not_called()


def test_log_graph_event_with_non_serializable_payload():
    """Testa log_graph_event com payload não serializável."""
    with patch("qa_core.observability._LOGGER") as mock_logger:
        mock_logger.isEnabledFor.return_value = True

        class CustomObject:
            def __repr__(self):
                return "<CustomObject>"

        log_graph_event(
            "test.event", trace_id="xyz", payload={"obj": CustomObject()}
        )
        mock_logger.log.assert_called_once()


def test_stringify_payload_with_serializable_data():
    """Testa _stringify_payload com dados serializáveis."""
    payload = {"str": "text", "num": 123, "bool": True}
    result = _stringify_payload(payload)
    assert result == payload


def test_stringify_payload_with_non_serializable_data():
    """Testa _stringify_payload com dados não serializáveis."""

    class NonSerializable:
        def __repr__(self):
            return "<NonSerializable>"

    payload = {"good": "value", "bad": NonSerializable()}
    result = _stringify_payload(payload)
    assert result["good"] == "value"
    assert result["bad"] == "<NonSerializable>"
