from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Mapping


def open_sqlite(db_path: Path) -> sqlite3.Connection:
	"""Opens (and creates if needed) a SQLite database connection."""

	db_path.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(db_path)

	# Good defaults for a small local time-series DB.
	conn.execute("PRAGMA journal_mode=WAL;")
	conn.execute("PRAGMA synchronous=NORMAL;")
	return conn


def init_schema(conn: sqlite3.Connection) -> None:
	"""Creates tables/indexes if they don't exist."""

	conn.execute(
		"""
		CREATE TABLE IF NOT EXISTS quotes (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			collected_at TEXT NOT NULL,
			ticker TEXT NOT NULL,
			asset_name TEXT,
			price_text TEXT,
			change_text TEXT,
			scrape_time_s REAL
		);
		"""
	)

	conn.execute(
		"""
		CREATE INDEX IF NOT EXISTS idx_quotes_ticker_collected_at
			ON quotes(ticker, collected_at);
		"""
	)
	conn.commit()


def _to_iso_string(value: Any) -> str:
	if value is None:
		return ""
	isoformat = getattr(value, "isoformat", None)
	if callable(isoformat):
		return isoformat()
	return str(value)


def insert_quote(
	conn: sqlite3.Connection,
	quote: Mapping[str, Any],
	scrape_time_s: float | None = None,
) -> None:
	"""Inserts one scraped quote row. Call conn.commit() outside for batching."""

	collected_at = _to_iso_string(quote.get("Timestamp"))
	ticker = str(quote.get("Ticker", ""))
	asset_name = quote.get("Ativo")
	price_text = quote.get("Preço")
	change_text = quote.get("Variação")

	conn.execute(
		"""
		INSERT INTO quotes (collected_at, ticker, asset_name, price_text, change_text, scrape_time_s)
		VALUES (?, ?, ?, ?, ?, ?);
		""",
		(collected_at, ticker, asset_name, price_text, change_text, scrape_time_s),
	)
