"""Dados de demonstração para o app publicado (link de avaliação).

O seed é **opcional** e desligado por padrão. É ativado quando:

- a variável de ambiente ``CAMINHO_CERTO_DEMO=1`` está definida (uso local), ou
- o app tem o secret ``demo = true`` (Streamlit Community Cloud).

Só popula o banco quando ele está vazio, então nunca sobrescreve dados reais.
"""

from __future__ import annotations

from database import adicionar_aluno, listar_alunos, registrar_frequencia

ALUNOS = ["João Silva", "Maria Santos", "Pedro Oliveira", "Luana Gomes", "Carlos Pinto"]
DIAS = ("2026-11-04", "2026-11-05", "2026-11-06")
EM_RISCO = {"Pedro Oliveira", "Carlos Pinto"}


def semear_demo() -> bool:
    """Cria alunos e histórico de exemplo. Retorna True se algo foi criado."""
    if listar_alunos():
        return False

    for nome in ALUNOS:
        adicionar_aluno(nome, "Turma A", f"Responsável de {nome.split()[0]}", "(11) 90000-0000")

    ids = {a["nome"]: a["id"] for a in listar_alunos()}
    for dia in DIAS:
        for nome, aluno_id in ids.items():
            registrar_frequencia(aluno_id, dia, "A" if nome in EM_RISCO else "P")

    return True
