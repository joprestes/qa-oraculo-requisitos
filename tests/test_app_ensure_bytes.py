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


def test_ensure_bytes_objeto_generico():
    class Fake:
        def __str__(self):
            return "fake"

    assert app._ensure_bytes(Fake()) == b"fake"
