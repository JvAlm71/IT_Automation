from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")

service = Service(log_output="geckodriver.log")

driver = webdriver.Firefox(options=options, service=service)
try:
    driver.get("https://www.bbc.com/portuguese/articles/cx2wz90jg5po")
    wait = WebDriverWait(driver, 10)
    titulo = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text
    print(titulo)


finally:
    driver.quit()