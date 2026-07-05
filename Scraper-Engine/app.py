# app.py

import json
import csv
import os
import sys

from src.downloader import download_page
from src.parser import parse_html
from src.cleaner import clean_data
from src.logger import logger


def save_json(data):
    os.makedirs("outputs", exist_ok=True)

    with open("outputs/output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_csv(data):
    os.makedirs("outputs", exist_ok=True)

    with open("outputs/output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["Field", "Value"])

        for key, value in data.items():

            if isinstance(value, list):
                writer.writerow([key, " | ".join(value)])
            else:
                writer.writerow([key, value])


def main():

    if len(sys.argv) != 2:
        print("Usage:")
        print("python app.py <URL>")
        return

    url = sys.argv[1]

    html = download_page(url)

    if not html:
        return

    parsed = parse_html(html)

    cleaned = clean_data(parsed)

    save_json(cleaned)

    save_csv(cleaned)

    logger.info("Scraping completed successfully!")

    print("\nDone!")
    print("JSON : outputs/output.json")
    print("CSV  : outputs/output.csv")


if __name__ == "__main__":
    main()
