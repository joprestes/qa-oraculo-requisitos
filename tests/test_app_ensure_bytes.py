# tests/test_app_ensure_bytes.py
import io

import app


def test_ensure_bytes_str():
    assert app._ensure_bytes("texto") == b"texto"


def test_ensure_bytes_bytes():
    assert app._ensure_bytes(b"abc") == b"abc"


def test_ensure_bytes_getvalue():
    buffer = io.BytesIO(b"xyz")
    assert app._ensure_bytes(buffer) == b"xyz"


def test_ensure_bytes_getvalue_lanca_excecao_faz_fallback():
    class Broken:
        def getvalue(self):
            raise RuntimeError("falha intencional")

        def __str__(self):
            return "conteudo alternativo"

    resultado = app._ensure_bytes(Broken())

    assert resultado == b"conteudo alternativo"


def test_ensure_bytes_sem_getvalue_usa_str_para_bytes():
    class SemGetValue:
        def __str__(self):
            return "dado com acentuação: çã"

    resultado = app._ensure_bytes(SemGetValue())

    assert resultado == "dado com acentuação: çã".encode("utf-8")
