# src/downloader.py

import importlib.util
from pathlib import Path

import requests

try:
    from config.config import HEADERS, TIMEOUT
except ModuleNotFoundError:
    config_path = Path(__file__).resolve().parents[1] / "config" / "config.py"
    spec = importlib.util.spec_from_file_location("scraper_engine_config", config_path)
    if spec is None or spec.loader is None:
        raise
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    HEADERS = config.HEADERS
    TIMEOUT = config.TIMEOUT

from src.logger import logger


def download_page(url):
    """
    Download HTML from a webpage.
    """

    try:
        logger.info(f"Downloading: {url}")

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        logger.info("Download successful")

        return response.text

    except requests.exceptions.RequestException as e:
        logger.error(f"Download failed: {e}")

        return None
