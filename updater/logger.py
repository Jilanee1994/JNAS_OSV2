# ==========================================================
# updater/logger.py
# COMPLETE FILE
# ==========================================================

import logging
from pathlib import Path


class Logger:

    def __init__(self):

        self.log_dir = Path.cwd() / "logs"
        self.log_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.log_file = self.log_dir / "updater.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger("JNAS-Updater")

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)


# ==========================================================
# END OF FILE
# ==========================================================
