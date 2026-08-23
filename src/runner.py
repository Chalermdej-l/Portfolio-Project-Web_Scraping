"""Step 2b: split a country's URL list into shards and launch one worker per shard.

The scraping task is I/O bound, so N worker processes run concurrently, each
covering a contiguous slice of the URL list (the last shard absorbs the remainder
of round(total / nodes)).
"""

import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

HOTEL_URL_DIR = Path("Hotel_url")
DEFAULT_WORKERS = 10


def count_records(country_code: str) -> int:
    """Number of hotel URLs in the per-country CSV."""
    return len(pd.read_csv(HOTEL_URL_DIR / f"url_country_{country_code}.csv"))


def compute_ranges(total: int, nodes: int) -> list[tuple[int, int]]:
    """Split [0, total) into node slices; the last slice absorbs the rounding remainder."""
    per_node = round(total / nodes)
    ranges = []
    for i in range(nodes):
        to = (i + 1) * per_node
        if i + 1 == nodes:
            to = total
        ranges.append((per_node * i, to))
    return ranges


def launch(country_code: str, nodes: int = DEFAULT_WORKERS) -> list[int]:
    """Launch one `python -m src.cli scrape` process per shard and wait for all of them."""
    total = count_records(country_code)
    ranges = compute_ranges(total, nodes)
    logger.info("Launching %d workers for %s (%d URLs, %d per node)", nodes, country_code, total, round(total / nodes))
    processes = [
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "src.cli",
                "scrape",
                "--country",
                country_code,
                "--start",
                str(start),
                "--end",
                str(to),
            ]
        )
        for start, to in ranges
    ]
    exit_codes = [proc.wait() for proc in processes]
    failed = [i + 1 for i, code in enumerate(exit_codes) if code != 0]
    if failed:
        raise RuntimeError(f"Worker processes finished with errors: {failed}")
    return exit_codes
