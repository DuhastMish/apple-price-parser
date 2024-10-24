"""
Google sheet table worker.
"""

from datetime import datetime

import gspread
from gspread.exceptions import WorksheetNotFound
from gspread.utils import ValueInputOption

from python_utils.helper.datetime import date_to_str
from python_utils.logger.main import get_logger

LOGGER = get_logger()


class TableWorker:
    """
    Google sheet worker.
    """

    TABLE_KEY = "1VYEuq_WXf5S01SwjJkerxM_FgshVYKIFmb8CVKLGDKk"

    def __init__(self):
        LOGGER.info("Initializing the connection to Google")
        self.gc = gspread.service_account(filename="credentials.json")
        self.table = self.gc.open_by_key(self.TABLE_KEY)
        LOGGER.info("Connection done")
        worksheet = None
        work_sheet_name = date_to_str(datetime.now(), "%d.%m.%Y")
        try:
            LOGGER.info("Looking for a worksheet")
            worksheet = self.table.worksheet(work_sheet_name)
        except WorksheetNotFound:
            LOGGER.info("Worksheet not found")
            LOGGER.info("Creating worksheet")
            worksheet = self.table.add_worksheet(
                title=work_sheet_name, rows=200, cols=20
            )
            worksheet.update(
                [
                    [
                        "Продукт",
                        "Версия",
                        "Память",
                        "Цвет",
                        "eSim",
                        "Trade59",
                        "iPoint",
                        "Swype59",
                        "AppZone",
                        "GadgetBar",
                        "Connect",
                        "Минимальная цена",
                    ]
                ],
                "A1:L1",
            )
            worksheet.format("A1:Z1", {"textFormat": {"bold": True}})
            LOGGER.info("Worksheet created")

        if not worksheet:
            raise WorksheetNotFound("Worksheet not found")

        self.worksheet = worksheet

    def insert(self, rows: list[dict]) -> None:
        LOGGER.info("Inserting rows")
        previons_product = {}
        overall_range = len(rows)
        rows_to_update: list[list] = []
        for idx, product in enumerate(rows):
            index = idx + 2
            product_name: str = product.get("name")
            product_version: str = product.get("version")
            product_memory: int = product.get("memory")
            product_color: str = product.get("color")
            product_esim: str = "Да" if product.get("is_esim") else ""

            if previons_product.get("name") == product_name:
                product_name = ""

            if previons_product.get("version") == product_version:
                product_version = ""

            if not product_version and previons_product.get("memory") == product_memory:
                product_memory = ""

            rows_to_update.append(
                [
                    product_name,
                    product_version,
                    product_memory,
                    product_color,
                    product_esim,
                    product.get("trade59") or "",
                    product.get("ipoint") or "",
                    product.get("swype59") or "",
                    product.get("appzone") or "",
                    product.get("gadgetbar") or "",
                    product.get("connect") or "",
                    f"=MIN(F{index}:K{index})"
                ]
            )
        self.worksheet.update(rows_to_update, f"A2:L{overall_range + 1}", value_input_option=ValueInputOption.user_entered)
        # TODO: Добавить позицию символа F в алфавите относительно количества ключей в первом элементме product

        LOGGER.info("Insert done")
