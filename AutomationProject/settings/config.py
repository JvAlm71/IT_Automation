from __future__ import annotations

from pathlib import Path

# Browser execution
# Set to False to see the browser in action. Useful for debugging, but may be less stable.
HEADLESS: bool = True  

# WINDOW_SIZE: tuple[int, int] = (1920, 1080)
VIEWPORT: dict[str, int] = {"width": 1920, "height": 1080}
# Window size to launch in the browser.
BROWSER_LAUNCH_ARGS: list[str] = ["--window-size=1920,1080" "--start-maximized"]

# Scraping
TICKERS: list[str] = ["PETR4", "VALE3", "ITUB4", "GGBR3"]
CHART_CLICK_POSITION: dict[str, float] = {"x": 732, "y": 59}

TIMEOUT_PREVIOUS_TEXT_MS: int = 500
TIMEOUT_SELECT_RESULT_MS: int = 500
TIMEOUT_WAIT_SYMBOL_CHANGE_MS: int = 500
TIMEOUT_WAIT_VALUE_CHANGE_MS: int = 500
TIMEOUT_VALID_TEXT_MS: int = 10000

# Persistence
SQLITE_DB_PATH: Path = Path("data") / "quotes.sqlite3"
