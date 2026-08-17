from __future__ import annotations

import argparse
import json
from pathlib import Path

from bs4 import BeautifulSoup

GROUP_HEADING = "Az előző év azonos időszaka = 100,0%"
TOTAL_COLUMN = "Összesen"

MONTHS = {
    "január": 1,
    "február": 2,
    "március": 3,
    "április": 4,
    "május": 5,
    "június": 6,
    "július": 7,
    "augusztus": 8,
    "szeptember": 9,
    "október": 10,
    "november": 11,
    "december": 12,
}

def parse(html: str, year: int) -> dict[str, any]:
    soup = BeautifulSoup(html, "html.parser")
    
    table = soup.find("table", class_="stadat")
    if table is None:
        raise ValueError("No STADAT table found in the page")

    total_index = _total_column_index(table)
    tbody = _find_group(soup)

    result: dict[str, float | None] = {
        f"{year}-{month:02d}-01": None for month in MONTHS.values()
    }
    found = False
    current_year: int | None = None

    for row in tbody.find_all("tr", recursive=False):
        cells = row.find_all(["th", "td"])
        if len(cells) <= total_index:
            continue

        year_text = _normalize(_clean(cells[0]))
        if year_text:
            if not year_text.isdigit():
                continue
            
            current_year = int(year_text)

        month = MONTHS.get(_normalize(_clean(cells[1])).lower())
        if current_year != year or month is None:
            continue

        found = True
        value = _to_float(_clean(cells[total_index]))
        result[f"{year}-{month:02d}-01"] = round(value - 100, 1) if value is not None else None

    if not found:
        raise ValueError(f"No rows found for year {year}")

    return result

def _clean(cell) -> str:
    cell = cell.__copy__()
    for sup in cell.find_all("sup"):
        sup.decompose()
    return cell.get_text(strip=True).replace("\xa0", "").replace("\u2009", "")


def _normalize(text: str) -> str:
    return " ".join(text.split()).rstrip(".").strip()


def _to_float(text: str) -> float | None:
    text = text.strip()
    if not text or text in {"..", "…", "-", "–"}:
        return None
    return float(text.replace(" ", "").replace(",", "."))


def _find_group(soup: BeautifulSoup):
    for tbody in soup.find_all("tbody"):
        heading = tbody.find("tr")
        if heading and _normalize(_clean(heading)) == _normalize(GROUP_HEADING):
            return tbody
    raise ValueError(f"Group not found on the page: {GROUP_HEADING!r}")


def _total_column_index(table) -> int:
    header_row = table.find("thead").find_all("tr")[-1]
    position = 0
    for cell in header_row.find_all(["th", "td"]):
        span = int(cell.get("colspan", 1))
        if _clean(cell) == TOTAL_COLUMN:
            return position
        position += span
    raise ValueError(f"Column not found in the table header: {TOTAL_COLUMN!r}")

