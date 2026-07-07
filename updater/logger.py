# ==========================================================
# updater/logger.py
# V2 - PART 1/2
# ==========================================================

import logging
from pathlib import Path


class Logger:

    def __init__(self):

        self.log_dir = (
            Path(__file__).resolve().parent.parent /
            "logs"
        )

        self.log_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.log_file = self.log_dir / "updater.log"

        self.logger = logging.getLogger(
            "JNAS_UPDATER"
        )

        self.logger.setLevel(
            logging.INFO
        )

        self.logger.handlers.clear()

        formatter = logging.Formatter(

            "%(asctime)s | %(levelname)s | %(message)s"

        )

        file_handler = logging.FileHandler(
            self.log_file,
            encoding="utf-8"
        )

        file_handler.setFormatter(
            formatter
        )

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(
            formatter
        )

        self.logger.addHandler(
            file_handler
        )

        self.logger.addHandler(
            console_handler
        )



# ==========================================================
# updater/logger.py
# V2 - PART 2/2 (FINAL)
# ==========================================================

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

    def debug(self, message):

        self.logger.debug(message)

    def separator(self):

        self.logger.info("=" * 70)

    def blank(self):

        self.logger.info("")


# ==========================================================
# END OF FILE
# ==========================================================
