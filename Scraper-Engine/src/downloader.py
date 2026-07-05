# src/downloader.py

import requests

from config.config import HEADERS, TIMEOUT
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

