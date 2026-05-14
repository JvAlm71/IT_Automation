from playwright.sync_api import expect


def open_quotes_page(context):
	"""Opens the B3 quotes page and returns the chart page (opened in a popup)."""

	landing_page = context.new_page()
	landing_page.goto("https://borainvestir.b3.com.br/", wait_until="domcontentloaded")

	with landing_page.expect_popup() as chart_page_info:
		landing_page.get_by_role("link", name="Acompanhe as cotações").click()

	chart_page = chart_page_info.value
	chart_page.wait_for_load_state("domcontentloaded")
	return chart_page


def get_chart_frame(chart_page):
	"""Returns the FrameLocator for the TradingView 'advanced chart' widget."""

	chart_frame = chart_page.frame_locator('iframe[title="advanced chart TradingView widget"]')
	expect(chart_frame.get_by_role("button", name="Intervalo do gráfico")).to_be_visible()
	return chart_frame


def set_interval_1_day(chart_frame):
	"""Sets the chart interval to '1 dia'."""

	chart_frame.get_by_role("button", name="Intervalo do gráfico").click()
	chart_frame.get_by_role("row", name="1 dia").click()
