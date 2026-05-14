from __future__ import annotations

from pathlib import Path

# Browser execution
HEADLESS: bool = True

WINDOW_SIZE: tuple[int, int] = (1920, 1080)
VIEWPORT: dict[str, int] = {"width": 1920, "height": 1080}
BROWSER_LAUNCH_ARGS: list[str] = [f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}"]

# Scraping
TICKERS: list[str] = ["PETR4", "VALE3", "ITUB4", "GGBR3"]
CHART_CLICK_POSITION: dict[str, float] = {"x": 732, "y": 59}

# Timeouts (ms) — keep aligned with the values that worked in your script.
TIMEOUT_PREVIOUS_TEXT_MS: int = 1000
TIMEOUT_SELECT_RESULT_MS: int = 500
TIMEOUT_WAIT_SYMBOL_CHANGE_MS: int = 500
TIMEOUT_WAIT_VALUE_CHANGE_MS: int = 500
TIMEOUT_VALID_TEXT_MS: int = 15000

# Persistence
SQLITE_DB_PATH: Path = Path("data") / "quotes.sqlite3"
