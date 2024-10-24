"""
Google sheet table worker.
"""

import string
import time
from datetime import datetime

import gspread
from gspread.exceptions import WorksheetNotFound
from gspread.utils import ValueInputOption

from python_utils.helper.datetime import date_to_str
from python_utils.helper.list import get_elem
from python_utils.logger.main import get_logger

LOGGER = get_logger()


class TableWorker:
    """
    Google sheet worker.
    """

    TABLE_KEY = "1VYEuq_WXf5S01SwjJkerxM_FgshVYKIFmb8CVKLGDKk"
    RIGHT_TABLE_CORNER = "K"
    ROWS_COUNT = 300

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
                title=work_sheet_name, rows=self.ROWS_COUNT, cols=20
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
        """
        Insert and format rows.
        """
        self._clear_worksheet()
        self._set_default_format()
        rows_to_update = self._insert(rows)
        self._merge_same_values_in_cols(rows_to_update)

    def _set_default_format(self) -> None:
        """
        Set up default format.
        """
        LOGGER.info("Setting up default format")
        self.worksheet.format(
            f"A1:{self.RIGHT_TABLE_CORNER}{self.ROWS_COUNT}",
            {"verticalAlignment": "MIDDLE", "horizontalAlignment": "CENTER"},
        )
        LOGGER.info("Setup completed")

    def _clear_worksheet(self) -> None:
        """
        Clear cols before insert.
        """
        LOGGER.info("Clear worksheet")
        right_corner_index = string.ascii_uppercase.index(self.RIGHT_TABLE_CORNER)
        requests = [
            {
                "unmergeCells": {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": self.ROWS_COUNT,
                        "startColumnIndex": 0,
                        "endColumnIndex": right_corner_index,
                    }
                }
            }
        ]
        self.worksheet.spreadsheet.batch_update({"requests": requests})
        self.worksheet.batch_clear([f"A2:{self.RIGHT_TABLE_CORNER}{self.ROWS_COUNT}"])
        LOGGER.info("Worksheet cleared")

    def _insert(self, rows: list[dict]) -> list[list]:
        """
        Iserting rows as is.
        """
        overall_range = len(rows)

        LOGGER.info("Inserting rows")
        previons_product = {}
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
                    f"=MIN(F{index}:{self.RIGHT_TABLE_CORNER}{index})",
                ]
            )
        self.worksheet.update(
            rows_to_update,
            f"A2:L{overall_range + 1}",
            value_input_option=ValueInputOption.user_entered,
        )
        # TODO: Добавить позицию символа F в алфавите относительно количества ключей в первом элементме product

        LOGGER.info("Insert done")

        return rows_to_update

    def _merge_same_values_in_cols(self, rows: list[dict]) -> None:
        """
        Merge same values in cols to one.
        """
        LOGGER.info("Merging same values")

        # Added empty row for correct determine the last one
        rows.append({})

        right_corner_index = string.ascii_uppercase.index(self.RIGHT_TABLE_CORNER)
        for col_idx, col_letter in enumerate(
            string.ascii_uppercase[:right_corner_index]
        ):
            cells_idx_to_merge: list[list[int]] = []
            cells_sub_range: list[int] = []

            prev_row_value = None
            for rows_idx, row in enumerate(rows):
                row_value = get_elem(row, col_idx)

                if prev_row_value != row_value:
                    prev_row_value = row_value
                    if cells_sub_range:
                        cells_idx_to_merge.append(cells_sub_range)
                    cells_sub_range = []
                else:
                    cells_sub_range.append(rows_idx + 1)

            if not cells_idx_to_merge:
                continue

            for sub_range in cells_idx_to_merge:
                time.sleep(1)
                cells_range = f"{col_letter}{get_elem(sub_range, 0)}:{col_letter}{get_elem(sub_range, -1) + 1}"
                self.worksheet.merge_cells(cells_range, merge_type="MERGE_ALL")

        LOGGER.info("Values merged")
