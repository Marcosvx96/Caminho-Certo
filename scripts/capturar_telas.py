"""Captura as telas do app em PNG (Playwright + Edge já instalado).

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\capturar_telas.py
"""

from __future__ import annotations

import os
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("CAMINHO_CERTO_URL", "http://localhost:8501")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "docs", "screenshots")
FUNDO = (245, 245, 245)


def recortar_vazio(caminho: str) -> None:
    """Remove a faixa de fundo lisa que sobra no rodapé do print."""
    with Image.open(caminho) as img:
        img = img.convert("RGB")
        largura, altura = img.size
        pixels = img.load()

        def linha_lisa(y: int) -> bool:
            for x in range(0, largura, 4):
                if pixels[x, y] != FUNDO:
                    return False
            return True

        fim = altura
        while fim > 10 and linha_lisa(fim - 1):
            fim -= 1
        margem = 60  # respiro visual
        fim = min(altura, fim + margem)
        img.crop((0, 0, largura, fim)).save(caminho, optimize=True)


def main() -> int:
    os.makedirs(SAIDA, exist_ok=True)

    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge", headless=True)
        pagina = navegador.new_page(
            viewport={"width": 1180, "height": 1600},
            device_scale_factor=2,
        )
        pagina.goto(BASE_URL, wait_until="networkidle")
        pagina.get_by_text("INICIAR CHAMADA").first.wait_for(timeout=60000)

        def foto(nome: str) -> None:
            caminho = os.path.join(SAIDA, nome)
            pagina.screenshot(path=caminho)
            recortar_vazio(caminho)
            print(f"capturado: {nome}")

        foto("01-menu-inicial.png")

        pagina.get_by_text("INICIAR CHAMADA").first.click()
        pagina.get_by_text("FINALIZAR E SALVAR CHAMADA").first.wait_for(timeout=60000)

        for chave, rotulo in (
            ("row-2", "AUSÊNCIA"),   # Maria Santos
            ("row-3", "AUSÊNCIA"),   # Pedro Oliveira
            ("row-4", "ATRASO"),     # Luana Gomes
        ):
            linha = pagina.locator(f".st-key-{chave}")
            linha.locator("button", has_text=rotulo).first.click()
            pagina.wait_for_timeout(700)

        pagina.get_by_text("FINALIZAR E SALVAR CHAMADA").first.wait_for(timeout=30000)
        foto("02-chamada-diaria.png")

        pagina.get_by_text("FINALIZAR E SALVAR CHAMADA").first.click()
        pagina.get_by_text("RESULTADOS DA CHAMADA").first.wait_for(timeout=60000)
        pagina.wait_for_timeout(900)
        foto("03-resultados.png")

        pagina.get_by_text("VISUALIZAR RELAT").first.click()
        pagina.get_by_text("Indicadores de frequência").first.wait_for(timeout=60000)
        pagina.wait_for_timeout(1200)
        foto("04-relatorios.png")

        pagina.goto(BASE_URL, wait_until="networkidle")
        pagina.get_by_text("CADASTRO DE ALUNOS").first.wait_for(timeout=60000)
        pagina.locator(".st-key-card-alunos").locator("button", has_text="ABRIR").first.click()
        pagina.get_by_text("CADASTRAR ALUNO").first.wait_for(timeout=60000)
        pagina.wait_for_timeout(1200)
        foto("05-cadastro-alunos.png")

        navegador.close()

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
