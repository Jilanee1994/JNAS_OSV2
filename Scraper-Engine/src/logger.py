# src/logger.py

import logging
import os
import importlib.util
from pathlib import Path

try:
    from config.config import LOG_FILE
except ModuleNotFoundError:
    config_path = Path(__file__).resolve().parents[1] / "config" / "config.py"
    spec = importlib.util.spec_from_file_location("scraper_engine_config", config_path)
    if spec is None or spec.loader is None:
        raise
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    LOG_FILE = config.LOG_FILE

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ScraperEngine")
