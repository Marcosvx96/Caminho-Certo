"""Identidade visual do sistema Caminho Certo.

Reproduz o design das telas aprovadas na validação:
fundo cinza claro, cards brancos arredondados, verde como cor primária
e chips semânticos (verde / vermelho / amarelo) para frequência.
"""

from __future__ import annotations

import streamlit as st

CSS = """
<style>
:root{
  --cc-fundo:#F5F5F5;
  --cc-superficie:#FFFFFF;
  --cc-texto:#111111;
  --cc-texto-sec:#6B7280;
  --cc-borda:#E6E6E6;
  --cc-verde:#4CAF50;
  --cc-verde-escuro:#7CB342;
  --cc-vermelho:#F44336;
  --cc-amarelo:#FFC107;
  --cc-preto:#111111;
}

/* ---------- Estrutura ---------- */
.stApp{background:var(--cc-fundo);}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"]{display:none;}
.block-container{max-width:1080px;padding-top:1.4rem;padding-bottom:3rem;}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"]{display:none;}

/* ---------- Cabeçalho ---------- */
.cc-header{display:flex;align-items:center;gap:.75rem;padding:.15rem 0 1.1rem 0;
  border-bottom:1px solid var(--cc-borda);margin-bottom:1.4rem;}
.cc-logo{width:46px;height:46px;border-radius:12px;background:var(--cc-verde);
  display:flex;align-items:center;justify-content:center;font-size:24px;line-height:1;}
.cc-titulo{font-size:1.15rem;font-weight:800;letter-spacing:.06em;color:var(--cc-texto);line-height:1.15;}
.cc-sub{font-size:.76rem;color:var(--cc-texto-sec);letter-spacing:.02em;}

/* ---------- Tipografia de seção ---------- */
.cc-secao{font-size:.78rem;font-weight:800;letter-spacing:.14em;color:var(--cc-texto-sec);
  text-transform:uppercase;margin:.2rem 0 .9rem 0;}
.cc-titulo-pagina{font-size:1.75rem;font-weight:800;letter-spacing:.02em;
  text-transform:uppercase;color:var(--cc-texto);margin:0 0 .3rem 0;}
.cc-descricao{font-size:.9rem;color:var(--cc-texto-sec);margin:0 0 1.3rem 0;}

/* ---------- Cards ----------
   Streamlit >=1.5x aplica o border no próprio stVerticalBlock com classe st-key-*.
   Mantemos também o seletor antigo (VerticalBlockBorderWrapper) por compatibilidade. */
div[data-testid="stVerticalBlock"][class*="st-key-card-"],
div[data-testid="stVerticalBlock"][class*="st-key-row-"],
div[data-testid="stVerticalBlock"][class*="st-key-card-central"],
[data-testid="stVerticalBlockBorderWrapper"]{
  background:var(--cc-superficie);
  border:1px solid var(--cc-borda) !important;
  border-radius:16px;
  box-shadow:0 1px 3px rgba(16,24,40,.05);
  padding:.35rem .55rem;
}
.cc-icone{font-size:1.65rem;line-height:1;margin-bottom:.45rem;}
.cc-card-titulo{font-size:.82rem;font-weight:800;letter-spacing:.08em;
  text-transform:uppercase;color:var(--cc-texto);line-height:1.25;}
.cc-card-desc{font-size:.75rem;color:var(--cc-texto-sec);margin-top:.15rem;}

/* ---------- Card central (funcionalidade principal) ---------- */
div[data-testid="stVerticalBlock"].st-key-card-central,
.st-key-card-central [data-testid="stVerticalBlockBorderWrapper"]{
  border:2px solid var(--cc-verde-escuro) !important;
  border-radius:18px;
}
.cc-pill-verde{display:inline-block;background:var(--cc-verde-escuro);color:#fff;
  font-size:.62rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
  padding:.25rem .7rem;border-radius:999px;margin-bottom:.7rem;}
.cc-hero-icone{font-size:2.1rem;line-height:1;margin-bottom:.3rem;}
.cc-hero-titulo{font-size:1.5rem;font-weight:800;letter-spacing:.05em;
  text-transform:uppercase;color:var(--cc-texto);}
.cc-hero-desc{font-size:.82rem;color:var(--cc-texto-sec);margin-top:.2rem;}

/* ---------- Botões ---------- */
div[data-testid="stButton"] > button{
  border-radius:11px;font-weight:800;letter-spacing:.06em;font-size:.74rem;
  text-transform:uppercase;padding:.55rem .9rem;transition:all .15s ease;
}
[class*="st-key-card-"] div[data-testid="stButton"] > button{
  background:var(--cc-superficie);color:var(--cc-texto);
  border:1px solid var(--cc-borda);
}
[class*="st-key-card-"] div[data-testid="stButton"] > button:hover{
  border-color:var(--cc-verde);color:var(--cc-verde-escuro);
}
.st-key-btn-verde div[data-testid="stButton"] > button{
  background:var(--cc-verde) !important;color:#fff !important;border:none !important;
  font-size:.82rem;padding:.7rem 1rem;
}
.st-key-btn-verde div[data-testid="stButton"] > button:hover{
  background:#43A047 !important;
}
.st-key-acoes-finais div[data-testid="stButton"] > button{
  background:var(--cc-preto) !important;color:#fff !important;border:1px solid var(--cc-preto) !important;
  font-size:.8rem;padding:.7rem 1rem;
}
.st-key-acoes-finais div[data-testid="stButton"] > button:hover{
  background:#000 !important;
}

/* ---------- Linha de aluno ---------- */
.cc-aluno{display:flex;align-items:center;gap:.65rem;}
.cc-avatar{width:38px;height:38px;border-radius:50%;background:#EDF7ED;
  color:var(--cc-verde-escuro);display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:.8rem;flex:0 0 38px;}
.cc-aluno-nome{font-size:.86rem;font-weight:700;color:var(--cc-texto);line-height:1.2;}
.cc-aluno-turma{font-size:.72rem;color:var(--cc-texto-sec);}

/* ---------- Chips de status ---------- */
.cc-chip{display:inline-block;font-size:.62rem;font-weight:800;letter-spacing:.1em;
  text-transform:uppercase;padding:.28rem .6rem;border-radius:999px;white-space:nowrap;}
.cc-chip-p{background:#E8F5E9;color:#2E7D32;border:1px solid #A5D6A7;}
.cc-chip-a{background:#FFEBEE;color:#C62828;border:1px solid #EF9A9A;}
.cc-chip-t{background:#FFF8E1;color:#8D6E00;border:1px solid #FFE082;}

/* ---------- Pills de seleção ---------- */
div[data-testid="stPills"] button,
div[data-testid="stButtonGroup"] button{
  border-radius:999px;font-size:.62rem;font-weight:800;letter-spacing:.08em;
  text-transform:uppercase;padding:.25rem .55rem;
}

/* ---------- Contadores do rodapé ---------- */
.cc-contadores{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;
  font-size:.72rem;color:var(--cc-texto-sec);margin-top:.6rem;}
.cc-cont{background:var(--cc-superficie);border:1px solid var(--cc-borda);
  border-radius:999px;padding:.22rem .7rem;font-weight:700;}
.cc-cont-p{color:#2E7D32;}
.cc-cont-a{color:#C62828;}
.cc-cont-t{color:#8D6E00;}

/* ---------- Cards informativos ---------- */
.cc-card-sucesso{border:1.5px solid var(--cc-verde);border-radius:16px;background:#fff;
  padding:1.1rem 1.2rem;}
.cc-card-alerta{border:1.5px solid var(--cc-vermelho);border-radius:16px;background:#fff;
  padding:1.1rem 1.2rem;}
.cc-card-neutro{border:1px solid var(--cc-borda);border-radius:16px;background:#fff;
  padding:1.1rem 1.2rem;}
.cc-card-titulo-grande{font-size:1.05rem;font-weight:800;letter-spacing:.05em;
  text-transform:uppercase;color:var(--cc-texto);margin:0;}
.cc-card-sub{font-size:.8rem;color:var(--cc-texto-sec);margin:.25rem 0 0 0;}
.cc-linha-status{display:flex;justify-content:space-between;align-items:center;
  padding:.42rem 0;border-bottom:1px dashed #EFEFEF;font-size:.84rem;}
.cc-linha-status:last-child{border-bottom:none;}
.cc-taxa{font-size:1.9rem;font-weight:800;color:var(--cc-verde-escuro);line-height:1;}
.cc-taxa-rotulo{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--cc-texto-sec);}

/* ---------- Tabelas e inputs ---------- */
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;}
div[data-baseweb="select"] > div, .stDateInput div[data-baseweb="input"]{
  border-radius:10px;
}
label, .stSelectbox label, .stDateInput label, .stTextInput label{
  font-size:.68rem !important;font-weight:800 !important;letter-spacing:.1em;
  text-transform:uppercase;color:var(--cc-texto-sec) !important;
}
</style>
"""


def apply_custom_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
