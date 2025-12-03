"""Shared helpers for list_tools utilities.

This module centralizes reading tabular data and extracting/cleaning filename
columns for list-related tools. It avoids duplication between list utilities.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import pandas as pd


class ColumnSelectionError(ValueError):
    """Raised when a requested column is missing or invalid."""


def parse_column_selector(selector: str) -> str | int:
    """Interpret a column selector string as either a name or zero-based index.

    Integers are treated as zero-based positions. Non-integer strings are
    returned unchanged.
    """

    try:
        return int(selector)
    except ValueError:
        return selector


def read_table(input_path: Path) -> pd.DataFrame:
    """Load a CSV or Excel file into a pandas DataFrame."""
    suffix = input_path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(input_path)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(input_path)
    raise ValueError(f"Unsupported file extension: {suffix}")


def extract_column(df: pd.DataFrame, selector: str | int) -> pd.Series:
    """Return the selected column as a Series or raise ColumnSelectionError."""
    if isinstance(selector, int):
        if selector < 0 or selector >= df.shape[1]:
            raise ColumnSelectionError(
                f"Column index {selector} is out of range for {df.shape[1]} columns."
            )
        return df.iloc[:, selector]

    if selector not in df.columns:
        raise ColumnSelectionError(f"Column '{selector}' not found in table columns.")
    return df[selector]


def clean_filenames(
    values: Iterable[object],
    *,
    strip_spaces: bool = True,
    drop_empty: bool = True,
) -> List[str]:
    """Convert raw values to cleaned filename strings.

    Parameters
    ----------
    values:
        Iterable of raw cell values.
    strip_spaces:
        Whether to strip leading/trailing whitespace.
    drop_empty:
        Whether to discard empty or NaN-like values after normalization.
    """

    cleaned: List[str] = []
    for item in values:
        if pd.isna(item):
            if drop_empty:
                continue
            cleaned.append("")
            continue

        text = str(item)
        if strip_spaces:
            text = text.strip()
        if drop_empty and not text:
            continue
        cleaned.append(text)
    return cleaned


def deduplicate(
    items: Sequence[str], keep_order: bool = True
) -> Tuple[List[str], int]:
    """Return a deduplicated list and the number of removed items."""
    if not keep_order:
        unique_items = sorted(set(items))
        return unique_items, len(items) - len(unique_items)

    seen = set()
    unique_list: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique_list.append(item)
    removed = len(items) - len(unique_list)
    return unique_list, removed
