# Booking.com Hotel Scraper

A personal data-engineering project: collect public hotel listing data from Booking.com
(coordinates, identifiers, currency, review scores) and load it into SQL Server for
exploratory analysis.

The pipeline is three steps:

1. **Get URLs** — download the public sitemap index, expand the `en-us` child sitemaps,
   and write one CSV per country code into `Hotel_url/`.
2. **Scrape** — split a country's URL list into shards and run one worker process per
   shard. Each worker parses the hotel pages and writes `Output/worker_<start>-<end>.csv`.
3. **Combine & load** — concatenate the worker CSVs, de-duplicate, align columns to the
   `Hotel_Info` schema, and bulk-insert into SQL Server.

## Project structure

```
src/
  config.py    # column layout + SQL insert contract (DB settings from env vars)
  sitemap.py   # step 1: sitemap index -> per-country URL CSVs
  scraper.py   # step 2: page fetching + parsing
  runner.py    # step 2b: shard math + worker process launching
  loader.py    # step 3: combine worker CSVs + SQL Server bulk load
  cli.py       # command-line entry point
notebooks/
  get_url.ipynb      # thin wrapper around src.sitemap
  scrape_booking.ipynb  # thin wrapper around src.runner / src.scraper
  combine_load.ipynb    # thin wrapper around src.loader
tests/             # unit tests + a captured-page fixture
image/             # screenshots referenced below
```

## Setup

Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` from the example (used by the load step):

```bash
copy .env.example .env
```

The load step needs a SQL Server with the `scape_booking` database and the
`Hotel_Info` table. The connection values come from environment variables
(`DB_DRIVER`, `DB_SERVER`, `DB_DATABASE`); defaults match a local SQL Express install.

## Usage

```bash
# Step 1: download sitemaps, write Hotel_url/url_country_<cc>.csv
python -m src.cli geturl

# Step 2: scrape one country with 10 parallel workers
python -m src.cli scrape --country th --workers 10

# ...or scrape a single shard (this is what each worker process runs)
python -m src.cli scrape --country th --start 0 --end 1973

# Step 3: combine Output/*.csv and insert into SQL Server
python -m src.cli combine
```

Notebooks in `notebooks/` do the same things with more interactive output.

## Design notes

- **Sharding math** — `runner.compute_ranges(total, nodes)` splits `[0, total)` into
  `nodes` contiguous slices of `round(total / nodes)`; the last slice absorbs the
  remainder. `tests/test_runner.py` pins the exact behaviour, including edge cases.
- **Resilience** — requests use a timeout, HTTP-level retry with backoff for 429/5xx,
  a short delay between page requests, and a bounded parse-retry loop per page.
- **Missing values** — a score that is absent on a page stays NULL through to the
  database; only `inuse` defaults to 0.
- **Parser** — the page parsing in `src/scraper.py` targets the exact markup that the
  pages ship in (inline `<script>` JSON blobs). `tests/fixtures/hotel.html` is a
  hand-captured representative page, and `tests/test_scraper.py` pins the parser's
  behaviour against it. If Booking.com changes their markup the tests fail first,
  which tells you the parser needs updating.

## Scraping ethics

- Public listing pages only, via the site's own public sitemap.
- Rate-limited (delay between requests) and retried politely on transient errors.
- An honest `User-Agent` identifying the project, not a browser impersonation.
- Data is used for personal learning / portfolio analysis only.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
ruff format --check .
```
