import time

import pandas as pd
from playwright.sync_api import sync_playwright
from browser.navigation import open_quotes_page
from scraper.tradingview import extract_asset_data, set_interval_1_day, get_chart_frame
from settings.config import BROWSER_LAUNCH_ARGS, HEADLESS, SQLITE_DB_PATH, TICKERS, VIEWPORT
from storage.persistence import init_schema, insert_quote, open_sqlite


def run() -> None:
    """Orchestrates: open site -> scrape tickers -> print + persist to SQLite."""

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=HEADLESS, args=BROWSER_LAUNCH_ARGS)
        context = browser.new_context(viewport=VIEWPORT)

        conn = open_sqlite(SQLITE_DB_PATH)
        init_schema(conn)

        try:
            chart_page = open_quotes_page(context)
            chart_frame = get_chart_frame(chart_page)
            set_interval_1_day(chart_frame)

            results = []
            for ticker in TICKERS:
                start = time.perf_counter()
                data = extract_asset_data(chart_frame, ticker)
                elapsed = time.perf_counter() - start

                insert_quote(conn, data, scrape_time_s=elapsed)
                conn.commit()

                results.append(data)
                print(
                    f"{data['Ticker']}: Preço={data['Preço']} | Variação={data['Variação']}"
                    f" | time={elapsed:.2f}s"
                )

            df = pd.DataFrame(results)
            print("\nResumo:")
            print(df)

        finally:
            conn.close()
            context.close()
            browser.close()


if __name__ == "__main__":
    run()