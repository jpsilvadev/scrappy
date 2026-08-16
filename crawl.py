from typing import TypedDict
from urllib.parse import urljoin, urlsplit

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
