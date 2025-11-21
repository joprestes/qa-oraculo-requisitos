import logging
from qa_core.security import SanitizedLogger


def test_sanitized_logger_info():
    """Testa que SanitizedLogger.info chama o logger interno."""
    from unittest.mock import MagicMock

    mock_logger = MagicMock(spec=logging.Logger)
    sanitized = SanitizedLogger(mock_logger)

    sanitized.info("Test message")
    mock_logger.info.assert_called_once()


def test_sanitized_logger_warning():
    """Testa que SanitizedLogger.warning chama o logger interno."""
    from unittest.mock import MagicMock

    mock_logger = MagicMock(spec=logging.Logger)
    sanitized = SanitizedLogger(mock_logger)

    sanitized.warning("Warning message")
    mock_logger.warning.assert_called_once()


def test_sanitized_logger_error():
    """Testa que SanitizedLogger.error chama o logger interno."""
    from unittest.mock import MagicMock

    mock_logger = MagicMock(spec=logging.Logger)
    sanitized = SanitizedLogger(mock_logger)

    sanitized.error("Error message")
    mock_logger.error.assert_called_once()


def test_sanitized_logger_debug():
    """Testa que SanitizedLogger.debug chama o logger interno."""
    from unittest.mock import MagicMock

    mock_logger = MagicMock(spec=logging.Logger)
    sanitized = SanitizedLogger(mock_logger)

    sanitized.debug("Debug info")
    mock_logger.debug.assert_called_once()
