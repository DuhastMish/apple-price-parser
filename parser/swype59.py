"""
Swype59 parser implementation.
"""

import re
import time
from parser.base import BaseParser

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from python_utils.helper.datatype import as_array, to_int
from python_utils.helper.list import get_elem
from python_utils.logger.main import get_logger

LOGGER = get_logger()


class Swype59Parser(BaseParser):
    """
    Swype59 parser.
    """

    SITE = "https://swype59.ru/"

    HARDCODE = {
        "Iphone 13": "iphone-13",
        "Iphone 14": "iphone-14",
        "Iphone 14 Plus": "iphone-14-plus",
        "Iphone 14 Pro": "",
        "Iphone 14 Pro Max": "",
        "Iphone 15": "iphone-15",
        "Iphone 15 Plus": "iphone-15-plus",
        "Iphone 15 Pro": "iphone-15-pro",
        "Iphone 15 Pro Max": "iphone-15-pro-max",
        "Iphone 16": "iphone-16",
        "Iphone 16 Plus": "iphone-16-plus",
        "Iphone 16 Pro": "iphone-16-pro",
        "Iphone 16 Pro Max": "iphone-16-pro-max",
    }

    def get(self) -> list[str]:
        """
        Return result.
        """
        result = self._parse()
        result.sort(
            key=lambda product: (
                product.get("version"),
                product.get("memory"),
            )
        )

        return result

    def _parse(self) -> list[dict]:
        """
        Parse web site.
        """
        start_time = time.time()
        LOGGER.info(f"Parsing {self.SITE}")

        prev_product_link = ""
        found_products: list[Tag] = []

        for product in self.products:
            product_name = product.get("name")
            product_version = product.get("version")
            product_memory = self._prepare_memory(product.get("memory"))

            product_link = self.HARDCODE.get(f"{product_name} {product_version}")

            if prev_product_link != product_link:
                found_products: list[Tag] = self._search_product(product_link)
                prev_product_link = product_link

            for found_product in found_products:
                found_price_raw: Tag = (
                    found_product.find("meta", {"itemprop": "price"}) or {}
                )
                found_price = re.search(r"\d+", found_price_raw.get("content")) or ""
                found_memory = self._find_in_title(found_product, product_memory)
                if not found_memory:
                    continue

                # ! У swype все цвета снаружи с одинаковыми ценами, только внутри карточки
                # found_color = self._find_in_title(found_product, product_color)
                # if not found_color:
                #     continue

                is_esim = bool(self._find_in_title(found_product, ["esim", "e-sim"]))
                # TODO: eSim пропускаем
                if is_esim:
                    continue

                found_price = to_int(found_price.group()) or 0
                product.update({"swype59": found_price})

        LOGGER.info(f"Parsing done for {round(time.time() - start_time)} sec.")
        return self.products

    def _search_product(self, search_args: str, nav_limit: int = 200) -> list[Tag]:
        """
        Search products by args.
        """
        time.sleep(1)
        page = requests.get(
            self.SITE + "collection/" + search_args + f"?page_size={nav_limit}",
            timeout=1000,
        )

        if page.status_code != 200:
            return []

        soup = BeautifulSoup(page.content, "html.parser")
        found_products_list: Tag = (
            get_elem(
                soup.find_all("div", {"class": "grid-list catalog-list"}),
                0,
                with_error=False,
            )
            or []
        )

        if not found_products_list:
            return []

        found_products: list[Tag] = (
            found_products_list.find_all("div", {"itemprop": "itemOffered"}) or []
        )

        return found_products

    def _prepare_memory(self, memory: str) -> str:
        """
        Prepare memory for current web site.
        """
        memory_map = {
            "1 ТБ": "1Tb",
        }

        return memory_map.get(memory) or memory

    def _find_in_title(self, tag_element: Tag, search_item: list | str) -> str:
        """
        Find item in title.
        """
        title = tag_element.find("a", {"itemprop": "url"})
        title = title.text

        search_item = as_array(search_item)

        for item in search_item:
            if str(item).lower() in title.lower():
                return str(item)

        return ""
