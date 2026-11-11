"""Camada de dados do sistema Caminho Certo.

Persistência em SQLite com foco em integridade:
- restrição UNIQUE (aluno_id, data) evita chamada duplicada no mesmo dia;
- UPSERT garante que reenviar a chamada atualiza em vez de duplicar;
- o banco pode ser isolado por teste via variável de ambiente CAMINHO_CERTO_DB.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "db.sqlite3")

STATUS_VALIDOS = ("P", "A", "T")  # Presente, Ausente, Atrasado


def db_path() -> str:
    """Caminho do banco ativo (permite isolar testes)."""
    return os.environ.get("CAMINHO_CERTO_DB", DEFAULT_DB_PATH)


@contextmanager
def get_connection():
    """Conexão com commit/rollback automáticos e fechamento garantido."""
    caminho = db_path()
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Cria o schema quando necessário. Idempotente."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS alunos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT NOT NULL,
                turma       TEXT NOT NULL,
                responsavel TEXT NOT NULL DEFAULT '',
                contato     TEXT NOT NULL DEFAULT '',
                criado_em   TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS frequencias (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                data     TEXT NOT NULL,
                status   TEXT NOT NULL CHECK (status IN ('P', 'A', 'T')),
                FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE CASCADE,
                UNIQUE (aluno_id, data)
            );

            CREATE INDEX IF NOT EXISTS idx_frequencias_data ON frequencias (data);
            """
        )


# ---------------------------------------------------------------------------
# Alunos
# ---------------------------------------------------------------------------
def adicionar_aluno(nome: str, turma: str, responsavel: str = "", contato: str = "") -> bool:
    """Insere um aluno. Retorna False quando nome ou turma estão vazios."""
    nome = (nome or "").strip()
    turma = (turma or "").strip()
    if not nome or not turma:
        return False

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO alunos (nome, turma, responsavel, contato) VALUES (?, ?, ?, ?)",
            (nome, turma, (responsavel or "").strip(), (contato or "").strip()),
        )
    return True


def listar_alunos(turma: str | None = None) -> list[dict]:
    sql = "SELECT id, nome, turma, responsavel, contato FROM alunos"
    params: tuple = ()
    if turma:
        sql += " WHERE turma = ?"
        params = (turma,)
    sql += " ORDER BY nome COLLATE NOCASE"

    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def listar_turmas() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT turma FROM alunos ORDER BY turma COLLATE NOCASE").fetchall()
    return [r["turma"] for r in rows]


def remover_aluno(aluno_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Frequência
# ---------------------------------------------------------------------------
def registrar_frequencia(aluno_id: int, data: str, status: str) -> bool:
    """Grava/atualiza a presença de um aluno em uma data (ISO: YYYY-MM-DD)."""
    if status not in STATUS_VALIDOS:
        raise ValueError(f"Status inválido: {status!r}. Use um de {STATUS_VALIDOS}.")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO frequencias (aluno_id, data, status) VALUES (?, ?, ?)
            ON CONFLICT (aluno_id, data) DO UPDATE SET status = excluded.status
            """,
            (aluno_id, data, status),
        )
    return True


def salvar_chamada(data: str, registros: dict[int, str]) -> int:
    """Salva a chamada inteira do dia em uma única transação."""
    itens = [(int(aid), data, st) for aid, st in registros.items()]
    if not itens:
        return 0
    for _, _, st in itens:
        if st not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {st!r}")

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO frequencias (aluno_id, data, status) VALUES (?, ?, ?)
            ON CONFLICT (aluno_id, data) DO UPDATE SET status = excluded.status
            """,
            itens,
        )
    return len(itens)


def frequencias_do_dia(data: str) -> dict[int, str]:
    with get_connection() as conn:
        rows = conn.execute("SELECT aluno_id, status FROM frequencias WHERE data = ?", (data,)).fetchall()
    return {r["aluno_id"]: r["status"] for r in rows}


def ultima_data_registrada() -> str | None:
    with get_connection() as conn:
        row = conn.execute("SELECT MAX(data) AS d FROM frequencias").fetchone()
    return row["d"] if row and row["d"] else None


def faltas_consecutivas(limite: int = 3) -> list[dict]:
    """Alunos com `limite` ou mais ausências consecutivas a partir do último registro.

    É o núcleo do combate à evasão: quem falta seguidamente entra no alerta.
    """
    alertas: list[dict] = []
    for aluno in listar_alunos():
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT data, status FROM frequencias WHERE aluno_id = ? ORDER BY data DESC",
                (aluno["id"],),
            ).fetchall()

        faltas = 0
        ultima_falta = None
        for r in rows:
            if r["status"] != "A":
                break
            faltas += 1
            if ultima_falta is None:
                ultima_falta = r["data"]

        if faltas >= limite:
            alertas.append({**aluno, "faltas": faltas, "ultima_falta": ultima_falta})

    return sorted(alertas, key=lambda a: (-a["faltas"], a["nome"]))
