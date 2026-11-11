# Associação Caminho Certo — Gestão Escolar e Combate à Evasão

MVP em **Python + Streamlit + SQLite** para registro de frequência e identificação
preventiva de alunos em risco de evasão, na Associação Caminho Certo (Jundiapeba).

- **ODS 4** — Educação de Qualidade
- **ODS 10** — Redução das Desigualdades

## Telas

| Tela | Arquivo/função | O que faz |
|---|---|---|
| 1. Menu Inicial | `render_home` | Dashboard com a ação central (Chamada Diária) e atalhos |
| 2. Chamada Diária | `render_chamada` | Seleciona turma e data, marca PRESENÇA / AUSÊNCIA / ATRASO |
| 3. Resultados | `render_resultado` | Confirma o salvamento, mostra taxa e alerta faltas consecutivas |
| Apoio | `render_alunos` | Cadastro e remoção de alunos |
| Apoio | `render_relatorios` | Indicadores, histórico e exportação CSV |

## Como rodar

```powershell
# na raiz do projeto
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

streamlit run src/app.py
```

O app abre em `http://localhost:8501`. O banco é criado automaticamente em
`data/db.sqlite3` na primeira execução.

Para começar com dados de demonstração (5 alunos + 3 dias de histórico):

```powershell
.\.venv\Scripts\python.exe scripts\seed_demo.py
```

Para zerar tudo, basta apagar `data/db.sqlite3`.

## Apresentação

O PDF de apresentação do projeto está em
[`docs/Apresentacao_Caminho_Certo.pdf`](docs/Apresentacao_Caminho_Certo.pdf) — 10 páginas
em A4 paisagem: capa, problema/solução, arquitetura, uma página por tela (com captura
real do sistema), telas de apoio, testes/correções e como executar.

Para regerar (usa o Edge já instalado, sem baixar navegador):

```powershell
pip install playwright fpdf2
.\\.venv\\Scripts\\python.exe scripts\\capturar_telas.py   # app precisa estar rodando
.\\.venv\\Scripts\\python.exe scripts\\gerar_pdf.py
```

As capturas ficam em `docs/screenshots/`.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Os testes usam **banco temporário isolado** (variável `CAMINHO_CERTO_DB`) — nunca
tocam nos dados reais.

## Modelo de dados

```
alunos(id, nome, turma, responsavel, contato, criado_em)
frequencias(id, aluno_id, data, status)   -- status: P | A | T
  UNIQUE(aluno_id, data)                  -- impede duplicidade no mesmo dia
  FOREIGN KEY(aluno_id) → alunos(id) ON DELETE CASCADE
```

Salvar a chamada duas vezes no mesmo dia **atualiza** os registros (UPSERT), em vez
de duplicá-los.

## Regras de negócio

- **Taxa de comparecimento** = `(presenças + atrasos) / total de registros`.
  Atraso conta como comparecimento; ausência não.
- **Alerta de evasão** = 3 ou mais ausências **consecutivas** a partir do registro
  mais recente do aluno.

## Acessibilidade

- Tema de alto contraste definido em `.streamlit/config.toml`
- Verde como cor primária, chips semânticos (verde/vermelho/amarelo) com texto —
  a cor nunca é o único indicador de status
- Rótulos em maiúsculas e pesos fortes para leitura rápida

## LGPD

O sistema armazena nome de crianças/adolescentes e telefone de responsáveis.
Recomendações:

- Acesso restrito à equipe da associação
- `data/*.sqlite3` está no `.gitignore` — **nunca** versione o banco
- Defina prazo de retenção e responsável pelo tratamento dos dados
- Colete consentimento dos responsáveis no cadastro

## Estrutura

```
Caminho Certo/
├── .github/workflows/ci.yml
├── .streamlit/config.toml
├── data/                    # banco local (ignorado no Git)
├── src/
│   ├── app.py               # interface e roteamento
│   ├── database.py          # CRUD e schema SQLite
│   ├── reports.py           # indicadores e CSV
│   └── styles.py            # identidade visual
├── tests/
│   ├── conftest.py          # banco isolado
│   └── test_app.py
├── requirements.txt
└── README.md
```
