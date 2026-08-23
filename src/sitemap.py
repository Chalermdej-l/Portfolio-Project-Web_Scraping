"""Step 1: download the Booking.com hotel sitemap index and split URLs per country.

Booking.com publishes a sitemap index (https://www.booking.com/sitembk-hotel-index.xml)
that links one gzipped child sitemap per language. We keep the English (en-us) child
sitemaps, flatten their <loc> entries into one list, and write one CSV per country
code so the scraping step can shard the work.
"""

import logging
import re
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SITEMAP_INDEX_URL = "https://www.booking.com/sitembk-hotel-index.xml"
COUNTRY_CODE_RE = re.compile(r"booking\.com/hotel/([a-z]{2})/")
HOTEL_URL_DIR = Path("Hotel_url")
TEMP_SITEMAP_FILE = "ab.xml.gz"
REQUEST_TIMEOUT = (5, 30)

USER_AGENT = "hotel-scraper/1.0 (personal portfolio project; contact: https://github.com/Chalermdej-l)"
HEADERS = {"User-Agent": USER_AGENT}


def fetch_sitemap_index(url: str = SITEMAP_INDEX_URL) -> list[str]:
    """Return the list of en-us child sitemap URLs from the sitemap index."""
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml-xml")
    return [loc.text for loc in soup.select('loc:-soup-contains("en-us")')]


def expand_sitemap(index_url: str) -> list[str]:
    """Download one child sitemap and return its hotel <loc> URLs."""
    response = requests.get(index_url, stream=True, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    with open(TEMP_SITEMAP_FILE, "wb") as f:
        f.write(response.content)
    return pd.read_xml(TEMP_SITEMAP_FILE)["loc"].tolist()


def write_country_csvs(urls: list[str], output_dir: Path = HOTEL_URL_DIR) -> pd.DataFrame:
    """Write one CSV per country code (the index column is the URL position)."""
    url_df = pd.DataFrame(urls, columns=["code"])
    url_df["country_code"] = url_df["code"].str.extract(COUNTRY_CODE_RE, expand=False)
    output_dir.mkdir(parents=True, exist_ok=True)
    for country in url_df["country_code"].unique():
        url_df[url_df["country_code"] == country].reset_index(drop=True).to_csv(
            output_dir / f"url_country_{country}.csv"
        )
        logger.info("Wrote %s with %d URLs", country, (url_df["country_code"] == country).sum())
    return url_df


def run() -> pd.DataFrame:
    """Fetch the sitemap index, expand every en-us child sitemap, write the CSVs."""
    index_links = fetch_sitemap_index()
    logger.info("Found %d en-us child sitemaps", len(index_links))
    urls: list[str] = []
    for link in index_links:
        urls.extend(expand_sitemap(link))
    logger.info("Collected %d hotel URLs", len(urls))
    return write_country_csvs(urls)
