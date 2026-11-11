"""Suíte de testes do MVP Caminho Certo."""

from __future__ import annotations

import csv
import io

import pytest

from database import (
    adicionar_aluno,
    faltas_consecutivas,
    frequencias_do_dia,
    init_db,
    listar_alunos,
    listar_turmas,
    registrar_frequencia,
    remover_aluno,
    salvar_chamada,
)
from reports import csv_relatorio, lista_do_dia, resumo_dia, tabela_geral


# ---------------------------------------------------------------------------
# Alunos
# ---------------------------------------------------------------------------
def test_init_db_e_idempotente():
    init_db()
    init_db()  # não deve lançar erro na segunda execução
    assert listar_alunos() == []


def test_adicionar_aluno_sucesso():
    assert adicionar_aluno("João Silva", "Turma A", "Maria Silva", "11999999999") is True
    alunos = listar_alunos()
    assert len(alunos) == 1
    assert alunos[0]["nome"] == "João Silva"
    assert alunos[0]["turma"] == "Turma A"


def test_adicionar_aluno_sem_nome_falha():
    assert adicionar_aluno("", "Turma A", "Maria", "1199") is False
    assert adicionar_aluno("   ", "Turma A", "Maria", "1199") is False
    assert listar_alunos() == []


def test_adicionar_aluno_sem_turma_falha():
    assert adicionar_aluno("João", "", "Maria", "1199") is False
    assert listar_alunos() == []


def test_listar_alunos_ordenado_por_nome():
    adicionar_aluno("Zeca", "Turma A")
    adicionar_aluno("Ana", "Turma A")
    adicionar_aluno("Bruno", "Turma B")
    nomes = [a["nome"] for a in listar_alunos()]
    assert nomes == ["Ana", "Bruno", "Zeca"]


def test_listar_alunos_filtra_por_turma():
    adicionar_aluno("Ana", "Turma A")
    adicionar_aluno("Bruno", "Turma B")
    assert [a["nome"] for a in listar_alunos("Turma B")] == ["Bruno"]


def test_listar_turmas_sem_repeticao():
    adicionar_aluno("Ana", "Turma A")
    adicionar_aluno("Bruno", "Turma A")
    adicionar_aluno("Caio", "Turma B")
    assert listar_turmas() == ["Turma A", "Turma B"]


def test_remover_aluno_apaga_frequencias():
    adicionar_aluno("Ana", "Turma A")
    aluno_id = listar_alunos()[0]["id"]
    registrar_frequencia(aluno_id, "2026-11-10", "P")

    assert remover_aluno(aluno_id) is True
    assert listar_alunos() == []
    assert frequencias_do_dia("2026-11-10") == {}


# ---------------------------------------------------------------------------
# Frequência
# ---------------------------------------------------------------------------
def _aluno(nome="Ana", turma="Turma A") -> int:
    adicionar_aluno(nome, turma)
    return next(a["id"] for a in listar_alunos() if a["nome"] == nome)


def test_registrar_frequencia_presenca():
    aluno_id = _aluno()
    registrar_frequencia(aluno_id, "2026-11-10", "P")
    assert frequencias_do_dia("2026-11-10") == {aluno_id: "P"}


def test_chamada_repetida_atualiza_em_vez_de_duplicar():
    aluno_id = _aluno()
    registrar_frequencia(aluno_id, "2026-11-10", "P")
    registrar_frequencia(aluno_id, "2026-11-10", "A")

    dia = frequencias_do_dia("2026-11-10")
    assert dia == {aluno_id: "A"}
    assert len(dia) == 1


def test_status_invalido_e_rejeitado():
    aluno_id = _aluno()
    with pytest.raises(ValueError):
        registrar_frequencia(aluno_id, "2026-11-10", "X")
    with pytest.raises(ValueError):
        salvar_chamada("2026-11-10", {aluno_id: "Z"})


def test_salvar_chamada_turma_inteira():
    a1 = _aluno("Ana")
    a2 = _aluno("Bruno")
    total = salvar_chamada("2026-11-10", {a1: "P", a2: "A"})
    assert total == 2
    assert frequencias_do_dia("2026-11-10") == {a1: "P", a2: "A"}


def test_salvar_chamada_vazia_retorna_zero():
    assert salvar_chamada("2026-11-10", {}) == 0


# ---------------------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------------------
def test_resumo_dia_conta_status():
    a1 = _aluno("Ana")
    a2 = _aluno("Bruno")
    a3 = _aluno("Caio")
    salvar_chamada("2026-11-10", {a1: "P", a2: "A", a3: "T"})

    resumo = resumo_dia("2026-11-10")
    assert resumo["P"] == 1
    assert resumo["A"] == 1
    assert resumo["T"] == 1
    assert resumo["total"] == 3
    assert resumo["taxa"] == 66.7  # presença + atraso


def test_resumo_dia_sem_registros():
    resumo = resumo_dia("2026-01-01")
    assert resumo == {"P": 0, "A": 0, "T": 0, "total": 0, "taxa": 0.0}


def test_resumo_dia_filtra_por_turma():
    a1 = _aluno("Ana", "Turma A")
    a2 = _aluno("Bruno", "Turma B")
    salvar_chamada("2026-11-10", {a1: "P", a2: "A"})

    assert resumo_dia("2026-11-10", "Turma A")["P"] == 1
    assert resumo_dia("2026-11-10", "Turma B")["total"] == 1


def test_lista_do_dia_traz_status():
    a1 = _aluno("Ana")
    salvar_chamada("2026-11-10", {a1: "T"})
    linhas = lista_do_dia("2026-11-10")
    assert linhas == [{"id": a1, "nome": "Ana", "turma": "Turma A", "status": "T"}]


def test_tabela_geral_calcula_taxa_por_aluno():
    a1 = _aluno("Ana")
    registrar_frequencia(a1, "2026-11-10", "P")
    registrar_frequencia(a1, "2026-11-11", "A")
    registrar_frequencia(a1, "2026-11-12", "T")
    registrar_frequencia(a1, "2026-11-13", "P")

    linha = tabela_geral()[0]
    assert linha["presentes"] == 2
    assert linha["ausentes"] == 1
    assert linha["atrasados"] == 1
    assert linha["registros"] == 4
    assert linha["taxa"] == 75.0


def test_faltas_consecutivas_detecta_alerta():
    a1 = _aluno("Ana")
    for dia in ("2026-11-08", "2026-11-09", "2026-11-10"):
        registrar_frequencia(a1, dia, "A")

    alertas = faltas_consecutivas(3)
    assert len(alertas) == 1
    assert alertas[0]["faltas"] == 3


def test_faltas_consecutivas_ignora_sequencia_quebrada():
    a1 = _aluno("Ana")
    registrar_frequencia(a1, "2026-11-06", "A")
    registrar_frequencia(a1, "2026-11-07", "A")
    registrar_frequencia(a1, "2026-11-08", "P")  # quebra a sequência
    registrar_frequencia(a1, "2026-11-09", "A")

    assert faltas_consecutivas(3) == []


def test_csv_exporta_cabecalho_e_linhas():
    a1 = _aluno("Ana")
    registrar_frequencia(a1, "2026-11-10", "P")

    conteudo = csv_relatorio().decode("utf-8-sig")
    linhas = list(csv.reader(io.StringIO(conteudo), delimiter=";"))
    assert linhas[0][:3] == ["ID", "Nome", "Turma"]
    assert linhas[1][1] == "Ana"
    assert linhas[1][-1] == "100,0"
