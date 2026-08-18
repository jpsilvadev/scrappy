import asyncio
import sys

from crawl import crawl_site_async
from json_report import write_json_report


async def main() -> None:
    args = sys.argv
    if len(args) < 2:
        print("usage: uv run main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)

    if len(args) > 4:
        print("usage: uv run main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)

    base_url = args[1]
    try:
        max_concurrency = int(args[2])
        max_pages = int(args[3])
    except (TypeError, ValueError):
        print("Incorrect type for either `max_concurrency` or `max_pages`")
        print("Exiting...")
        sys.exit(1)

    print(f"Starting crawl of: {base_url}")
    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)
    if page_data is None:
        print("Crawl failed. No data retrieved.")
        sys.exit(1)

    print(f"Crawl completed. Found {len(page_data)} pages.")
    write_json_report(page_data)


if __name__ == "__main__":
    asyncio.run(main())
