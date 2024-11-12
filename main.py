"""
Runs parser.
"""

import asyncio
from formatter.main import Formatter
from parser.appzone import AppZoneParser
from parser.connect import ConnectParser
from parser.gadgetbar import GadgetBarParser
from parser.ipoint import iPointParser
from parser.main import create_base_products_list
from parser.swype59 import Swype59Parser
from parser.trade59 import Trade59Parser

from python_utils.logger.main import get_logger
from sheet.main import TableWorker
from utils.scheduler import Scheduler

LOGGER = get_logger()


if __name__ == "__main__":
    """
    Run parser.
    """
    LOGGER.info("Starting parser")

    scheduled_tasks = Scheduler()
    scheduled_tasks.run()

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

    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.error("Parser stopped!")
