"""
Formatter for result.
"""

from copy import deepcopy

from config import PRODUCTS
from python_utils.logger.main import get_logger

LOGGER = get_logger()


class Formatter:
    """
    Formatter for result.
    """

    def __init__(self, products: list[dict]) -> None:
        self.products = products

    def format(self) -> None:
        """
        Format result. Grouping and removing colors if they the same.
        """
        self.products.sort(
            key=lambda product: (
                product.get("version"),
                product.get("trade59") or 0,
                product.get("ipoint") or 0,
                product.get("swype59") or 0,
                product.get("appzone") or 0,
                product.get("gadgetbar") or 0,
                product.get("connect") or 0,
            )
        )

        self._group_result()
        self._remove_color()
        # self._remove_same_col()  # Removed by using cells merge in sheet.main

    def _group_result(self) -> None:
        """
        Group result by price and color.
        """
        LOGGER.info("Groping result")
        previous_product = {}
        products_to_del = []
        for product in self.products:
            if not previous_product or not self._is_products_matched(
                product, previous_product
            ):
                previous_product = product
                continue

            previous_product_color = previous_product.get("color")
            product_color = product.get("color")

            previous_product.update(
                {"color": ", ".join([previous_product_color, product_color])}
            )

            products_to_del.append(product)

        for product_to_del in products_to_del:
            self.products.remove(product_to_del)

        LOGGER.info("Grouping done")

    def _remove_same_col(self) -> None:
        """
        Remove same values in cols.

        # ! Unused
        """
        LOGGER.info("Removing same cols")
        prev_name = ""
        prev_version = ""
        prev_memory = ""

        for product in self.products:
            product_name = product.get("name")
            if prev_name != product_name:
                prev_name = product_name
            else:
                product.update({"name": ""})

            product_version = product.get("version")
            if prev_version != product_version:
                prev_version = product_version
            else:
                product.update({"version": ""})

            product_memory = product.get("memory")
            if prev_memory != product_memory:
                prev_memory = product_memory
            else:
                product.update({"memory": ""})

        LOGGER.info("Cols cleared")

    def _remove_color(self) -> None:
        """
        Remove colors for products if they matched.
        """
        LOGGER.info("Removing colors")
        for product in self.products:
            product_name = product.get("name")
            product_info = PRODUCTS.get(product_name) or {}
            if not product_info:
                continue

            product_version = product.get("version")
            product_info = product_info.get(product_version) or {}
            if not product_info:
                continue

            product_info_colors: set = set(product_info.get("color") or [])
            product_colors: set = set((product.get("color") or "").split(", "))

            if product_colors != product_info_colors:
                continue

            product.update({"color": ""})

        LOGGER.info("Colors removed")

    def _is_products_matched(self, product_1: dict, product_2: dict) -> bool:
        product_1_copy = deepcopy(product_1)
        product_2_copy = deepcopy(product_2)

        product_1_copy.pop("color", None)
        product_2_copy.pop("color", None)

        return product_1_copy == product_2_copy

    def _is_products_matched_wo_price(self, product_1: dict, product_2: dict) -> bool:
        keys_to_check = ["product", "version", "memory"]
        product_1_copy = {
            key: value for key, value in product_1.items() if key in keys_to_check
        }
        product_2_copy = {
            key: value for key, value in product_2.items() if key in keys_to_check
        }

        return product_1_copy == product_2_copy
