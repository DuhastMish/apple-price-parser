"""
Connect parser implementation.
"""

import time
from parser.base import BaseParser

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from python_utils.helper.datatype import to_float, to_int
from python_utils.helper.list import get_elem
from python_utils.logger.main import get_logger

LOGGER = get_logger()


class ConnectParser(BaseParser):
    """
    Connect parser.
    """

    SITE = "https://www.connectperm.ru/"
    SEARCH_PATH = "search/?q="

    HARDCODE = {
        "Iphone 13": "iphone-13",
        "Iphone 14": "iphone-14",
        "Iphone 14 Plus": "iphone-14-plus",
        "Iphone 14 Pro": "",
        "Iphone 14 Pro Max": "",
        "Iphone 15": "iphone-15",
        "Iphone 15 Plus": "iphone-15-plus",
        "Iphone 15 Pro": "iphone-15-pro",
        "Iphone 15 Pro Max": "iphone-15-pro-max-",
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
        result.sort(key=lambda product: (product.get("version")))

        return result

    def _parse(self) -> list[dict]:
        """
        Parse web site.
        """
        start_time = time.time()
        LOGGER.info(f"Parsing {self.SITE}")

        iphones_ids = self._parse_product_id("iphone")
        iphones_json: list[dict] = self._get_products(iphones_ids)

        for product in self.products:
            product_name = product.get("name")
            product_version = product.get("version")
            product_color = self._prepare_color(product.get("color")).lower()
            product_memory = self._prepare_memory(product.get("memory"))

            for found_product in iphones_json:
                found_title = found_product.get("title")
                if found_title.lower() != f"{product_name} {product_version}".lower():
                    continue

                variants: list[dict] = found_product.get("variants") or []
                for variant in variants:
                    variant_title = (variant.get("title") or "").lower()

                    if product_memory not in variant_title:
                        continue

                    if product_color not in variant_title:
                        continue

                    if "e-sim" in variant_title and "1sim" not in variant_title:
                        continue

                    if "2sim" in variant_title:
                        continue

                    product.update({"connect": to_int(to_float(variant.get("price")))})

        LOGGER.info(f"Parsing done for {round(time.time() - start_time)} sec.")

        return self.products

    def _parse_product_id(self, product_name: str) -> list[str]:
        page = requests.get(
            self.SITE + "collection/" + product_name,
            timeout=1000,
        )
        soup = BeautifulSoup(page.content, "html.parser")
        found_products_list: Tag = (
            get_elem(
                soup.find_all("div", {"class": "products-grid"}),
                0,
                with_error=False,
            )
            or []
        )

        if not found_products_list:
            return []

        found_products: list[Tag] = (
            found_products_list.find_all("form", {"class": "product-card"}) or []
        )

        return [product.get("data-product-id") for product in found_products]

    def _get_products(self, product_ids: list[str]) -> list[dict]:
        """
        Search products by ids.
        """
        page = requests.get(
            self.SITE + "products_by_id/" + ",".join(product_ids) + ".json",
            headers={"Content-Type": "application/json"},
            timeout=1000,
        )

        if page.status_code != 200:
            return []

        return page.json().get("products")

    def _prepare_memory(self, memory: str) -> str:
        """
        Prepare memory for current web site.
        """
        memory_map = {
            "128": "128гб",
            "256": "256гб",
            "512": "512гб",
            "1 ТБ": "1тб",
            "1Tb": "1тб",
        }

        return memory_map.get(memory) or memory

    def _prepare_color(self, color: str) -> str:
        """
        Prepare colors for current web site.
        """
        colors_map = {
            "тёмная ночь": "Midnight",
            "сияющая звезда": "Starlight",
            "синий": "Blue",
            "зеленый": "Green",
            "розовый": "Pink",
            "темная ночь": "Midnight",
            "голубой": "Blue",
            "фиолетовый": "Purple",
            "желтый": "Yellow",
            "красный": "(PRODUCT)RED",
            "черный космос": "Space Black",
            "серебристый": "Silver",
            "золотой": "Gold",
            "глубокий фиолетовый": "Deep Purple",
        }

        return colors_map.get(color) or color
