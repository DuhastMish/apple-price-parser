"""
iPointParser parser implementation.
"""

import re
import time
from parser.base import BaseParser

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from python_utils.helper.datatype import to_int
from python_utils.helper.list import get_elem
from python_utils.logger.main import get_logger

LOGGER = get_logger()


class iPointParser(BaseParser):
    """
    iPointParser parser.
    """

    SITE = "https://ipointperm.ru/"

    HARDCODE = {
        "Iphone 13": "iphone-13-13-mini",
        "Iphone 14": "iphone-14-14-plus",
        "Iphone 14 Plus": "iphone-14-14-plus",
        "Iphone 14 Pro": "iphone-14-pro-14-pro-max",
        "Iphone 14 Pro Max": "iphone-14-pro-14-pro-max",
        "Iphone 15": "iphone-15",
        "Iphone 15 Plus": "iphone-15",
        "Iphone 15 Pro": "iphone-15-pro-15-pro-max",
        "Iphone 15 Pro Max": "iphone-15-pro-15-pro-max",
        "Iphone 16": "iphone-16-16-plus",
        "Iphone 16 Plus": "iphone-16-16-plus",
        "Iphone 16 Pro": "iphone-16-pro-16-pro-max",
        "Iphone 16 Pro Max": "iphone-16-pro-16-pro-max",
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
            product_color = self._prepare_color(product.get("color"))

            product_link = self.HARDCODE.get(f"{product_name} {product_version}")

            if prev_product_link != product_link:
                found_products: list[Tag] = self._search_product(product_link)
                prev_product_link = product_link

            for found_product in found_products:
                found_price_raw: Tag = found_product.find("span", {"class": "price"})
                found_price = re.search(r"\d+", found_price_raw.text) or ""
                found_memory = self._find_in_title(found_product, product_memory)
                found_title = self._find_in_title(found_product, f"{product_version} {product_memory}")

                if not found_title:
                    continue

                if not found_memory:
                    continue

                found_color = self._find_in_title(found_product, product_color)
                if not found_color:
                    continue

                is_esim = bool(self._find_in_title(found_product, ["esim", "e-sim"]))
                # TODO: eSim пропускаем
                if is_esim:
                    continue

                found_price = to_int(found_price.group()) or 0
                product.update({"ipoint": found_price})

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
                soup.find_all("div", {"class": "products-list row"}),
                0,
                with_error=False,
            )
            or []
        )

        if not found_products_list:
            return []

        found_products: list[Tag] = (
            found_products_list.find_all("div", {"class": "card-inner"}) or []
        )

        return found_products

    def _prepare_color(self, color: str) -> str:
        """
        Prepare colors for current web site.
        """
        colors_map = {
            "(PRODUCT)RED": "(PRODUCT) RED",
            "красный": "Product RED",
            "темная ночь": "Midnight",
            "сияющая звезда": ["Starlight", "Сияющая звезда"],
            "голубой": "Blue",
            "фиолетовый": "Purple",
            "желтый": "Yellow",
            "золотой": "Gold",
            "глубокий фиолетовый": "Deep Purple",
            "черный космос": "Space Black",
            "серебристый": "Silver",
        }

        return colors_map.get(color) or color

    def _prepare_memory(self, memory: str) -> str:
        """
        Prepare memory for current web site.
        """
        memory_map = {
            "1 ТБ": "1Tb",
        }

        return memory_map.get(memory) or memory
