import re

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect, sync_playwright


def clicar_no_grafico(chart_iframe, position: dict | None = None):
    """Clica no canvas do gráfico (útil pra aplicar seleção e atualizar valores)."""

    chart_area = chart_iframe.get_by_label(re.compile(r"^Gráfico para", re.IGNORECASE))
    expect(chart_area).to_be_visible()

    if not position:
        chart_area.click()
        return

    # A posição é relativa ao elemento; clamp evita erro se a viewport mudar.
    box = chart_area.bounding_box()
    if not box:
        chart_area.click()
        return

    x = float(position.get("x", 1))
    y = float(position.get("y", 1))
    x = max(1.0, min(x, box["width"] - 1.0))
    y = max(1.0, min(y, box["height"] - 1.0))
    chart_area.click(position={"x": x, "y": y})

def extrair_dados_ativo(chart_iframe, ticker: str):
    """
    Função para extrair o preço e variação de um ativo específico a 
    partir do iframe do gráfico.
    """

    ticker = ticker.strip().upper()

    # Locators dos valores .
    preco_locator = chart_iframe.locator(".valueValue-l31H9iuA").nth(5)
    variacao_locator = chart_iframe.locator(".valueValue-l31H9iuA").nth(7)

    preco_before = (preco_locator.text_content() or "").strip()
    variacao_before = (variacao_locator.text_content() or "").strip()

    # Elemento que muda quando o símbolo do gráfico muda.
    symbol_button = chart_iframe.get_by_role("button", name="Mudar símbolo")
    expect(symbol_button).to_be_visible()
    symbol_before = (symbol_button.text_content() or "").strip()

    # Abrir a pesquisa de símbolo, digitar e selecionar um resultado.
    chart_iframe.get_by_role("button", name="Pesquisa de símbolo").click()
    search_box = chart_iframe.get_by_role("searchbox", name="Símbolo, ISIN ou CUSIP")
    expect(search_box).to_be_visible()
    search_box.dblclick()
    search_box.fill(ticker)

    ticker_pattern = re.compile(re.escape(ticker), re.IGNORECASE)
    selected = False
    selectors = [
        lambda: chart_iframe.get_by_role("row", name=ticker_pattern).first,
        lambda: chart_iframe.get_by_role("option", name=ticker_pattern).first,
        lambda: chart_iframe.get_by_text(ticker_pattern).first,
    ]
    for make_locator in selectors:
        try:
            make_locator().click(timeout=2500)
            selected = True
            break
        except PlaywrightTimeoutError:
            continue

    if not selected:
        search_box.press("ArrowDown")
        search_box.press("Enter")

    clicar_no_grafico(chart_iframe, position={"x": 732, "y": 59})

 
    if symbol_before:
        expect(symbol_button).not_to_have_text(symbol_before, timeout=15000)

    try:
        if preco_before:
            expect(preco_locator).not_to_have_text(preco_before, timeout=15000)
        if variacao_before:
            expect(variacao_locator).not_to_have_text(variacao_before, timeout=15000)
    except AssertionError:
        pass

    # Parte de extração de dados.
    expect(preco_locator).to_be_visible()
    expect(variacao_locator).to_be_visible()

    preco = (preco_locator.text_content() or "").strip()
    variacao = (variacao_locator.text_content() or "").strip()

    nome_ativo = (symbol_button.text_content() or "").strip()
    
    return {
        "Ticker": ticker,
        "Ativo": nome_ativo,
        "Preço": preco,
        "Variação": variacao,
        "Timestamp": pd.Timestamp.now()
    }


def abrir_pagina_cotacoes(context):
    page1 = context.new_page()
    page1.goto("https://borainvestir.b3.com.br/", wait_until="domcontentloaded")

    with page1.expect_popup() as page2_info:
        page1.get_by_role("link", name="Acompanhe as cotações").click()

    page2 = page2_info.value
    page2.wait_for_load_state("domcontentloaded")
    return page2


def obter_frame_grafico(page2):
    chart_iframe = page2.frame_locator('iframe[title="advanced chart TradingView widget"]')
    expect(chart_iframe.get_by_role("button", name="Intervalo do gráfico")).to_be_visible()
    return chart_iframe


def setar_intervalo_1_dia(chart_iframe):
    chart_iframe.get_by_role("button", name="Intervalo do gráfico").click()
    chart_iframe.get_by_role("row", name="1 dia").click()


def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()

        page2 = abrir_pagina_cotacoes(context)
        chart_iframe = obter_frame_grafico(page2)
        setar_intervalo_1_dia(chart_iframe)

        tickers = [
            "PETR4",
            "VALE3",
            "ITUB4",
            "GGBR3",
        ]

        resultados = []
        for ticker in tickers:
            dados = extrair_dados_ativo(chart_iframe, ticker)
            resultados.append(dados)
            print(f"{dados['Ticker']}: Preço={dados['Preço']} | Variação={dados['Variação']}")

        df = pd.DataFrame(resultados)
        print("\nResumo:")
        print(df)

        context.close()
        browser.close()


if __name__ == "__main__":
    run()