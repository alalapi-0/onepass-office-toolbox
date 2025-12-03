"""Analyze and deduplicate filename columns from spreadsheets."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import List, Optional

from ._common import (
    ColumnSelectionError,
    clean_filenames,
    deduplicate,
    extract_column,
    parse_column_selector,
    read_table,
)


def build_parser(*, add_help: bool = True) -> argparse.ArgumentParser:
    """Create the argument parser for the deduplication report tool."""
    parser = argparse.ArgumentParser(
        description=(
            "Analyze duplicates in a CSV/Excel filename column. "
            "Column indices are interpreted as zero-based when given as integers."
        ),
        add_help=add_help,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to the input CSV/Excel file.")
    parser.add_argument(
        "--column",
        "-c",
        required=True,
        help="Column name or zero-based index to analyze (e.g., 'filename' or 0).",
    )
    parser.add_argument(
        "--unique-output",
        "-u",
        default="unique_filenames.txt",
        help="Path to write the unique filename list (default: unique_filenames.txt).",
    )
    parser.add_argument(
        "--duplicates-output",
        "-d",
        default="duplicate_filenames.txt",
        help=(
            "Path to write duplicate filenames with counts "
            "(default: duplicate_filenames.txt)."
        ),
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding for output files (default: utf-8).",
    )
    parser.add_argument(
        "--strip-spaces",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Strip surrounding whitespace from filenames (default: enabled).",
    )
    parser.add_argument(
        "--drop-empty",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Drop empty or NaN values after cleaning (default: enabled).",
    )
    return parser


def analyze_duplicates(
    input_path: Path,
    column: str | int,
    *,
    unique_output: Path,
    duplicates_output: Path,
    encoding: str,
    strip_spaces: bool,
    drop_empty: bool,
) -> dict[str, int | str]:
    """Process the filename column and write unique and duplicate reports."""
    df = read_table(input_path)
    series = extract_column(df, column)

    cleaned = clean_filenames(series.tolist(), strip_spaces=strip_spaces, drop_empty=drop_empty)
    unique_list, removed_duplicates = deduplicate(cleaned, keep_order=True)

    counts = Counter(cleaned)
    duplicate_items = [(name, count) for name, count in counts.items() if count > 1]

    unique_output.write_text("\n".join(unique_list), encoding=encoding)
    duplicates_output.write_text(
        "\n".join(f"{name},{count}" for name, count in sorted(duplicate_items)),
        encoding=encoding,
    )

    return {
        "total_rows": len(series),
        "cleaned_count": len(cleaned),
        "unique_count": len(unique_list),
        "duplicate_name_count": len(duplicate_items),
        "duplicate_occurrences": sum(count - 1 for _, count in duplicate_items),
        "duplicates_removed": removed_duplicates,
        "unique_output_path": str(unique_output),
        "duplicates_output_path": str(duplicates_output),
    }


def main(args: Optional[List[str]] = None) -> int:
    """CLI entry for the filename deduplication report tool."""
    parser = build_parser()
    parsed = parser.parse_args(args=args)

    input_path = Path(parsed.input)
    column_selector = parse_column_selector(parsed.column)
    unique_output = Path(parsed.unique_output)
    duplicates_output = Path(parsed.duplicates_output)

    try:
        stats = analyze_duplicates(
            input_path,
            column_selector,
            unique_output=unique_output,
            duplicates_output=duplicates_output,
            encoding=parsed.encoding,
            strip_spaces=parsed.strip_spaces,
            drop_empty=parsed.drop_empty,
        )
    except FileNotFoundError:
        print(f"Error: input file not found: {input_path}")
        return 1
    except ColumnSelectionError as exc:
        print(f"Error: {exc}")
        return 1
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Unexpected error: {exc}")
        return 1

    print("Duplicate analysis completed.")
    print(f"Total rows: {stats['total_rows']}")
    print(f"Valid filenames after cleaning: {stats['cleaned_count']}")
    print(f"Unique filenames: {stats['unique_count']}")
    print(f"Duplicate names: {stats['duplicate_name_count']}")
    print(f"Duplicate occurrences (beyond first): {stats['duplicate_occurrences']}")
    print(f"Unique list saved to: {stats['unique_output_path']}")
    print(f"Duplicates report saved to: {stats['duplicates_output_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
