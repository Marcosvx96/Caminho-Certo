"""Associação Caminho Certo — Gestão Escolar e Combate à Evasão (MVP).

Telas:
  1. Menu Inicial (dashboard)
  2. Chamada Diária (registro de presença)
  3. Resultados da Chamada (confirmação + alerta de evasão)
Apoio: Cadastro de Alunos e Relatórios.
"""

from __future__ import annotations

import os
from datetime import date

import pandas as pd
import streamlit as st

from database import (
    STATUS_VALIDOS,
    adicionar_aluno,
    faltas_consecutivas,
    frequencias_do_dia,
    init_db,
    listar_alunos,
    listar_turmas,
    remover_aluno,
    salvar_chamada,
)
from demo import semear_demo
from reports import (
    csv_relatorio,
    historico,
    lista_do_dia,
    resumo_dia,
    tabela_geral,
    total_alunos,
)
from styles import apply_custom_styles

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

OPCOES_STATUS = ["PRESENÇA", "AUSÊNCIA", "ATRASO"]
OPCAO_PARA_STATUS = dict(zip(OPCOES_STATUS, STATUS_VALIDOS))
STATUS_PARA_OPCAO = {v: k for k, v in OPCAO_PARA_STATUS.items()}
STATUS_TEXTO = {"P": "PRESENÇA", "A": "AUSÊNCIA", "T": "ATRASO"}
STATUS_CLASSE = {"P": "cc-chip-p", "A": "cc-chip-a", "T": "cc-chip-t"}
AVATAR = {"P": "#4CAF50", "A": "#F44336", "T": "#FFC107"}

