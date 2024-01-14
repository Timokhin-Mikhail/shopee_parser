import json
import logging
import pickle

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import google.auth
from googleapiclient.discovery import build
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data_file import search_depth, products_list, id_spreadsheet
from datetime import date


def check_verification(driver):
    url = driver.current_url
    if "/verify/" in url:
        logging.info("Need Very Need Very Need Very Need Very Need Very Need Very Need Very Need Very Need Very Need Very Need Very Need Very")
        raise Exception
    return


if __name__ == '__main__':
    driver = None
    logging.basicConfig(level=logging.INFO, filename="/home/mikhail/Desktop/pars_shop/shopee_log.log", filemode="a", format="%(asctime)s: %(message)s")
    logging.info("Launching the parser")
    try:
        # opening a browser with hidden information about automatic operation
        options = Options()
        options.add_argument("--headless")
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

        driver.get('https://shopee.co.id/')
        for cookie in pickle.load(open("/home/mikhail/Desktop/pars_shop/cookies_test", "rb")):
            driver.add_cookie(cookie)
        sleep(5)
        driver.get('https://shopee.co.id/')
        check_verification(driver)
        logging.info("Start of parsing")
        result_list = []
        count_page = 0
        while True:
            for keyword, product_name in products_list:
                logging.info(f"Parsing {keyword}")


                current_date = date.today().strftime("%d.%m.%Y")
                product_list = [current_date, keyword, "-", "0"]

                search_textarea = (WebDriverWait(driver, 5).
                                              until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                    "body header input"))))
                search_textarea.click()
                for _ in range(100):
                    search_textarea.send_keys(Keys.BACK_SPACE)
                search_textarea.send_keys(keyword)
                sleep(1)  # waiting time before entering a search query
                search_textarea.send_keys(Keys.ENTER)
                sleep(1)
                check_verification(driver)
                count_page += 1
                sleep(2)

                try:

                    count_page_with_result = (WebDriverWait(driver, 5).
                                              until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                    ".shopee-mini-page-controller__total"))))
                    count_page_with_result = int(count_page_with_result.text.strip())
                    count = 1
                    page = 1
                    flag = False
                    while count < search_depth:
                        footer = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                                "body footer")))
                        change_count = 1
                        while True:
                            products = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                                                                    ".row.shopee-search-item-result__items li")))
                            for product in products:
                                sleep(0.02)
                                ActionChains(driver).scroll_to_element(product).perform()
                            ActionChains(driver).scroll_to_element(footer).perform()
                            products_href = driver.find_elements(By.CSS_SELECTOR, ".row.shopee-search-item-result__items li a")
                            if change_count >= 3 or len(products) == len(products_href):
                                break
                            change_count += 1
                        for product in products_href:
                            href_product = product.get_attribute('href')
                            if product_name in href_product:
                                product_list[2] = href_product
                                product_list[3] = count
                                flag = True
                                logging.info(f"Item position found: {count}")
                                logging.info("Go to the search for the next product (if available)")
                                break
                            count += 1
                        if page < count_page_with_result and count < search_depth and not flag:
                            page += 1
                            count_page += 1
                            next_page_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                                ".shopee-icon-button.shopee-icon-button--right")))
                            sleep(1)  # waiting time before going to the next page
                            logging.info(f"Go to the next page (page {page})")
                            next_page_button.click()
                            check_verification(driver)
                            sleep(2)
                        else:
                            logging.info("Item position not found")
                            logging.info("Go to the search for the next product (if available)")
                            break

                except Exception as ex:

                    logging.exception(ex)
                result_list.append(product_list)
            if result_list:
                # Getting access to work with Google tables
                creds, _ = google.auth.load_credentials_from_file('key.json')
                service = build('sheets', 'v4', credentials=creds)
                dictionary = {
                    "majorDimension": "ROWS",
                    "values": result_list
                }
                json_object = json.dumps(dictionary, indent=4)
                my = service.spreadsheets().values().append(spreadsheetId=id_spreadsheet,
                                                            range='Sheet1!A1:E1',
                                                            body=dictionary, valueInputOption="RAW", ).execute()

    except Exception as ex:
        logging.exception(ex)
    finally:
        logging.info("Completion of work")
        if driver:
            driver.close()
            driver.quit()
