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
uv run main.py --base_url <base_url> --max_concurrency <max_concurrency> --max_pages <max_pages> [--output FILENAME]
```

Example:

```bash
uv run main.py --base_url "https://learnwebscraping.dev/practice/ecommerce/" --max_concurrency 3 --max_pages 50
```

This crawls up to 50 pages on `base_url` with up to 3 concurrent requests
and writes the results to `report.json` (or the file passed via `--output`).