st.set_page_config(
    page_title="Associação Caminho Certo",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def fmt_data(valor: str | date) -> str:
    """24/11/2026 -> 24 de Novembro, 2026 (mesmo formato das telas)."""
    d = date.fromisoformat(valor) if isinstance(valor, str) else valor
    return f"{d.day} de {MESES[d.month - 1]}, {d.year}"


def iniciais(nome: str) -> str:
    partes = [p for p in nome.split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def chip(status: str) -> str:
    return f'<span class="cc-chip {STATUS_CLASSE.get(status, "cc-chip-p")}">{STATUS_TEXTO.get(status, "—")}</span>'


def cabecalho() -> None:
    st.markdown(
        """
        <div class="cc-header">
          <div class="cc-logo">🏫</div>
          <div>
            <div class="cc-titulo">GESTÃO COMUNITÁRIA</div>
            <div class="cc-sub">Associação Caminho Certo · Jundiapeba</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ir_para(pagina: str) -> None:
    st.session_state.pagina = pagina
    st.rerun()


def _limpar_selecao_status() -> None:
    """Ao trocar turma/data, as pills voltam ao estado salvo do dia."""
    for chave in [k for k in st.session_state.keys() if str(k).startswith("status_")]:
        del st.session_state[chave]


def _init_state() -> None:
    padroes = {
        "pagina": "home",
        "chamada_data": date.today(),
        "resultado": None,
        "turma_nova": "",
    }
    for chave, valor in padroes.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


# ---------------------------------------------------------------------------
# Tela 1 — Menu Inicial
# ---------------------------------------------------------------------------
def render_home() -> None:
    cabecalho()
    turmas = listar_turmas()

    st.markdown('<div class="cc-secao">Menu Inicial</div>', unsafe_allow_html=True)

    with st.container(border=True, key="card-central"):
        st.markdown('<div class="cc-pill-verde">Funcionalidade central</div>', unsafe_allow_html=True)
        st.markdown('<div class="cc-hero-icone">🗒️</div>', unsafe_allow_html=True)
        st.markdown('<div class="cc-hero-titulo">Chamada Diária</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="cc-hero-desc">Registre a presença da turma em poucos toques. '
            "Tudo é salvo no banco local, sem internet.</div>",
            unsafe_allow_html=True,
        )
        with st.container(key="btn-verde"):
            if st.button("INICIAR CHAMADA", width="stretch", key="home_iniciar"):
                ir_para("chamada")

    st.write("")

    def cartao(icone, titulo, descricao, pagina, chave, rotulo="ABRIR"):
        with st.container(border=True, key=f"card-{chave}"):
            st.markdown(f'<div class="cc-icone">{icone}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="cc-card-titulo">{titulo}</div>', unsafe_allow_html=True)
            if descricao:
                st.markdown(f'<div class="cc-card-desc">{descricao}</div>', unsafe_allow_html=True)
            if st.button(rotulo, width="stretch", key=f"home_{chave}"):
                ir_para(pagina)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        cartao("👤➕", "Cadastro de Alunos", f"{total_alunos()} alunos cadastrados", "alunos", "alunos")
    with col2:
        rotulo_turmas = "1 turma ativa" if len(turmas) == 1 else f"{len(turmas)} turmas ativas"
        cartao("📅", "Histórico de Presenças", rotulo_turmas, "relatorios", "historico")

    col3, col4 = st.columns(2, gap="medium")
    with col3:
        cartao("📊", "Dashboard Simplificado", "Indicadores de frequência", "relatorios", "dashboard")
    with col4:
        cartao("📄", "Relatórios", "Exportar dados em CSV", "relatorios", "relatorios")

    st.write("")
    st.markdown(
        '<div class="cc-contadores"><span class="cc-cont">Home</span>'
        '<span class="cc-cont">Chamada</span>'
        '<span class="cc-cont">Relatórios</span></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tela 2 — Chamada Diária
# ---------------------------------------------------------------------------
def render_chamada() -> None:
    cabecalho()

    st.markdown('<div class="cc-titulo-pagina">Chamada Diária</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-descricao">Selecione a turma, data e registre a presença de cada aluno.</div>',
        unsafe_allow_html=True,
    )

    turmas = listar_turmas()
    if not turmas:
        st.warning("Nenhum aluno cadastrado. Cadastre alunos antes de fazer a chamada.")
        with st.container(key="btn-verde"):
            if st.button("IR PARA CADASTRO DE ALUNOS", width="stretch", key="chamada_ir_alunos"):
                ir_para("alunos")
        if st.button("← Voltar ao Menu Inicial", type="tertiary", key="chamada_voltar_vazio"):
            ir_para("home")
        return

    filtro1, filtro2 = st.columns([2, 2], gap="medium")
    with filtro1:
        turma = st.selectbox(
            "Turma",
            turmas,
            key="sel_turma",
            on_change=_limpar_selecao_status,
        )
    with filtro2:
        data_escolhida = st.date_input(
            "Data",
            key="sel_data",
            on_change=_limpar_selecao_status,
        )

    alunos = listar_alunos(turma)
    data_iso = data_escolhida.isoformat()
    salvos = frequencias_do_dia(data_iso)

    if not alunos:
        st.info("Esta turma não possui alunos.")
    else:
        for aluno in alunos:
            status_atual = salvos.get(aluno["id"], "P")
            with st.container(border=True, key=f"row-{aluno['id']}"):
                c_aluno, c_pills, c_chip = st.columns([4, 4, 2], vertical_alignment="center")
                with c_aluno:
                    st.markdown(
                        f"""
                        <div class="cc-aluno">
                          <div class="cc-avatar">{iniciais(aluno['nome'])}</div>
                          <div>
                            <div class="cc-aluno-nome">{aluno['nome']}</div>
                            <div class="cc-aluno-turma">{aluno['turma']}</div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_pills:
                    escolha = st.pills(
                        "Status",
                        OPCOES_STATUS,
                        default=STATUS_PARA_OPCAO[status_atual],
                        key=f"status_{aluno['id']}",
                        label_visibility="collapsed",
                        required=True,
                    )
                with c_chip:
                    st.markdown(chip(OPCAO_PARA_STATUS.get(escolha or "PRESENÇA", "P")), unsafe_allow_html=True)

        # Contadores em tempo real
        contagem = {"P": 0, "A": 0, "T": 0}
        for aluno in alunos:
            rotulo = st.session_state.get(f"status_{aluno['id']}", "PRESENÇA")
            contagem[OPCAO_PARA_STATUS.get(rotulo, "P")] += 1
        st.markdown(
            f"""
            <div class="cc-contadores">
              <span class="cc-cont cc-cont-p">P: {contagem['P']}</span>
              <span class="cc-cont cc-cont-a">A: {contagem['A']}</span>
              <span class="cc-cont cc-cont-t">T: {contagem['T']}</span>
              <span>Alterações são salvas ao finalizar</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        with st.container(key="btn-verde"):
            if st.button("FINALIZAR E SALVAR CHAMADA", width="stretch", key="chamada_salvar"):
                registros = {}
                for aluno in alunos:
                    rotulo = st.session_state.get(f"status_{aluno['id']}", "PRESENÇA")
                    registros[aluno["id"]] = OPCAO_PARA_STATUS.get(rotulo, "P")
                salvar_chamada(data_iso, registros)
                st.session_state.resultado = {"data": data_iso, "turma": turma}
                ir_para("resultado")

    if st.button("← Voltar ao Menu Inicial", type="tertiary", key="chamada_voltar"):
        ir_para("home")


# ---------------------------------------------------------------------------
# Tela 3 — Resultados da Chamada
# ---------------------------------------------------------------------------
def render_resultado() -> None:
    resultado = st.session_state.get("resultado")
    if not resultado:
        render_home()
        return

    cabecalho()
    data_iso = resultado["data"]
    turma = resultado["turma"]
    resumo = resumo_dia(data_iso, turma)
    linhas = lista_do_dia(data_iso, turma)
    risco = [a for a in faltas_consecutivas(3) if a["turma"] == turma]

    st.markdown('<div class="cc-titulo-pagina">Resultados da Chamada</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="cc-descricao">{turma} · {fmt_data(data_iso)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="cc-card-sucesso">
          <p class="cc-card-titulo-grande">✅ Chamada finalizada com sucesso</p>
          <p class="cc-card-sub">Os registros de {resumo['total']} alunos foram salvos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if risco:
        itens = "".join(
            f'<div class="cc-linha-status"><span><strong>{a["nome"]}</strong></span>'
            f'<span style="color:#C62828;font-weight:700">{a["faltas"]} faltas consecutivas</span></div>'
            for a in risco
        )
        st.markdown(
            f"""
            <div class="cc-card-alerta">
              <p class="cc-card-titulo-grande" style="color:#C62828">⚠️ Atenção — alunos ausentes recorrentes</p>
              <p class="cc-card-sub">Contato com o responsável recomendado.</p>
              {itens}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

    linhas_html = "".join(
        f'<div class="cc-linha-status"><span>{l["nome"]}</span>{chip(l["status"])}</div>' for l in linhas
    )
    st.markdown(
        f"""
        <div class="cc-card-neutro">
          <p class="cc-card-titulo-grande">ℹ️ Resumo de presença</p>
          <div style="display:flex;gap:1.4rem;align-items:flex-end;margin:.8rem 0;">
            <div><div class="cc-taxa">{resumo['taxa']:.0f}%</div>
            <div class="cc-taxa-rotulo">Taxa de comparecimento</div></div>
            <div style="font-size:.78rem;color:#6B7280">Presença + atraso</div>
          </div>
          {linhas_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="cc-contadores" style="margin-top:.9rem">
          <span class="cc-cont cc-cont-p">Presentes: {resumo['P']}</span>
          <span class="cc-cont cc-cont-a">Ausentes: {resumo['A']}</span>
          <span class="cc-cont cc-cont-t">Atrasados: {resumo['T']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    with st.container(key="acoes-finais"):
        b1, b2 = st.columns(2, gap="medium")
        with b1:
            if st.button("NOVA CHAMADA (OUTRA TURMA)", width="stretch", key="res_nova"):
                st.session_state.resultado = None
                ir_para("chamada")
        with b2:
            if st.button("VISUALIZAR RELATÓRIOS", width="stretch", key="res_relatorios"):
                ir_para("relatorios")


# ---------------------------------------------------------------------------
# Apoio — Cadastro de Alunos
# ---------------------------------------------------------------------------
def render_alunos() -> None:
    cabecalho()
    st.markdown('<div class="cc-titulo-pagina">Cadastro de Alunos</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-descricao">Dados de contato do responsável são sensíveis (LGPD): '
        "mantenha o acesso restrito à equipe da associação.</div>",
        unsafe_allow_html=True,
    )

    turmas = listar_turmas()
    opcoes = turmas + ["+ Nova turma"]
    turma_sel = st.selectbox("Turma / Atividade", opcoes, key="cad_turma_sel")

    turma_final = turma_sel
    if turma_sel == "+ Nova turma":
        turma_final = st.text_input("Nome da nova turma", key="cad_turma_nova", placeholder="Ex: Turma B")

    with st.form("form_aluno", clear_on_submit=True):
        nome = st.text_input("Nome completo do aluno")
        responsavel = st.text_input("Nome do responsável")
        contato = st.text_input("Telefone de contato", placeholder="(11) 90000-0000")
        enviado = st.form_submit_button("CADASTRAR ALUNO", width="stretch")

        if enviado:
            if adicionar_aluno(nome, turma_final, responsavel, contato):
                st.success(f"Aluno(a) {nome.strip()} cadastrado(a) com sucesso!")
            else:
                st.error("Preencha o nome do aluno e a turma.")

    st.write("")
    st.markdown('<div class="cc-secao">Alunos cadastrados</div>', unsafe_allow_html=True)
    alunos = listar_alunos()
    if alunos:
        df = pd.DataFrame(alunos).rename(
            columns={"id": "ID", "nome": "Nome", "turma": "Turma", "responsavel": "Responsável", "contato": "Contato"}
        )
        st.dataframe(df, width="stretch", hide_index=True)

        with st.expander("Remover aluno"):
            alvo = st.selectbox(
                "Aluno",
                options=[a["id"] for a in alunos],
                format_func=lambda i: next(a["nome"] for a in alunos if a["id"] == i),
                key="remover_alvo",
            )
            if st.button("REMOVER", key="remover_btn"):
                remover_aluno(int(alvo))
                st.rerun()
    else:
        st.info("Nenhum aluno cadastrado ainda.")

    if st.button("← Voltar ao Menu Inicial", type="tertiary", key="alunos_voltar"):
        ir_para("home")


# ---------------------------------------------------------------------------
# Apoio — Relatórios
# ---------------------------------------------------------------------------
def render_relatorios() -> None:
    cabecalho()
    st.markdown('<div class="cc-titulo-pagina">Relatórios</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-descricao">Indicadores de frequência para identificação preventiva de evasão.</div>',
        unsafe_allow_html=True,
    )

    aba_dash, aba_hist, aba_dados = st.tabs(["Dashboard", "Histórico", "Dados / Exportar"])

    with aba_dash:
        alunos = tabela_geral()
        risco = faltas_consecutivas(3)
        geral = resumo_dia(date.today().isoformat())

        c1, c2, c3 = st.columns(3, gap="medium")
        c1.metric("Alunos", len(alunos))
        c2.metric("Em risco (3+ faltas)", len(risco))
        c3.metric("Chamadas hoje", geral["total"])

        st.write("")
        if risco:
            st.markdown('<div class="cc-secao">Alunos em risco de evasão</div>', unsafe_allow_html=True)
            for a in risco:
                st.markdown(
                    f'<div class="cc-linha-status"><span><strong>{a["nome"]}</strong> · {a["turma"]}</span>'
                    f'<span style="color:#C62828;font-weight:700">{a["faltas"]} faltas</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("Nenhum aluno com 3 ou mais faltas consecutivas.")

    with aba_hist:
        registros = historico(30)
        if registros:
            df_hist = pd.DataFrame(registros)[["data", "total", "P", "A", "T", "taxa"]]
            df_hist.columns = ["Data", "Registros", "Presenças", "Ausências", "Atrasos", "Taxa (%)"]
            st.dataframe(df_hist, width="stretch", hide_index=True)
        else:
            st.info("Nenhuma chamada registrada ainda.")

    with aba_dados:
        dados = tabela_geral()
        if dados:
            df = pd.DataFrame(dados)[
                ["nome", "turma", "presentes", "ausentes", "atrasados", "registros", "taxa"]
            ]
            df.columns = ["Nome", "Turma", "Presenças", "Ausências", "Atrasos", "Registros", "Taxa (%)"]
            st.dataframe(df, width="stretch", hide_index=True)
            st.download_button(
                "BAIXAR CSV",
                data=csv_relatorio(),
                file_name=f"frequencia_caminho_certo_{date.today().isoformat()}.csv",
                mime="text/csv",
                width="stretch",
            )
        else:
            st.info("Sem dados para exportar.")

    if st.button("← Voltar ao Menu Inicial", type="tertiary", key="rel_voltar"):
        ir_para("home")


# ---------------------------------------------------------------------------
# Roteamento
# ---------------------------------------------------------------------------
def _demo_ativo() -> bool:
    """Liga os dados de exemplo sem afetar o uso real (ver src/demo.py)."""
    if os.environ.get("CAMINHO_CERTO_DEMO") == "1":
        return True
    try:
        return bool(st.secrets.get("demo", False))
    except Exception:
        return False


init_db()
if _demo_ativo():
    semear_demo()
apply_custom_styles()
_init_state()

PAGINAS = {
    "home": render_home,
    "chamada": render_chamada,
    "resultado": render_resultado,
    "alunos": render_alunos,
    "relatorios": render_relatorios,
}

PAGINAS.get(st.session_state.pagina, render_home)()
