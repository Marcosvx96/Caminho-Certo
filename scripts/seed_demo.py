"""Popula o banco com dados de demonstração (opcional).

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\seed_demo.py

Cria 5 alunos na Turma A e três dias de histórico, deixando dois alunos
com 3 faltas consecutivas para exibir o alerta de evasão.
"""

from __future__ import annotations

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from database import (  # noqa: E402
    adicionar_aluno,
    init_db,
    listar_alunos,
    registrar_frequencia,
)

ALUNOS = ["João Silva", "Maria Santos", "Pedro Oliveira", "Luana Gomes", "Carlos Pinto"]
DIAS = ("2026-11-04", "2026-11-05", "2026-11-06")
EM_RISCO = {"Pedro Oliveira", "Carlos Pinto"}


def main() -> None:
    init_db()
    if listar_alunos():
        print("Banco já possui alunos; nada foi alterado.")
        return

    for nome in ALUNOS:
        adicionar_aluno(nome, "Turma A", f"Responsável de {nome.split()[0]}", "(11) 90000-0000")

    ids = {a["nome"]: a["id"] for a in listar_alunos()}
    for dia in DIAS:
        for nome, aluno_id in ids.items():
            registrar_frequencia(aluno_id, dia, "A" if nome in EM_RISCO else "P")

    print(f"{len(ids)} alunos criados em 'Turma A' com {len(DIAS)} dias de histórico.")


if __name__ == "__main__":
    main()
