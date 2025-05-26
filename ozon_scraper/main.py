import json
import time
from pathlib import Path

import undetected_chromedriver as uc
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ozon_scraper.functions import collect_product_info


def get_products_links(item_name: str | None = "Наушники hyperx") -> None:
    driver = uc.Chrome()
    driver.implicitly_wait(5)

    driver.get(url="https://ozon.ru")
    time.sleep(2)

    find_input = driver.find_element(By.NAME, "text")
    find_input.clear()
    find_input.send_keys(item_name)
    time.sleep(2)

    find_input.send_keys(Keys.ENTER)
    time.sleep(2)

    current_url = f"{driver.current_url}&sorting=rating"
    driver.get(url=current_url)
    time.sleep(2)

    # page_down(driver=driver)  # noqa: ERA001
    time.sleep(2)

    try:
        find_links = driver.find_elements(By.CLASS_NAME, "tile-hover-target")
        products_urls = list({f'{link.get_attribute("href")}' for link in find_links})

        logger.success("[+] Ссылки на товары собраны!")
    except Exception as e:  # noqa: BLE001
        logger.error("[!] Что-то сломалось при сборе ссылок на товары: {}", e)

    products_urls_dict = {}

    for k, v in enumerate(products_urls):
        products_urls_dict.update({k: v})

    with Path("products_urls_dict.json").open("w", encoding="utf-8") as file:
        json.dump(products_urls_dict, file, indent=4, ensure_ascii=False)

    time.sleep(2)

    products_data = []

    for url in products_urls:
        data = collect_product_info(driver=driver, url=url)
        logger.debug(f'[+] Собрал данные товара с id: {data.get("product_id")}')
        time.sleep(2)
        products_data.append(data)

    with Path("PRODUCTS_DATA.json").open("w", encoding="utf-8") as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)

    driver.close()
    driver.quit()


def main() -> None:
    logger.info("Сбор данных начался. Пожалуйста ожидайте...")
    get_products_links("Наушники hyperx")
    logger.info("Работа выполнена успешно!")
