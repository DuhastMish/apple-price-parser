"""
Base products list.
"""

from config import PRODUCTS


def create_base_products_list() -> list[dict]:
    """
    Create base products list by config.
    """
    base_list = []

    for product_name, product_info in PRODUCTS.items():
        for product_version, product_specification in product_info.items():
            available_memory = product_specification.get("memory") or []
            available_colors = product_specification.get("color") or []

            for product_memory in available_memory:
                for product_color in available_colors:
                    base_list.append(
                        {
                            "name": product_name,
                            "version": product_version,
                            "memory": product_memory,
                            "color": product_color,
                        }
                    )

    return base_list
