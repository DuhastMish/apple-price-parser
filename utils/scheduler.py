"""
Асинхронные регулярные задачи.
"""

import time
from formatter.main import Formatter
from parser.appzone import AppZoneParser
from parser.connect import ConnectParser
from parser.gadgetbar import GadgetBarParser
from parser.ipoint import iPointParser
from parser.main import create_base_products_list
from parser.swype59 import Swype59Parser
from parser.trade59 import Trade59Parser

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from python_utils.logger.main import get_logger
from sheet.main import TableWorker

LOGGER = get_logger()


class Scheduler:
    """
    Class for regular tasks.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def run(self):
        """
        Create regular tasks.
        """
        self.scheduler.add_job(self.regular_parse, "cron", hour=8)
        self.scheduler.add_job(self.regular_parse, "cron", hour=12)
        self.scheduler.add_job(self.regular_parse, "cron", hour=18)

        self.scheduler.start()
        LOGGER.info("Regular tasks added")

    def stop(self):
        """
        Stop regular tasks.
        """
        self.scheduler.shutdown()
        LOGGER.info("Regular tasks stopped")

    async def regular_parse(self) -> None:
        """
        Parser task.
        """
        LOGGER.info("Starting parser")

        start_time = time.time()

        product_to_parse = create_base_products_list()
        Trade59Parser(product_to_parse).get()
        ConnectParser(product_to_parse).get()
        iPointParser(product_to_parse).get()
        Swype59Parser(product_to_parse).get()
        AppZoneParser(product_to_parse).get()
        GadgetBarParser(product_to_parse).get()

        product_to_parse.sort(key=lambda product: (product.get("version")))

        Formatter(product_to_parse).format()

        TableWorker().insert(product_to_parse)

        LOGGER.info(f"Paring completed for {round(time.time() - start_time)}")
