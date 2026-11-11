"""Configuração dos testes: isola o banco em arquivo temporário.

Isso evita o bug crítico da spec original, em que o pytest apagava os dados
reais em data/db.sqlite3.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(autouse=True)
def banco_isolado(tmp_path, monkeypatch):
    monkeypatch.setenv("CAMINHO_CERTO_DB", str(tmp_path / "teste.sqlite3"))
    import database

    database.init_db()
    yield
