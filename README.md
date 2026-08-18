# Scrappy

A simple async web crawler. Given a starting URL, it crawls all pages on the
same domain, extracts page data (heading, first paragraph, outgoing links,
image URLs), and writes the results to a JSON report.

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv sync
```

## Usage

```bash
uv run main.py <base_url> <max_concurrency> <max_pages>
```

Example:

```bash
uv run main.py "https://learnwebscraping.dev/practice/ecommerce/" 3 50
```

This crawls up to 50 pages on `base_url` with up to 3 concurrent requests
and writes the results to `report.json`.
