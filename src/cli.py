"""Command-line entry point: geturl | scrape | combine.

Examples:
    python -m src.cli geturl
    python -m src.cli scrape --country th --workers 10
    python -m src.cli scrape --country th --start 0 --end 1973
    python -m src.cli combine
"""

import argparse
import logging


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="python -m src.cli", description="Booking.com hotel scraping pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("geturl", help="download the sitemap index and write per-country URL CSVs")

    scrape = sub.add_parser("scrape", help="scrape one country (all shards, or one shard)")
    scrape.add_argument("--country", required=True, help="two-letter country code, e.g. th")
    scrape.add_argument("--workers", type=int, default=10, help="number of parallel worker processes")
    scrape.add_argument("--start", type=int, default=None, help="shard start index (worker mode)")
    scrape.add_argument("--end", type=int, default=None, help="shard end index (worker mode)")

    sub.add_parser("combine", help="combine Output/*.csv and load into SQL Server")

    args = parser.parse_args(argv)

    if args.command == "geturl":
        from src.sitemap import run

        run()
    elif args.command == "scrape":
        if args.start is not None and args.end is not None:
            from src.scraper import worker_scrape

            worker_scrape(args.country, args.start, args.end)
        else:
            from src.runner import launch

            launch(args.country, args.workers)
    elif args.command == "combine":
        from src.loader import combine_files, load_to_sql

        load_to_sql(combine_files())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
