"""Fiscal calendar helpers.

AetherData uses a February–January fiscal year, matching a common
enterprise-storage calendar:

    FY2026 Q1 = Feb 2025 – Apr 2025
    FY2026 Q2 = May 2025 – Jul 2025
    FY2026 Q3 = Aug 2025 – Oct 2025
    FY2026 Q4 = Nov 2025 – Jan 2026
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

import pandas as pd

QUARTER_MONTHS = {
    "Q1": (2, 3, 4),
    "Q2": (5, 6, 7),
    "Q3": (8, 9, 10),
    "Q4": (11, 12, 1),
}


def parse_period(value: str | date | datetime | pd.Timestamp) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, pd.Timestamp):
        return value.date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized period value: {value!r}")


def fiscal_year(period: str | date | datetime | pd.Timestamp) -> int:
    """Return fiscal year for a calendar date. February starts the next FY."""
    d = parse_period(period)
    return d.year + 1 if d.month >= 2 else d.year


def fiscal_quarter(period: str | date | datetime | pd.Timestamp) -> str:
    d = parse_period(period)
    if d.month in (2, 3, 4):
        return "Q1"
    if d.month in (5, 6, 7):
        return "Q2"
    if d.month in (8, 9, 10):
        return "Q3"
    return "Q4"


def period_label(period: str | date | datetime | pd.Timestamp) -> str:
    d = parse_period(period)
    return f"{d.year:04d}-{d.month:02d}"


def fiscal_label(period: str | date | datetime | pd.Timestamp) -> str:
    return f"{fiscal_quarter(period)} FY{fiscal_year(period)}"


def months_for_quarter(fiscal_year_value: int, quarter: str) -> list[str]:
    quarter = quarter.upper()
    if quarter not in QUARTER_MONTHS:
        raise ValueError(f"Invalid quarter: {quarter}")
    months = []
    for month in QUARTER_MONTHS[quarter]:
        calendar_year = fiscal_year_value - 1 if month >= 2 else fiscal_year_value
        months.append(f"{calendar_year:04d}-{month:02d}")
    return months


def quarter_sort_key(fiscal_year_value: int, quarter: str) -> tuple[int, int]:
    return fiscal_year_value, int(quarter.upper().replace("Q", ""))


def iter_months(start: str, end: str) -> list[str]:
    start_d = parse_period(start)
    end_d = parse_period(end)
    start_month = date(start_d.year, start_d.month, 1)
    end_month = date(end_d.year, end_d.month, 1)
    out: list[str] = []
    current = start_month
    while current <= end_month:
        out.append(f"{current.year:04d}-{current.month:02d}")
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return out


def normalize_quarter(value: str | None) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip().upper().replace(" ", "")
    if text.startswith("Q") and text[1:].isdigit():
        return f"Q{int(text[1:])}"
    if text.isdigit() and 1 <= int(text) <= 4:
        return f"Q{int(text)}"
    raise ValueError(f"Invalid quarter: {value!r}")


def as_list(value: str | int | Iterable | None) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, (str, int, float)):
        return [value]
    return list(value)
