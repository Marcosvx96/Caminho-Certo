"""Gera o PDF de apresentação do MVP Caminho Certo.

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\gerar_pdf.py

Requer as capturas em docs/screenshots (gere antes com scripts/capturar_telas.py).
"""

from __future__ import annotations

import os
import sys

from fpdf import FPDF
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(RAIZ, "docs", "screenshots")
SAIDA = os.path.join(RAIZ, "docs", "Apresentacao_Caminho_Certo.pdf")

VERDE = (76, 175, 80)
VERDE_ESCURO = (124, 179, 66)
TINTA = (17, 17, 17)
CINZA = (107, 114, 128)
BORDA = (230, 230, 230)
FUNDO = (245, 245, 245)
BRANCO = (255, 255, 255)
VERMELHO = (198, 40, 40)
AMBAR = (141, 110, 0)

LARGURA = 297.0
ALTURA = 210.0
MARGEM = 14.0
CONTEUDO = LARGURA - 2 * MARGEM
FIM = ALTURA - 18.0


def fonte(caminho: str) -> str:
    candidatos = [
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", caminho),
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "segoeui.ttf"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(fonte)


REGULAR = fonte("arial.ttf")
NEGRITO = fonte("arialbd.ttf")


class Apresentacao(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(False)
        self.set_margins(MARGEM, MARGEM, MARGEM)
        self.add_font("Body", "", REGULAR)
        self.add_font("Body", "B", NEGRITO)
        self.set_font("Body", "", 10)
        self.avisos: list[str] = []

    # ------------------------------------------------------------------ base
    def fundo_pagina(self, cor=FUNDO) -> None:
        self.set_fill_color(*cor)
        self.rect(0, 0, LARGURA, ALTURA, style="F")

    def rodape(self) -> None:
        self.set_char_spacing(0)
        self.set_font("Body", "", 7.5)
        self.set_text_color(*CINZA)
        self.text(MARGEM, ALTURA - 9, "Associação Caminho Certo  ·  MVP de Gestão Escolar e Combate à Evasão")
        self.text(LARGURA - MARGEM - 18, ALTURA - 9, f"{self.page_no():02d}")

    def cabecalho(self, kicker: str, titulo: str, descricao: str = "") -> float:
        self.set_char_spacing(0.5)
        self.set_font("Body", "B", 8.5)
        self.set_text_color(*CINZA)
        self.text(MARGEM, 20, kicker.upper())
        self.set_char_spacing(0)

        self.set_font("Body", "B", 21)
        self.set_text_color(*TINTA)
        self.text(MARGEM, 31, titulo)

        self.set_draw_color(*BORDA)
        self.set_line_width(0.3)
        self.line(MARGEM, 35.5, LARGURA - MARGEM, 35.5)

        y = 40.0
        if descricao:
            self.set_font("Body", "", 9.5)
            self.set_text_color(*CINZA)
            self.set_xy(MARGEM, y)
            self.multi_cell(CONTEUDO, 4.8, descricao)
            y = self.get_y() + 4
        return y

    def texto(self, x: float, y: float, w: float, txt: str, tam=10, estilo="", cor=TINTA, lh=5.0) -> float:
        self.set_font("Body", estilo, tam)
        self.set_text_color(*cor)
        self.set_xy(x, y)
        self.multi_cell(w, lh, txt, markdown=True)
        return self.get_y()

    def marcador(self, x: float, y: float, cor=VERDE) -> None:
        self.set_fill_color(*cor)
        self.rect(x, y + 1.2, 1.6, 1.6, style="F")

    def lista(self, x: float, y: float, w: float, itens: list[str], tam=9.6, lh=4.9, gap=2.4) -> float:
        for item in itens:
            self.marcador(x, y)
            y = self.texto(x + 4.5, y, w - 4.5, item, tam=tam, lh=lh) + gap
        return y

    def bloco(self, x: float, y: float, w: float, h: float, cor_borda=BORDA, cor_fundo=BRANCO, destaque=None) -> None:
        self.set_fill_color(*cor_fundo)
        self.set_draw_color(*cor_borda)
        self.set_line_width(0.3)
        self.rect(x, y, w, h, style="FD")
        if destaque:
            self.set_fill_color(*destaque)
            self.rect(x, y, 1.8, h, style="F")

    def etiqueta(self, x: float, y: float, txt: str, cor_fundo=VERDE, cor_texto=BRANCO, tam=7.5, largura=None) -> float:
        self.set_font("Body", "B", tam)
        self.set_char_spacing(0.6)
        w = largura or (self.get_string_width(txt) + 7)
        self.set_fill_color(*cor_fundo)
        self.rect(x, y, w, 6.2, style="F")
        self.set_text_color(*cor_texto)
        self.text(x + 3.5, y + 4.2, txt.upper())
        self.set_char_spacing(0)
        return w

    def conferir(self, y: float, minimo: float = FIM - 6) -> None:
        if y > minimo:
            self.avisos.append(f"pagina {self.page_no()}: conteudo termina em {y:.1f}mm")

    # --------------------------------------------------------------- imagens
    def imagem(self, caminho: str, x: float, y: float, max_w: float, max_h: float) -> tuple[float, float]:
        with Image.open(caminho) as img:
            largura_px, altura_px = img.size
        razao = altura_px / largura_px
        w = max_w
        h = w * razao
        if h > max_h:
            h = max_h
            w = h / razao

        self.set_fill_color(*BRANCO)
        self.set_draw_color(*BORDA)
        self.set_line_width(0.3)
        self.rect(x, y, w, h, style="FD")
        self.image(caminho, x, y, w=w, h=h)
        return w, h


def capa(pdf: Apresentacao) -> None:
    pdf.add_page()
    pdf.fundo_pagina(FUNDO)

    # bloco branco principal
    pdf.set_fill_color(*BRANCO)
    pdf.set_draw_color(*BORDA)
    pdf.set_line_width(0.3)
    pdf.rect(MARGEM, 22, CONTEUDO, 150, style="FD")
    pdf.set_fill_color(*VERDE)
    pdf.rect(MARGEM, 22, 2.4, 150, style="F")

    # marca
    pdf.set_fill_color(*VERDE)
    pdf.rect(MARGEM + 14, 36, 16, 16, style="F")
    pdf.set_font("Body", "B", 13)
    pdf.set_text_color(*BRANCO)
    pdf.text(MARGEM + 18.2, 46.6, "CC")

    pdf.set_char_spacing(0.8)
    pdf.set_font("Body", "B", 8.5)
    pdf.set_text_color(*CINZA)
    pdf.text(MARGEM + 35, 42.5, "ASSOCIAÇÃO CAMINHO CERTO  ·  JUNDIAPEBA")
    pdf.set_char_spacing(0)
    pdf.set_font("Body", "", 9)
    pdf.set_text_color(*CINZA)
    pdf.text(MARGEM + 35, 48.5, "Mogi das Cruzes  ·  Educação comunitária")

    # titulo
    pdf.set_font("Body", "B", 34)
    pdf.set_text_color(*TINTA)
    pdf.text(MARGEM + 14, 78, "Gestão Escolar e")
    pdf.text(MARGEM + 14, 90, "Combate à Evasão")

    pdf.set_font("Body", "", 11.5)
    pdf.set_text_color(*CINZA)
    pdf.text(
        MARGEM + 14,
        101,
        "MVP em Python + Streamlit + SQLite  ·  Registro de frequência e alerta precoce de ausências",
    )

    # etiquetas
    x = MARGEM + 14
    for txt, cor in (
        ("ODS 4 · Educação de Qualidade", VERDE),
        ("ODS 10 · Redução das Desigualdades", VERDE_ESCURO),
        ("22 testes automatizados", TINTA),
    ):
        x += pdf.etiqueta(x, 112, txt, cor_fundo=cor, tam=7.5) + 3

    # tres telas em miniatura
    y = 128
    for i, (num, nome) in enumerate(
        (("01", "Menu Inicial"), ("02", "Chamada Diária"), ("03", "Resultados da Chamada"))
    ):
        bx = MARGEM + 14 + i * 88
        pdf.set_fill_color(*FUNDO)
        pdf.set_draw_color(*BORDA)
        pdf.rect(bx, y, 82, 28, style="FD")
        pdf.set_font("Body", "B", 15)
        pdf.set_text_color(*VERDE)
        pdf.text(bx + 6, y + 13, num)
        pdf.set_font("Body", "B", 10)
        pdf.set_text_color(*TINTA)
        pdf.text(bx + 6, y + 20.5, nome)
        pdf.set_font("Body", "", 8)
        pdf.set_text_color(*CINZA)
        subtitulo = (
            "visão geral e atalhos"
            if i == 0
            else "registro por aluno" if i == 1 else "confirmação e alertas"
        )
        pdf.text(bx + 6, y + 25, subtitulo)

    pdf.set_font("Body", "", 8.5)
    pdf.set_text_color(*CINZA)
    pdf.text(MARGEM + 14, 166, "Apresentação do projeto  ·  Novembro de 2026")

    # link do app publicado, alinhado à direita
    pdf.set_font("Body", "B", 8.5)
    pdf.set_text_color(*VERDE_ESCURO)
    rotulo = "caminho-certo.streamlit.app"
    pdf.text(MARGEM + CONTEUDO - 14 - pdf.get_string_width(rotulo), 166, rotulo)

    pdf.rodape()


def problema(pdf: Apresentacao) -> None:
    pdf.add_page()
    pdf.fundo_pagina()
    y = pdf.cabecalho(
        "Contexto",
        "O problema e a solução",
        "A associação atende crianças e adolescentes em situação de vulnerabilidade. A perda de "
        "contato com a frequência é o primeiro sinal de evasão — e hoje o registro é manual.",
    )

    coluna = (CONTEUDO - 10) / 2

    # problema
    pdf.bloco(MARGEM, y, coluna, 96, destaque=VERMELHO)
    pdf.texto(MARGEM + 8, y + 10, coluna - 16, "O problema", tam=9, estilo="B", cor=VERMELHO)
    pdf.texto(MARGEM + 8, y + 16, coluna - 16, "Chamada em papel", tam=13, estilo="B")
    y1 = pdf.lista(
        MARGEM + 8,
        y + 26,
        coluna - 16,
        [
            "A lista de presença fica dispersa e **não gera indicador** nenhum.",
            "Faltas repetidas só são percebidas quando o aluno **já abandonou**.",
            "Sem histórico, a conversa com a família começa tarde e sem evidências.",
            "Relatórios para parceiros e editais são montados à mão.",
        ],
    )
    pdf.conferir(y1, y + 92)

    # solucao
    xs = MARGEM + coluna + 10
    pdf.bloco(xs, y, coluna, 96, destaque=VERDE)
    pdf.texto(xs + 8, y + 10, coluna - 16, "A solução", tam=9, estilo="B", cor=VERDE)
    pdf.texto(xs + 8, y + 16, coluna - 16, "Chamada digital em 3 telas", tam=13, estilo="B")
    y2 = pdf.lista(
        xs + 8,
        y + 26,
        coluna - 16,
        [
            "Registro por aluno em **um toque**: presença, ausência ou atraso.",
            "**Alerta automático** a partir de 3 faltas consecutivas.",
            "Indicadores e histórico prontos para a coordenação.",
            "Exportação em CSV e banco local: **funciona sem internet**.",
        ],
    )
    pdf.conferir(y2, y + 92)

    # fluxo
    yf = y + 104
    pdf.texto(MARGEM, yf, CONTEUDO, "O FLUXO DE USO", tam=8.5, estilo="B", cor=CINZA, lh=4)
    passos = [
        ("1", "Escolher turma e data", "Menu Inicial → Chamada Diária"),
        ("2", "Marcar cada aluno", "Pills de status com contador em tempo real"),
        ("3", "Salvar e decidir", "Resultado com taxa e lista de risco"),
    ]
    largura = (CONTEUDO - 16) / 3
    for i, (num, titulo, desc) in enumerate(passos):
        bx = MARGEM + i * (largura + 8)
        pdf.bloco(bx, yf + 5, largura, 22, cor_fundo=BRANCO)
        pdf.set_font("Body", "B", 13)
        pdf.set_text_color(*VERDE)
        pdf.text(bx + 6, yf + 14, num)
        pdf.set_font("Body", "B", 9.5)
        pdf.set_text_color(*TINTA)
        pdf.text(bx + 15, yf + 12.5, titulo)
        pdf.set_font("Body", "", 8)
        pdf.set_text_color(*CINZA)
        pdf.text(bx + 15, yf + 18.5, desc)

    pdf.rodape()


def arquitetura(pdf: Apresentacao) -> None:
    pdf.add_page()
    pdf.fundo_pagina()
    y = pdf.cabecalho(
        "Técnico",
        "Como o sistema foi construído",
        "Aplicação de página única em Streamlit, com persistência local em SQLite e "
        "regras de negócio separadas da interface — o que permite testar tudo sem abrir a tela.",
    )

    coluna = (CONTEUDO - 10) / 2

    # stack
    pdf.texto(MARGEM, y, coluna, "TECNOLOGIAS", tam=8.5, estilo="B", cor=CINZA, lh=4)
    ys = y + 6
    itens = [
        ("Python 3.14", "linguagem do projeto"),
        ("Streamlit 1.67", "interface web reativa, sem front-end separado"),
        ("SQLite", "banco de arquivo único, zero infraestrutura"),
        ("pandas", "tabelas de indicadores e exportação"),
        ("pytest", "22 testes automatizados"),
        ("GitHub Actions", "CI rodando a suíte a cada push"),
    ]
    for nome, desc in itens:
        pdf.bloco(MARGEM, ys, coluna, 11.5, cor_fundo=BRANCO)
        pdf.set_font("Body", "B", 9.5)
        pdf.set_text_color(*TINTA)
        pdf.text(MARGEM + 5, ys + 5, nome)
        pdf.set_font("Body", "", 8.2)
        pdf.set_text_color(*CINZA)
        pdf.text(MARGEM + 5, ys + 9.2, desc)
        ys += 13

    # modelo de dados
    xs = MARGEM + coluna + 10
    pdf.texto(xs, y, coluna, "MODELO DE DADOS", tam=8.5, estilo="B", cor=CINZA, lh=4)
    yd = y + 6
    pdf.bloco(xs, yd, coluna, 44, cor_fundo=BRANCO)
    pdf.set_font("Body", "B", 9)
    pdf.set_text_color(*TINTA)
    pdf.text(xs + 6, yd + 7, "alunos")
    pdf.set_font("Body", "", 8.6)
    pdf.set_text_color(*CINZA)
    pdf.text(xs + 6, yd + 13, "id · nome · turma · responsável · contato · criado_em")
    pdf.set_font("Body", "B", 9)
    pdf.set_text_color(*TINTA)
    pdf.text(xs + 6, yd + 22, "frequencias")
    pdf.set_font("Body", "", 8.6)
    pdf.set_text_color(*CINZA)
    pdf.text(xs + 6, yd + 28, "id · aluno_id · data · status  (P | A | T)")
    pdf.set_font("Body", "", 8.6)
    pdf.set_text_color(*VERDE_ESCURO)
    pdf.text(xs + 6, yd + 35, "UNIQUE (aluno_id, data)  →  impede chamada duplicada")
    pdf.set_text_color(*CINZA)
    pdf.text(xs + 6, yd + 41, "ON DELETE CASCADE  →  remove aluno apaga o histórico")

    # regras
    yr = yd + 50
    pdf.texto(xs, yr, coluna, "REGRAS DE NEGÓCIO", tam=8.5, estilo="B", cor=CINZA, lh=4)
    yr += 6
    pdf.bloco(xs, yr, coluna, 36, cor_fundo=BRANCO, destaque=VERDE_ESCURO)
    pdf.texto(
        xs + 7,
        yr + 6,
        coluna - 14,
        "**Taxa de comparecimento** = (presenças + atrasos) ÷ total de registros.\n"
        "Atraso conta como comparecimento; ausência, não.",
        tam=8.8,
        lh=4.6,
    )
    pdf.texto(
        xs + 7,
        yr + 20,
        coluna - 14,
        "**Alerta de evasão** = 3 ou mais ausências consecutivas a partir do "
        "registro mais recente do aluno: o gatilho para ligar para a família.",
        tam=8.8,
        lh=4.6,
    )

    # estrutura de pastas
    ye = max(ys, yr + 36) + 6
    pdf.texto(MARGEM, ye, coluna, "ESTRUTURA DO PROJETO", tam=8.5, estilo="B", cor=CINZA, lh=4)
    pdf.bloco(MARGEM, ye + 6, CONTEUDO, 16, cor_fundo=BRANCO)
    pdf.set_font("Body", "", 8.4)
    pdf.set_text_color(*TINTA)
    pdf.text(
        MARGEM + 6,
        ye + 12,
        "src/app.py  (telas e roteamento)   ·   src/database.py  (schema e CRUD)   ·   "
        "src/reports.py  (indicadores e CSV)   ·   src/styles.py  (identidade visual)",
    )
    pdf.set_text_color(*CINZA)
    pdf.text(
        MARGEM + 6,
        ye + 18,
        "tests/  (banco isolado + 22 testes)   ·   scripts/  (captura de telas e dados de exemplo)   ·   "
        ".github/workflows/ci.yml   ·   .streamlit/config.toml",
    )

    pdf.conferir(ye + 22)
    pdf.rodape()


def pagina_tela(
    pdf: Apresentacao,
    kicker: str,
    titulo: str,
    descricao: str,
    imagem: str,
    blocos: list[tuple[str, str]],
    nota: str = "",
) -> None:
    pdf.add_page()
    pdf.fundo_pagina()
    y = pdf.cabecalho(kicker, titulo, descricao)

    largura_img = 168
    _, altura_img = pdf.imagem(imagem, MARGEM, y, largura_img, FIM - y - 8)

    x = MARGEM + largura_img + 10
    w = CONTEUDO - largura_img - 10
    yy = y + 1
    for titulo_bloco, corpo in blocos:
        pdf.texto(x, yy, w, titulo_bloco.upper(), tam=8, estilo="B", cor=VERDE_ESCURO, lh=4)
        yy = pdf.texto(x, yy + 5, w, corpo, tam=9.2, lh=4.9) + 7

    if nota:
        yy += 1
        pdf.bloco(x, yy, w, 24, cor_fundo=BRANCO, destaque=VERDE)
        pdf.texto(x + 6, yy + 6, w - 12, nota, tam=8.4, cor=CINZA, lh=4.4)

    pdf.conferir(max(yy + 24, y + altura_img))
    pdf.rodape()


def telas(pdf: Apresentacao) -> None:
    pagina_tela(
        pdf,
        "Tela 1 de 3",
        "Menu Inicial",
        "Ponto de partida da coordenação: a ação central em destaque e os atalhos organizados em grade.",
        os.path.join(SHOTS, "01-menu-inicial.png"),
        [
            (
                "O que aparece",
                "Card central com borda verde e etiqueta **Funcionalidade central**, seguido de "
                "quatro cartões em grade 2×2: cadastro, histórico, dashboard e relatórios.",
            ),
            (
                "Decisão de design",
                "O botão verde só existe para a chamada — é o caminho que a equipe usa todos os dias. "
                "Os demais cartões usam botão neutro, para não competir visualmente.",
            ),
            (
                "Dados reais na tela",
                "Os subtítulos são consultados no banco a cada carregamento: número de alunos "
                "cadastrados e de turmas ativas (com pluralização correta).",
            ),
        ],
        nota="Tudo em uma coluna, com largura máxima de 1080 px: legível no notebook da "
        "coordenação e no tablet usado na sala.",
    )

    pagina_tela(
        pdf,
        "Tela 2 de 3",
        "Chamada Diária",
        "Seleciona turma e data, lista os alunos e registra o status de cada um em um toque.",
        os.path.join(SHOTS, "02-chamada-diaria.png"),
        [
            (
                "Como funciona",
                "Cada aluno é uma linha com avatar, nome, turma e três pílulas: **Presença**, "
                "**Ausência** e **Atraso**. O chip à direita repete o status por escrito.",
            ),
            (
                "Feedback imediato",
                "Os contadores P / A / T no rodapé são recalculados a cada clique, antes de salvar. "
                "A pessoa confere o total da turma sem precisar contar linha por linha.",
            ),
            (
                "Integridade",
                "Reenviar a chamada do mesmo dia **atualiza** os registros em vez de duplicar "
                "(restrição UNIQUE + UPSERT). O status já salvo volta selecionado.",
            ),
        ],
        nota="A pílula não pode ser desmarcada por acidente (required=True): sempre há "
        "exatamente um status por aluno.",
    )

    pagina_tela(
        pdf,
        "Tela 3 de 3",
        "Resultados da Chamada",
        "Confirma o que foi salvo e transforma a chamada em decisão: quem precisa de contato hoje.",
        os.path.join(SHOTS, "03-resultados.png"),
        [
            (
                "Confirmação",
                "Faixa verde com o total de registros salvos, turma e data por extenso. "
                "É o comprovante de que a chamada foi persistida.",
            ),
            (
                "Alerta de evasão",
                "Bloco vermelho lista os alunos com **3 ou mais faltas consecutivas** e sugere "
                "contato com o responsável. É o coração do combate à evasão.",
            ),
            (
                "Resumo e próximo passo",
                "Taxa de comparecimento, status de cada aluno e dois botões pretos: nova chamada "
                "ou relatórios.",
            ),
        ],
        nota="A cor nunca é o único indicador: cada chip traz o status escrito em maiúsculas, "
        "o que mantém a tela compreensível para quem tem daltonismo.",
    )


def apoio_relatorios(pdf: Apresentacao) -> None:
    pagina_tela(
        pdf,
        "Tela de apoio",
        "Relatórios",
        "Indicadores por aluno, histórico de chamadas e exportação em CSV — fora das 3 telas principais, "
        "mas essencial para a coordenação e para prestar contas a parceiros.",
        os.path.join(SHOTS, "04-relatorios.png"),
        [
            (
                "Três abas",
                "**Dashboard** (alunos, alunos em risco, chamadas do dia), **Histórico** "
                "(últimas 30 datas) e **Dados / Exportar** (tabela completa + CSV).",
            ),
            (
                "Exportação",
                "O CSV sai em UTF-8 com BOM e separador ponto e vírgula, para abrir direto no "
                "Excel em português sem perder acentuação.",
            ),
        ],
        nota="A lista de risco usa a mesma regra da tela de resultados, então o número do "
        "dashboard nunca contradiz a chamada.",
    )


def apoio_cadastro(pdf: Apresentacao) -> None:
    pagina_tela(
        pdf,
        "Tela de apoio",
        "Cadastro de Alunos",
        "Inclusão e remoção de alunos, com turma, responsável e telefone de contato.",
        os.path.join(SHOTS, "05-cadastro-alunos.png"),
        [
            (
                "Formulário",
                "Turma existente ou nova turma criada na hora, nome do aluno, responsável e "
                "telefone. Campos obrigatórios são validados antes de gravar.",
            ),
            (
                "LGPD",
                "A tela avisa que os dados do responsável são sensíveis e o arquivo do banco "
                "está no .gitignore: o repositório nunca carrega dados de alunos.",
            ),
        ],
        nota="Remover um aluno apaga também o histórico de frequência (ON DELETE CASCADE), "
        "sem deixar registros órfãos.",
    )


def qualidade(pdf: Apresentacao) -> None:
    pdf.add_page()
    pdf.fundo_pagina()
    y = pdf.cabecalho(
        "Qualidade",
        "Testes e correções na especificação",
        "A especificação original tinha falhas que quebrariam o projeto em produção. "
        "Em vez de copiar o documento, cada ponto foi corrigido e coberto por teste.",
    )

    pdf.texto(MARGEM, y, 118, "CORREÇÕES APLICADAS", tam=8.5, estilo="B", cor=CINZA, lh=4)
    linhas = [
        ("Testes apagavam o banco real", "Banco temporário por teste via variável CAMINHO_CERTO_DB"),
        ("Relatórios vazios no código", "Indicadores por aluno, histórico e exportação CSV implementados"),
        ("Chamada duplicada no mesmo dia", "UNIQUE (aluno_id, data) + UPSERT: reenvio atualiza"),
        ("CSS de acessibilidade não aplicava", "Seletores atualizados para o Streamlit 1.67 (conferido no DOM)"),
        ("Apenas 2 testes vagos", "22 testes reais: banco, regras de negócio, relatórios e CSV"),
        ("Nenhum controle de versão dos dados", ".gitignore exclui o banco; tema fixo em config.toml"),
    ]
    yy = y + 6
    for problema_txt, solucao in linhas:
        pdf.bloco(MARGEM, yy, 118, 13, cor_fundo=BRANCO)
        pdf.set_fill_color(*VERDE)
        pdf.rect(MARGEM, yy, 1.6, 13, style="F")
        pdf.set_font("Body", "B", 8.6)
        pdf.set_text_color(*TINTA)
        pdf.text(MARGEM + 5, yy + 5.2, problema_txt)
        pdf.set_font("Body", "", 8.2)
        pdf.set_text_color(*CINZA)
        pdf.text(MARGEM + 5, yy + 10.2, solucao)
        yy += 15

    # numeros
    xd = MARGEM + 128
    w = CONTEUDO - 128
    pdf.texto(xd, y, w, "VERIFICAÇÃO", tam=8.5, estilo="B", cor=CINZA, lh=4)

    numeros = [
        ("22", "testes automatizados, 100% passando"),
        ("6", "correções na especificação original"),
        ("0", "erros no console durante o fluxo completo"),
    ]
    yn = y + 6
    for valor, rotulo in numeros:
        pdf.bloco(xd, yn, w, 22, cor_fundo=BRANCO, destaque=VERDE_ESCURO)
        pdf.set_font("Body", "B", 24)
        pdf.set_text_color(*VERDE_ESCURO)
        pdf.text(xd + 7, yn + 13, valor)
        pdf.set_font("Body", "", 8.4)
        pdf.set_text_color(*CINZA)
        pdf.text(xd + 24, yn + 9, rotulo[:52])
        if len(rotulo) > 52:
            pdf.text(xd + 24, yn + 13.5, rotulo[52:])
        yn += 26

    yt = yn + 2
    pdf.texto(xd, yt, w, "COBERTURA DOS TESTES", tam=8.5, estilo="B", cor=CINZA, lh=4)
    yt += 6
    pdf.lista(
        xd,
        yt,
        w,
        [
            "Cadastro, listagem, filtro por turma e remoção em cascata",
            "Status válido, reenvio no mesmo dia e chamada vazia",
            "Taxa de comparecimento e contagem por turma",
            "Detecção de faltas consecutivas (com e sem quebra)",
            "Formato do CSV exportado",
        ],
        tam=8.4,
        lh=4.4,
        gap=2.2,
    )

    pdf.conferir(yy)
    pdf.rodape()


def encerramento(pdf: Apresentacao) -> None:
    pdf.add_page()
    pdf.fundo_pagina()
    y = pdf.cabecalho(
        "Entrega",
        "Como executar e próximos passos",
        "O projeto roda em qualquer máquina com Python instalado, sem servidor e sem internet.",
    )

    # comandos
    pdf.texto(MARGEM, y, 150, "COMANDOS", tam=8.5, estilo="B", cor=CINZA, lh=4)
    yc = y + 6
    pdf.bloco(MARGEM, yc, 150, 46, cor_fundo=(24, 24, 24))
    pdf.set_font("Body", "", 8.6)
    pdf.set_text_color(230, 230, 230)
    comandos = [
        ("py -m venv .venv", "cria o ambiente isolado"),
        (r".\.venv\Scripts\Activate.ps1", "ativa o ambiente (PowerShell)"),
        ("pip install -r requirements.txt", "instala as dependências"),
        ("streamlit run src/app.py", "abre o sistema em localhost:8501"),
    ]
    lin = yc + 9
    for cmd, desc in comandos:
        pdf.set_text_color(160, 220, 160)
        pdf.text(MARGEM + 7, lin, cmd)
        pdf.set_text_color(150, 150, 150)
        pdf.text(MARGEM + 88, lin, desc)
        lin += 8.5
    pdf.set_text_color(150, 150, 150)
    pdf.text(MARGEM + 7, yc + 42, "python -m pytest tests/ -v   →   22 passed")

    pdf.set_font("Body", "B", 8.6)
    pdf.set_text_color(*VERDE_ESCURO)
    pdf.text(MARGEM, yc + 52, "Publicado em caminho-certo.streamlit.app")

    # proximos passos
    xd = MARGEM + 160
    w = CONTEUDO - 160
    pdf.texto(xd, y, w, "PENDÊNCIAS PARA A VERSÃO 2", tam=8.5, estilo="B", cor=CINZA, lh=4)
    yp = y + 6
    pdf.bloco(xd, yp, w, 46, cor_fundo=BRANCO, destaque=AMBAR)
    pdf.lista(
        xd + 7,
        yp + 7,
        w - 14,
        [
            "**Período da turma** (matutino/vespertino) como campo próprio.",
            "**Datas de validação** do documento original precisam ser replanejadas.",
            "Trocar a métrica de testes do documento por **22 testes reais**.",
        ],
        tam=8.5,
        lh=4.5,
        gap=2.2,
    )
    pdf.conferir(yp + 46)

    # fecho
    yf = yp + 58
    pdf.set_font("Body", "B", 15)
    pdf.set_text_color(*TINTA)
    pdf.text(xd, yf + 6, "Um registro simples,")
    pdf.text(xd, yf + 13, "uma criança a menos fora da escola.")

    pdf.set_font("Body", "", 8.6)
    pdf.set_text_color(*CINZA)
    pdf.text(xd, yf + 22, "ODS 4 e ODS 10  ·  Associação Caminho Certo")

    pdf.set_draw_color(*BORDA)
    pdf.line(MARGEM, FIM - 12, LARGURA - MARGEM, FIM - 12)
    pdf.text(MARGEM, FIM - 5, "Documento gerado a partir do sistema em execução, com dados de demonstração.")

    pdf.rodape()


def main() -> int:
    for nome in os.listdir(SHOTS) if os.path.isdir(SHOTS) else []:
        if not nome.endswith(".png"):
            print(f"aviso: arquivo inesperado em screenshots: {nome}")

    pdf = Apresentacao()
    pdf.set_title("Associação Caminho Certo — Gestão Escolar e Combate à Evasão")
    pdf.set_author("Associação Caminho Certo")
    pdf.set_subject("Apresentação do MVP")

    capa(pdf)
    problema(pdf)
    arquitetura(pdf)
    telas(pdf)
    apoio_relatorios(pdf)
    apoio_cadastro(pdf)
    qualidade(pdf)
    encerramento(pdf)

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    pdf.output(SAIDA)

    if pdf.avisos:
        print("ATENÇÃO - possiveis estouros de layout:")
        for a in pdf.avisos:
            print("  " + a)
    else:
        print("layout sem estouros")

    print(f"PDF gerado: {SAIDA} ({os.path.getsize(SAIDA) // 1024} KB, {pdf.page_no()} paginas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
