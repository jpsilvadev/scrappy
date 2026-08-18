import json

from crawl import PageData


def write_json_report(
    page_data: dict[str, PageData] | None, filename: str = "report.json"
):
    if not page_data:
        return
    data = sorted(page_data.values(), key=lambda p: p["url"])
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
