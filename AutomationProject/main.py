from playwright.sync_api import sync_playwright


def run() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()

        page1 = context.new_page()
        page1.goto("https://borainvestir.b3.com.br/")
        with page1.expect_popup() as page1_info:
            page1.get_by_role("link", name="Acompanhe as cotações").click()
        
        page2 = page1_info.value
        page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_role("button", name="Intervalo do gráfico").click()
        page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_role("row", name="1 dia").click()
        page2.locator("iframe[title=\"hotlists TradingView widget\"]").content_frame.get_by_text("PETR4 D Mercado aberto").click()
        page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_role("button", name="Pesquisa de símbolo").click()
        page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_role("searchbox", name="Símbolo, ISIN ou CUSIP").dblclick()
        page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_role("searchbox", name="Símbolo, ISIN ou CUSIP").fill("Petr4")
        page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_text("Petroleo Brasileiro SA Pfd").first.click()
        page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_label("Gráfico para BMFBOVESPA_DLY:").click(position={"x":732,"y":59})
        
        # === EXTRAÇÃO DE DADOS ===
        chart_iframe = page2.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame
        
        
        # DEBUG: Ver quantos elementos existem e seus valores
        # elementos = chart_iframe.locator(".valueValue-l31H9iuA").all()
        # print(f"\n🔍 Total de elementos encontrados: {len(elementos)}")
        # for i, elem in enumerate(elementos):
        #     print(f"   [{i}] {elem.text_content()}")

        nome_ativo = chart_iframe.get_by_role("button", name="Mudar símbolo").text_content()
        print(f"\nAtivo: {nome_ativo}")

        # Extrair o primeiro (preço atual)
        preco = chart_iframe.locator(".valueValue-l31H9iuA").nth(5).text_content()
        print(f"\nPreço Atual: {preco}")
        
        # # Segundo elemento com a mesma classe é a variação
        variacao = chart_iframe.locator(".valueValue-l31H9iuA").nth(7).text_content()
        print(f"Variação: {variacao}")
        
        # Manter navegador aberto
        # input("\n⏸️  Pressione ENTER para fechar o navegador...")
        
        context.close()
        browser.close()
        
run()