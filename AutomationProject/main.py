import re
import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect, sync_playwright

# I STILL NEED TO MAKE THIS MORE EFFICIENT: it's too slow to fetch data for each asset,
# because it needs to change the chart symbol and wait for elements to update.


def click_on_chart(chart_frame, position: dict | None = None):
    """Clicks on the chart canvas to get the most up-to-date value."""

    chart_area = chart_frame.get_by_label(re.compile(r"^Gráfico para", re.IGNORECASE))
    expect(chart_area).to_be_visible()

    if not position:
        chart_area.click()
        return

    # Position is relative to the element; clamp avoids errors if the viewport changes.
    box = chart_area.bounding_box()
    if not box:
        chart_area.click()
        return

    x = float(position.get("x", 1))
    y = float(position.get("y", 1))
    x = max(1.0, min(x, box["width"] - 1.0))
    y = max(1.0, min(y, box["height"] - 1.0))
    chart_area.click(position={"x": x, "y": y})


def extract_asset_data(chart_frame, ticker: str):
    """
    Extracts the price and change for a specific asset from the chart iframe.
    """

    ticker = ticker.strip().upper()

    # Value locators.
    price_locator = chart_frame.locator(".valueValue-l31H9iuA").nth(5)
    change_locator = chart_frame.locator(".valueValue-l31H9iuA").nth(7)

    previous_price = (price_locator.text_content() or "").strip()
    previous_change = (change_locator.text_content() or "").strip()

    # Element that changes when the chart symbol changes.
    symbol_button = chart_frame.get_by_role("button", name="Mudar símbolo")
    expect(symbol_button).to_be_visible()
    previous_symbol_text = (symbol_button.text_content() or "").strip()

    # Open symbol search, type, and select a result.
    chart_frame.get_by_role("button", name="Pesquisa de símbolo").click()
    search_box = chart_frame.get_by_role("searchbox", name="Símbolo, ISIN ou CUSIP")
    expect(search_box).to_be_visible()
    search_box.dblclick()
    search_box.fill(ticker)

    ticker_pattern = re.compile(re.escape(ticker), re.IGNORECASE)
    selected = False
    selectors = [
        lambda: chart_frame.get_by_role("row", name=ticker_pattern).first,
        lambda: chart_frame.get_by_role("option", name=ticker_pattern).first,
        lambda: chart_frame.get_by_text(ticker_pattern).first,
    ]
    for make_locator in selectors:
        try:
            make_locator().click(timeout=500)
            selected = True
            break
        except PlaywrightTimeoutError:
            continue

    if not selected:
        search_box.press("ArrowDown")
        search_box.press("Enter")

    click_on_chart(chart_frame, position={"x": 732, "y": 59})

    if previous_symbol_text:
        expect(symbol_button).not_to_have_text(previous_symbol_text, timeout=500)

    try:
        if previous_price:
            expect(price_locator).not_to_have_text(previous_price, timeout=500)
        if previous_change:
            expect(change_locator).not_to_have_text(previous_change, timeout=500)
    except AssertionError:
        pass

    # Data extraction.
    expect(price_locator).to_be_visible()
    expect(change_locator).to_be_visible()

    price = (price_locator.text_content() or "").strip()
    change = (change_locator.text_content() or "").strip()

    asset_name = (symbol_button.text_content() or "").strip()

    return {
        "Ticker": ticker,
        "Ativo": asset_name,
        "Preço": price,
        "Variação": change,
        "Timestamp": pd.Timestamp.now()
    }


def open_quotes_page(context):
    """
    Opens the B3 quotes page and returns the chart page, which opens in a popup.
    """
    landing_page = context.new_page()
    landing_page.goto("https://borainvestir.b3.com.br/", wait_until="domcontentloaded")

    with landing_page.expect_popup() as chart_page_info:
        landing_page.get_by_role("link", name="Acompanhe as cotações").click()

    chart_page = chart_page_info.value
    chart_page.wait_for_load_state("domcontentloaded")
    return chart_page


def get_chart_frame(chart_page):
    chart_frame = chart_page.frame_locator('iframe[title="advanced chart TradingView widget"]')
    expect(chart_frame.get_by_role("button", name="Intervalo do gráfico")).to_be_visible()
    return chart_frame


def set_interval_1_day(chart_frame):
    chart_frame.get_by_role("button", name="Intervalo do gráfico").click()
    chart_frame.get_by_role("row", name="1 dia").click()


def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()

        chart_page = open_quotes_page(context)
        chart_frame = get_chart_frame(chart_page)
        set_interval_1_day(chart_frame)

        tickers = [
            "PETR4",
            "VALE3",
            "ITUB4",
            "GGBR3",
        ]

        results = []
        for ticker in tickers:
            data = extract_asset_data(chart_frame, ticker)
            results.append(data)
            print(f"{data['Ticker']}: Preço={data['Preço']} | Variação={data['Variação']}")

        df = pd.DataFrame(results)
        print("\nResumo:")
        print(df)

        context.close()
        browser.close()


if __name__ == "__main__":
    run()