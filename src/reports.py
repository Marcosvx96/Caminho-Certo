"""Relatórios e indicadores de frequência (combate à evasão)."""

from __future__ import annotations

import csv
import io

from database import get_connection, listar_alunos


def resumo_dia(data: str, turma: str | None = None) -> dict:
    """Contagem de presenças, ausências e atrasos de uma data."""
    sql = "SELECT f.status, COUNT(*) AS total FROM frequencias f"
    params: list = []
    if turma:
        sql += " JOIN alunos a ON a.id = f.aluno_id WHERE f.data = ? AND a.turma = ?"
        params = [data, turma]
    else:
        sql += " WHERE f.data = ?"
        params = [data]
    sql += " GROUP BY f.status"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    contagem = {r["status"]: r["total"] for r in rows}
    presentes = contagem.get("P", 0)
    ausentes = contagem.get("A", 0)
    atrasados = contagem.get("T", 0)
    total = presentes + ausentes + atrasados
    # Comparecimento = presença + atraso (o aluno esteve na atividade).
    taxa = round((presentes + atrasados) / total * 100, 1) if total else 0.0

    return {
        "P": presentes,
        "A": ausentes,
        "T": atrasados,
        "total": total,
        "taxa": taxa,
    }


def lista_do_dia(data: str, turma: str | None = None) -> list[dict]:
    sql = """
        SELECT a.id, a.nome, a.turma, f.status
        FROM frequencias f
        JOIN alunos a ON a.id = f.aluno_id
        WHERE f.data = ?
    """
    params: list = [data]
    if turma:
        sql += " AND a.turma = ?"
        params.append(turma)
    sql += " ORDER BY a.nome COLLATE NOCASE"

    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def tabela_geral() -> list[dict]:
    """Indicadores por aluno: contagens e taxa de comparecimento."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                a.id,
                a.nome,
                a.turma,
                COALESCE(SUM(CASE WHEN f.status = 'P' THEN 1 ELSE 0 END), 0) AS presentes,
                COALESCE(SUM(CASE WHEN f.status = 'A' THEN 1 ELSE 0 END), 0) AS ausentes,
                COALESCE(SUM(CASE WHEN f.status = 'T' THEN 1 ELSE 0 END), 0) AS atrasados,
                COUNT(f.id) AS registros
            FROM alunos a
            LEFT JOIN frequencias f ON f.aluno_id = a.id
            GROUP BY a.id, a.nome, a.turma
            ORDER BY a.nome COLLATE NOCASE
            """
        ).fetchall()

    dados = []
    for r in rows:
        item = dict(r)
        total = item["registros"]
        item["taxa"] = round((item["presentes"] + item["atrasados"]) / total * 100, 1) if total else 0.0
        dados.append(item)
    return dados


def historico(limite: int = 30) -> list[dict]:
    """Últimas datas com chamada registrada e o resumo de cada uma."""
    with get_connection() as conn:
        datas = [
            r["data"]
            for r in conn.execute(
                "SELECT DISTINCT data FROM frequencias ORDER BY data DESC LIMIT ?", (limite,)
            ).fetchall()
        ]
    return [{"data": d, **resumo_dia(d)} for d in datas]


def csv_relatorio() -> bytes:
    """Relatório completo em CSV (UTF-8 com BOM para abrir no Excel)."""
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=";")
    escritor.writerow(["ID", "Nome", "Turma", "Presenças", "Ausências", "Atrasos", "Registros", "Taxa (%)"])
    for linha in tabela_geral():
        escritor.writerow(
            [
                linha["id"],
                linha["nome"],
                linha["turma"],
                linha["presentes"],
                linha["ausentes"],
                linha["atrasados"],
                linha["registros"],
                str(linha["taxa"]).replace(".", ","),
            ]
        )
    return buffer.getvalue().encode("utf-8-sig")


def total_alunos() -> int:
    return len(listar_alunos())
