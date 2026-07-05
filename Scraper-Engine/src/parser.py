# src/parser.py

from bs4 import BeautifulSoup

from src.logger import logger


def parse_html(html):
    """
    Parse HTML and extract useful information.
    """

    soup = BeautifulSoup(html, "lxml")

    title = soup.title.string.strip() if soup.title else ""

    headings = [
        tag.get_text(strip=True)
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    ]

    paragraphs = [
        tag.get_text(strip=True)
        for tag in soup.find_all("p")
    ]

    links = [
        tag.get("href")
        for tag in soup.find_all("a", href=True)
    ]

    images = [
        tag.get("src")
        for tag in soup.find_all("img", src=True)
    ]

    logger.info("HTML parsed successfully")

    return {
        "title": title,
        "headings": headings,
        "paragraphs": paragraphs,
        "links": links,
        "images": images
    }
