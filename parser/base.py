"""
Base parser implementation.
"""
from bs4.element import Tag

from python_utils.helper.datatype import as_array


class BaseParser:
    """
    Base parser implementation.
    """

    def __init__(self, products: dict) -> None:
        self.products = products

    def _find_in_title(self, tag_element: Tag, search_item: list | str) -> str:
        """
        Find item in title.
        """
        title = tag_element.find("a", title=True)["title"]

        search_item = as_array(search_item)

        for item in search_item:
            if str(item).lower() in title.lower():
                return str(item)

        return ""
