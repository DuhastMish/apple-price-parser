"""
GadgetBar parser implementation.
"""

import re
import time
import urllib.parse
from parser.base import BaseParser

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from python_utils.helper.datatype import to_int
from python_utils.helper.list import get_elem
from python_utils.logger.main import get_logger

LOGGER = get_logger()


class GadgetBarParser(BaseParser):
    """
    GadgetBar parser.
    """

    SITE = "https://gadget-bar.ru/"
    SEARCH_PATH = "search/?q="

    def get(self) -> list[str]:
        """
        Return result.
        """
        result = self._parse()
        result.sort(key=lambda product: (product.get("version")))

        return result

    def _parse(self) -> list[dict]:
        """
        Parse web site.
        """
        start_time = time.time()
        LOGGER.info(f"Parsing {self.SITE}")

        prev_search_args = ""
        found_products: list[Tag] = []

        for product in self.products:
            product_name = product.get("name")
            product_version = product.get("version")
            product_memory = self._prepare_memory(product.get("memory"))
            product_color = self._prepare_color(product.get("color"))

            search_args = urllib.parse.quote_plus(
                f"{product_name} {product_version} {product_memory} {product_color}"
            )

            if search_args != prev_search_args:
                try:
                    found_products: list[Tag] = self._search_product(search_args)
                except Exception as ex:
                    LOGGER.info(f"Error while getting site {self.SITE}: {ex}")
                    continue

                prev_search_args = search_args

            for found_product in found_products:
                found_price_raw: Tag = found_product.find(
                    "span", {"class": "product-item-price-current"}
                )
                found_price = re.search(r"\d+", found_price_raw.text) or ""

                is_lla = self._find_in_title(found_product, "(LL/A)")
                if is_lla:
                    continue

                found_version = self._find_in_title(
                    found_product, f"{product_version} {product_memory}"
                )
                if not found_version:
                    continue

                found_memory = self._find_in_title(found_product, product_memory)
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
                product.update({"gadgetbar": found_price})

        LOGGER.info(f"Parsing done for {round(time.time() - start_time)} sec.")

        return self.products

    def _search_product(self, search_args: str) -> list[Tag]:
        """
        Search products by args.
        """
        # Уснули чтобы не закидать запросами.
        time.sleep(1)

        page = requests.get(self.SITE + self.SEARCH_PATH + search_args, timeout=1000)
        soup = BeautifulSoup(page.content, "html.parser")
        found_products_list: Tag = (
            get_elem(
                soup.find_all("div", {"class": "search-page-list-products"}),
                0,
                with_error=False,
            )
            or []
        )

        if not found_products_list:
            return []

        found_products: list[Tag] = (
            found_products_list.find_all("div", {"class": "product-item"}) or []
        )

        return found_products

    def _prepare_memory(self, memory: str) -> str:
        """
        Prepare memory for current web site.
        """
        memory_map = {
            "128": "128GB",
            "256": "256GB",
            "512": "512GB",
            "1 ТБ": "1Tb",
        }

        return memory_map.get(memory) or memory

    def _prepare_color(self, color: str) -> str:
        """
        Prepare colors for current web site.
        """
        colors_map = {
            "тёмная ночь": "Midnight",
            "сияющая звезда": "Starlight",
            "синий": ["Blue", "Blue_"],
            "зеленый": "Green",
            "розовый": "Pink",
            "(PRODUCT)RED": "Red",
            "темная ночь": "Midnight",
            "голубой": "Blue",
            "фиолетовый": "Purple",
            "желтый": "Yellow",
            "красный": "Red",
            "черный космос": "Space Black",
            "серебристый": "Silver",
            "золотой": "Gold",
            "глубокий фиолетовый": "Deep Purple",
        }

        return colors_map.get(color) or color
