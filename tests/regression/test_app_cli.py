import importlib
import subprocess
import sys

import pytest

from qa_core import app


def test_main_execucao_direta_reload(monkeypatch):
    monkeypatch.setattr(app, "__name__", "__main__")
    importlib.reload(app)
    assert True


@pytest.mark.slow
def test_main_execucao_direta_subprocess():
    result = subprocess.run(
        [sys.executable, "-m", "qa_core.app"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
