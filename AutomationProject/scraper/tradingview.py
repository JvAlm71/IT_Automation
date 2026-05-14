import re

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect
from browser.navigation import open_quotes_page
from settings.config import (
	CHART_CLICK_POSITION,TIMEOUT_PREVIOUS_TEXT_MS,
 TIMEOUT_SELECT_RESULT_MS,TIMEOUT_VALID_TEXT_MS,
 TIMEOUT_WAIT_SYMBOL_CHANGE_MS,TIMEOUT_WAIT_VALUE_CHANGE_MS,)


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
	"""Extracts the price and change for a specific asset from the chart iframe."""

	ticker = ticker.strip().upper()

	# Value locators.
	# Keep your original nth() logic. In headless, nodes may exist but be hidden; that's OK.
	price_locator = chart_frame.locator(".valueValue-l31H9iuA").nth(5)
	change_locator = chart_frame.locator(".valueValue-l31H9iuA").nth(7)

	# Read previous values with a short timeout to avoid blocking for 30s
	# when the widget hasn't fully rendered yet.
	try:
		previous_price = (price_locator.text_content(timeout=TIMEOUT_PREVIOUS_TEXT_MS) or "").strip()
	except PlaywrightTimeoutError:
		previous_price = ""

	try:
		previous_change = (change_locator.text_content(timeout=TIMEOUT_PREVIOUS_TEXT_MS) or "").strip()
	except PlaywrightTimeoutError:
		previous_change = ""

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
			make_locator().click(timeout=TIMEOUT_SELECT_RESULT_MS)
			selected = True
			break
		except PlaywrightTimeoutError:
			continue

	if not selected:
		search_box.press("ArrowDown")
		search_box.press("Enter")

	click_on_chart(chart_frame, position=CHART_CLICK_POSITION)

	if previous_symbol_text:
		expect(symbol_button).not_to_have_text(previous_symbol_text, timeout=TIMEOUT_WAIT_SYMBOL_CHANGE_MS)

	try:
		if previous_price:
			expect(price_locator).not_to_have_text(previous_price, timeout=TIMEOUT_WAIT_VALUE_CHANGE_MS)
		if previous_change:
			expect(change_locator).not_to_have_text(previous_change, timeout=TIMEOUT_WAIT_VALUE_CHANGE_MS)
	except AssertionError:
		pass

	# Data extraction.
	# In headless, these nodes may not be "visible" even when they already contain correct data.
	# So we synchronize by waiting for *valid text* instead of visibility.
	expect(price_locator).not_to_have_text("∅", timeout=TIMEOUT_VALID_TEXT_MS)
	expect(change_locator).not_to_have_text("∅", timeout=TIMEOUT_VALID_TEXT_MS)
	expect(price_locator).to_contain_text(re.compile(r"\d"), timeout=TIMEOUT_VALID_TEXT_MS)
	expect(change_locator).to_contain_text("%", timeout=TIMEOUT_VALID_TEXT_MS)

	price = (price_locator.text_content() or "").strip()
	change = (change_locator.text_content() or "").strip()

	asset_name = (symbol_button.text_content() or "").strip()

	return {
		"Ticker": ticker,
		"Ativo": asset_name,
		"Preço": price,
		"Variação": change,
		"Timestamp": pd.Timestamp.now(),
	}




def get_chart_frame(chart_page):
	"""Returns the FrameLocator for the TradingView 'advanced chart' widget."""

	chart_frame = chart_page.frame_locator('iframe[title="advanced chart TradingView widget"]')
	expect(chart_frame.get_by_role("button", name="Intervalo do gráfico")).to_be_visible()
	return chart_frame


def set_interval_1_day(chart_frame):
	"""Sets the chart interval to 1 day."""

	chart_frame.get_by_role("button", name="Intervalo do gráfico").click()
	chart_frame.get_by_role("row", name="1 dia").click()
    #chart_frame.locator("span").filter(has_text="dia").nth(1).click()
    # page.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.get_by_role("button", name="Intervalo do gráfico").click()
    # page.locator("iframe[title=\"advanced chart TradingView widget\"]").content_frame.locator("span").filter(has_text="dia").nth(1).click()
