import time

from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError


def open_quotes_page(context):
	"""Opens the B3 quotes page and returns the chart page (opened in a popup)."""

	landing_page = context.new_page()
	landing_page.goto("https://borainvestir.b3.com.br/", wait_until="domcontentloaded")

	with landing_page.expect_popup() as chart_page_info:
		landing_page.get_by_role("link", name="Acompanhe as cotações").click()

	chart_page = chart_page_info.value
	chart_page.wait_for_load_state("domcontentloaded")
	return chart_page
