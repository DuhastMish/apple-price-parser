"""
Runs parser.
"""

import asyncio

from python_utils.logger.main import get_logger
from utils.scheduler import Scheduler

LOGGER = get_logger()


if __name__ == "__main__":
    """
    Run parser.
    """
    LOGGER.info("Starting parser")

    scheduled_tasks = Scheduler()
    scheduled_tasks.run()

    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.error("Parser stopped!")
