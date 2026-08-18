import asyncio
import sys

from crawl import crawl_site_async


async def main() -> None:
    args = sys.argv
    if len(args) < 2:
        print("no website provided")
        sys.exit(1)

    if len(args) > 4:
        print("too many arguments provided")
        sys.exit(1)

    base_url = args[1]
    try:
        max_concurrency = int(args[2])
        max_pages = int(args[3])
    except (TypeError, ValueError):
        print("Incorrect type for either `max_concurrency` or `max_pages`")
        print("Exiting...")
        sys.exit(1)

    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)
    if page_data is None:
        print("crawl failed")
        sys.exit(1)

    print(f"Found {len(page_data)} pages:")
    for page in page_data.values():
        print(f"- {page['url']}: {len(page['outgoing_links'])} outgoing links")


if __name__ == "__main__":
    asyncio.run(main())
