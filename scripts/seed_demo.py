"""Popula o banco com dados de demonstração (opcional).

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\seed_demo.py

Cria 5 alunos na Turma A e três dias de histórico, deixando dois alunos
com 3 faltas consecutivas para exibir o alerta de evasão.
O app também usa a mesma rotina quando o secret ``demo = true`` está ativo
(ver src/demo.py).
"""

from __future__ import annotations

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from database import init_db  # noqa: E402
from demo import semear_demo  # noqa: E402


def main() -> None:
    init_db()
    if semear_demo():
        print("5 alunos criados em 'Turma A' com 3 dias de histórico.")
    else:
        print("Banco já possui alunos; nada foi alterado.")


if __name__ == "__main__":
    main()
