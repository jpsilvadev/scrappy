import argparse
import asyncio
import sys

from crawl import crawl_site_async
from json_report import write_json_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl a website and write a JSON report.")
    parser.add_argument("--base_url", required=True, help="starting URL to crawl")
    parser.add_argument(
        "--max_concurrency", type=int, required=True, help="maximum concurrent requests"
    )
    parser.add_argument(
        "--max_pages", type=int, required=True, help="maximum number of pages to crawl"
    )
    parser.add_argument(
        "--output",
        default="report.json",
        help="output JSON report filename (default: report.json)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    print(f"Starting crawl of: {args.base_url}")
    page_data = await crawl_site_async(args.base_url, args.max_concurrency, args.max_pages)
    if page_data is None:
        print("Crawl failed. No data retrieved.")
        sys.exit(1)

    print(f"Crawl completed. Found {len(page_data)} pages.")
    write_json_report(page_data, args.output)


if __name__ == "__main__":
    asyncio.run(main())
