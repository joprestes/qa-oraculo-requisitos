# =========================================================
# tests/test_format_datetime.py
# =========================================================
"""Testes dedicados à função format_datetime do módulo app."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from qa_core import app


@pytest.mark.parametrize(
    "valor,esperado",
    [
        ("2024-03-15T13:45:00", "15/03/2024 13:45"),
        (datetime(2024, 1, 5, 9, 30), "05/01/2024 09:30"),
        (123, "123"),
    ],
)
def test_format_datetime_formata_inputs_validos(valor, esperado):
    assert app.format_datetime(valor) == esperado


def test_format_datetime_retorna_original_para_string_nao_iso():
    valor = "data invalida"
    assert app.format_datetime(valor) is valor


def test_format_datetime_usa_strftime_quando_disponivel():
    mock_value = MagicMock()
    mock_value.strftime.return_value = "31/12/2024 23:59"

    resultado = app.format_datetime(mock_value)

    mock_value.strftime.assert_called_once_with("%d/%m/%Y %H:%M")
    assert resultado == "31/12/2024 23:59"
