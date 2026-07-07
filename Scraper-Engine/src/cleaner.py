# src/cleaner.py

from src.logger import logger


def clean_data(data):
    """
    Clean extracted data.
    """

    cleaned = {}

    # Title
    cleaned["title"] = data.get("title", "").strip()

    # Headings
    cleaned["headings"] = list(
        dict.fromkeys(
            h.strip()
            for h in data.get("headings", [])
            if h.strip()
        )
    )

    # Paragraphs
    cleaned["paragraphs"] = list(
        dict.fromkeys(
            p.strip()
            for p in data.get("paragraphs", [])
            if p.strip()
        )
    )

    # Links
    cleaned["links"] = list(
        dict.fromkeys(
            link.strip()
            for link in data.get("links", [])
            if link
        )
    )

    # Images
    cleaned["images"] = list(
        dict.fromkeys(
            img.strip()
            for img in data.get("images", [])
            if img
        )
    )

    logger.info("Data cleaned successfully")

    return cleaned
