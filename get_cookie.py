import pickle
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

options = Options()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.page_load_strategy = "eager"
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
# executable_path - path to c chromedriver exe file
s = Service(executable_path=r"/usr/local/bin/chromedriver")
driver = webdriver.Chrome(options=options, service=s)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
  '''
})



driver.get('https://shopee.co.id/buyer/login')
input("After authorization, press enter...")
sleep(5)
driver.get('https://shopee.co.id/')
pickle.dump(driver.get_cookies(), open("cookies_test", "wb"))
input("After very...")

