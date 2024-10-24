"""
Асинхронные регулярные задачи.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from python_utils.logger.main import get_logger

LOGGER = get_logger()


class Scheduler:
    """
    Класс для создания регулярных задач.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def run(self):
        """
        Create regular tasks.
        """
        LOGGER.info("Regular tasks added")

    def stop(self):
        """
        Stop regular tasks.
        """
        self.scheduler.shutdown()
        LOGGER.info("Regular tasks stopped")
