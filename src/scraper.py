"""Step 2: scrape one shard of a country's hotel URL list.

Each worker takes a contiguous slice of Hotel_url/url_country_<cc>.csv, requests
the hotel pages, and parses latitude/longitude, identifiers, currency and review
scores out of the inline <script> blobs. Results are written to
Output/worker_<start>-<end>.csv.
"""

import logging
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

HOTEL_URL_DIR = Path("Hotel_url")
OUTPUT_DIR = Path("Output")
REQUEST_TIMEOUT = (5, 30)
REQUEST_DELAY_SECONDS = 1.0
MAX_PARSE_RETRIES = 2
RETRY_SLEEP_SECONDS = 10

USER_AGENT = "hotel-scraper/1.0 (personal portfolio project; contact: https://github.com/Chalermdej-l)"

POSITION_SCRIPT_SELECTOR = "script:-soup-contains('booking.env.b_map_center_latitude')"
POSITION_KEYS = ("booking.env.b_map_center_longitude", "booking.env.b_map_center_latitude")
HOTEL_INFO_SCRIPT_SELECTOR = "script:-soup-contains('city_name')"
UTAG_KEYS = ("atnm", "hotel_name", "city_name", "region_name", "country_name", "dest_type", "dest_ufi", "hotel_id")
UTAG_DATA_RE = re.compile(r"window.utag_data\s=\s(.*?)\}", re.DOTALL)
CURRENCY_SCRIPT_SELECTOR = "script:-soup-contains('b_hotel_currencycode')"
CURRENCY_RE = re.compile(r'b_hotel_currencycode:\s"(.*?)",')
SCORE_SCRIPT_SELECTOR = "script:-soup-contains('PropertyReview:{}')"
SCORE_RE = re.compile(r'{"__typename":"PropertyReview","totalScore":(.*?)"}]}')
SCORE_SEGMENT_MARKER = '{"__typename":"ReviewQuestionSegment","question":'


def build_session(max_retries: int = 3, backoff_factor: float = 2) -> requests.Session:
    """A session with an honest user agent and retry-with-backoff for 5xx/429."""
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    retry = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def request_url(session: requests.Session, url: str) -> requests.Response:
    return session.get(url + "?lang=en-us", timeout=REQUEST_TIMEOUT)


def geturl_list(country_code: str) -> list[list]:
    """Return [index, url] pairs from the per-country URL CSV (index column kept on purpose)."""
    df = pd.read_csv(HOTEL_URL_DIR / f"url_country_{country_code}.csv")
    return df["code"].reset_index().values.tolist()


def parse_hotel(content: bytes) -> dict:
    """Parse one hotel page into the raw key/value dict written to the worker CSV."""
    sub_text: dict = {}
    result_hotel = BeautifulSoup(content, "html.parser")

    position_info = result_hotel.select_one(POSITION_SCRIPT_SELECTOR)
    for text in position_info.text.split("\n"):
        item = text.find("=") - 1
        if text[:item] in POSITION_KEYS:
            item = text[:-1].split("=")
            sub_text[item[0].strip()] = item[1].strip()

    hotel_info = result_hotel.select_one(HOTEL_INFO_SCRIPT_SELECTOR)
    js_data = UTAG_DATA_RE.search(hotel_info.text).group(1)
    for b in js_data.split("\n"):
        item = b.find(":")
        if b[:item] in UTAG_KEYS:
            item = b[:-2].split(":")
            sub_text[item[0].strip()] = item[1].strip().replace("'", "")

    currency_info = result_hotel.select_one(CURRENCY_SCRIPT_SELECTOR)
    sub_text["hotel_currency"] = CURRENCY_RE.search(currency_info.text).group(1)

    score_info = result_hotel.select_one(SCORE_SCRIPT_SELECTOR)
    js_data = SCORE_RE.search(score_info.text).group(1) + '"},'
    for d in js_data.split(SCORE_SEGMENT_MARKER):
        item_begin = d.find("customerType") + 15
        item_end = d.find("}", item_begin) - 1
        if d[item_begin:item_end] == "TOTAL":
            item_begin_type = d.find('"question":') + 12
            item_end_type = d.find(",", item_begin_type) - 1
            item_begin_score = d.find('"score":') + 8
            item_end_score = d.find(",", item_begin_score)
            sub_text[d[item_begin_type:item_end_type]] = d[item_begin_score:item_end_score]

    return sub_text


def worker_scrape(country: str, start: int, end: int) -> pd.DataFrame:
    """Scrape URLs [start:end] for one country and write Output/worker_<start>-<end>.csv."""
    link = geturl_list(country)
    link = link[start:end]
    session = build_session()
    final_list: list[dict] = []
    done_count = 0
    retry = 0
    print(f"Total of {len(link)} hotels in the list.")
    for a in link:
        url = a[1]
        index = a[0]
        result = False
        while not result:
            if retry > MAX_PARSE_RETRIES:
                print(f"Retry more than 3 times. skipping link {url}")
                retry = 0
                result = True
                break

            if done_count % 10 == 0:
                print(done_count)
                print(url)

            try:
                sub_text = {}
                result = request_url(session, url)

                if not result.ok:
                    raise RuntimeError(f"Didn't get the result {result.content}.")

                time.sleep(REQUEST_DELAY_SECONDS)
                sub_text = parse_hotel(result.content)
                sub_text["url_index"] = index + 1
                done_count += 1
                final_list.append(sub_text)
                retry = 0
                result = True

            except Exception:
                logger.exception("Error while processing script. Sleeping and retrying.")
                time.sleep(RETRY_SLEEP_SECONDS)
                retry += 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(final_list)
    df.to_csv(OUTPUT_DIR / f"worker_{start}-{end}.csv", index=False)
    print("Worker Done Executing.")
    return df
