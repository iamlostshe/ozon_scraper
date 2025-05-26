import re
import time
from pathlib import Path

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


def page_down(driver: uc.Chrome) -> None:
    driver.execute_script(
        "const scrollStep = 200; // Размер шага прокрутки (в пикселях)\n"
        "const scrollInterval = 100; // Интервал между шагами (в миллисекундах)\n\n"
        "const scrollHeight = document.documentElement.scrollHeight;\n"
        "let currentPosition = 0;\n"
        "const interval = setInterval(() => {\n"
        "    window.scrollBy(0, scrollStep);\n"
        "    currentPosition += scrollStep;\n\n"
        "    if (currentPosition >= scrollHeight) {\n"
        "        clearInterval(interval);\n"
        "    }\n"
        "}, scrollInterval);\n",
    )


def collect_product_info(driver: uc.Chrome, url: str | None = "") -> dict:
    driver.switch_to.new_window("tab")

    time.sleep(3)
    driver.get(url=url)
    time.sleep(3)

    # product_id
    product_id = driver.find_element(
        By.XPATH, '//div[contains(text(), "Артикул: ")]',
    ).text.split("Артикул: ")[1]

    # print(product_id)  # noqa: ERA001

    page_source = str(driver.page_source)
    soup = BeautifulSoup(page_source, "lxml")

    with Path(f"product_{product_id}.html").open("w", encoding="utf-8") as file:
        file.write(page_source)

    product_name = soup.find("div", attrs={"data-widget": "webProductHeading"}).find(
        "h1").text.strip().replace("\t", "").replace("\n", " ")

    try:
        product_id = soup.find("div", string=re.compile(
            r"Артикул:",
        )).text.split("Артикул: ")[1].strip()
    except:  # noqa: E722
        product_id = None

    # product statistic
    try:
        product_statistic = soup.find(
            "div", attrs={"data-widget": "webSingleProductScore"}).text.strip()

        if " • " in product_statistic:
            product_stars = product_statistic.split(" • ")[0].strip()
            product_reviews = product_statistic.split(" • ")[1].strip()
    except:  # noqa: E722
        product_statistic = None
        product_stars = None
        product_reviews = None

    # product price
    try:
        ozon_card_price_element = soup.find(
            "span", string="c Ozon Картой").parent.find("div").find("span")
        product_ozon_card_price = ozon_card_price_element.text.strip(
        ) if ozon_card_price_element else ""

        price_element = soup.find(
            "span", string="без Ozon Карты").parent.parent.find("div").findAll("span")

        product_discount_price = price_element[0].text.strip(
        ) if price_element[0] else ""
        product_base_price = price_element[1].text.strip(
        ) if price_element[1] is not None else ""
    except:  # noqa: E722
        product_ozon_card_price = None
        product_discount_price = None
        product_base_price = None

    # product price
    try:
        ozon_card_price_element = soup.find(
            "span", string="c Ozon Картой").parent.find("div").find("span")
    except AttributeError:
        card_price_div = soup.find(
            "div", attrs={"data-widget": "webPrice"}).findAll("span")

        product_base_price = card_price_div[0].text.strip()
        product_discount_price = card_price_div[1].text.strip()

    product_data = {
        "product_id": product_id,
        "product_name": product_name,
        "product_ozon_card_price": product_ozon_card_price,
        "product_discount_price": product_discount_price,
        "product_base_price": product_base_price,
        "product_statistic": product_statistic,
        "product_stars": product_stars,
        "product_reviews": product_reviews,
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return product_data
