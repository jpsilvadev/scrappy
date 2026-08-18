import asyncio
from typing import Self, TypedDict
from urllib.parse import urljoin, urlsplit

import aiohttp
import requests
from bs4 import BeautifulSoup, Tag


class UnsupportedContentTypeError(Exception):
    pass


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int, max_pages: int) -> None:
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session: aiohttp.ClientSession | None = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks: set[asyncio.Task] = set()

    async def __aenter__(self) -> Self:
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session is not None:
            await self.session.close()

    async def add_page_visit(self, normalized_url: str) -> bool:
        if self.should_stop:
            return False

        if len(self.page_data) == self.max_pages:
            self.should_stop = True
            print("Reached maximum number of pages to crawl.")
            for task in self.all_tasks:
                if not task.done():
                    task.cancel()
            return False

        async with self.lock:
            # returns true if first time visiting page
            return not normalized_url in self.page_data

    async def get_html(self, url: str) -> str | None:
        if self.session is None:
            return None
        try:
            async with self.session.get(
                url, headers={"User-Agent": "BootCrawler/1.0"}
            ) as r:
                if r.status > 399:
                    print(f"Error: HTTP {r.status} for {url}")
                    return None

                content_type = r.headers.get("content-type", "")
                if content_type.split(";")[0].strip() != "text/html":
                    print(f"Error: Non-HTML content {content_type} for {url}")
                    return None

                return await r.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def crawl_page(
        self,
        current_url: str | None = None,
    ) -> None:
        if self.should_stop:
            return

        if current_url is None:
            current_url = self.base_url

        parsed_current = urlsplit(current_url)
        if parsed_current.netloc != self.base_domain:
            return
        normalized_url = normalize_url(current_url)
        first_time_seeing = await self.add_page_visit(normalized_url)

        if not first_time_seeing:
            return

        async with self.semaphore:
            html = await self.get_html(current_url)
            print(f"starting crawl of {current_url}")
            if html is None:
                return

        async with self.lock:
            self.page_data[normalized_url] = extract_page_data(html, current_url)

        urls = self.page_data[normalized_url].get("outgoing_links", None)
        if not urls:
            return

        tasks = []
        for url in urls:
            task = asyncio.create_task(self.crawl_page(url))
            tasks.append(task)
            self.all_tasks.add(task)

        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                for task in tasks:
                    self.all_tasks.discard(task)

    async def crawl(self) -> dict[str, PageData] | None:
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(
    base_url: str, max_concurrency: int, max_pages: int
) -> dict[str, PageData] | None:
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    full_path = f"{parts.netloc}{parts.path}"
    full_path = full_path.rstrip("/")
    return full_path.lower()


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1")

    # fallback to h2
    if h_tag is None:
        h_tag = soup.find("h2")

    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main_tag = soup.find("main")
    p_tag = main_tag.find("p") if isinstance(main_tag, Tag) else None

    # fallback to just p if not in main
    if p_tag is None:
        p_tag = soup.find("p")

    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    urls = []
    soup = BeautifulSoup(html, "html.parser")
    anchor_tags = soup.find_all("a")
    for link in anchor_tags:
        if not isinstance(link, Tag):
            continue
        href = link.get("href")
        if not isinstance(href, str):
            continue
        urls.append(urljoin(base_url, href))
    return urls


def get_images_from_html(html: str, base_url: str) -> list[str]:
    images = []
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")
    for img in img_tags:
        if not isinstance(img, Tag):
            continue
        src = img.get("src")
        if not isinstance(src, str):
            continue
        images.append(urljoin(base_url, src))
    return images


def get_html(url: str) -> str | requests.exceptions.RequestException:
    try:
        r = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=30)
        r.raise_for_status()
        if r.headers.get("content-type", "").split(";")[0].strip() != "text/html":
            print(r.headers.get("content-type"))
            raise ValueError("Incorrect content-type")
    except requests.exceptions.RequestException as e:
        return e

    return r.text


def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


def crawl_page(
    base_url: str,
    current_url: str | None = None,
    page_data: dict[str, PageData] | None = None,
) -> dict[str, PageData]:
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    base_hostname = urlsplit(base_url).hostname
    current_hostname = urlsplit(current_url).hostname

    if current_hostname != base_hostname:
        return page_data

    normalized_url = normalize_url(current_url)

    if normalized_url in page_data:
        return page_data

    html = get_html(current_url)
    if isinstance(html, requests.exceptions.RequestException):
        return page_data

    print(f"crawling: {current_url}")
    page_data[normalized_url] = extract_page_data(html, current_url)

    urls = page_data[normalized_url].get("outgoing_links", None)
    if not urls:
        return page_data

    for url in urls:
        crawl_page(base_url, url, page_data)

    return page_data
