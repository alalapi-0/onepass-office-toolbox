"""Generate a clean filename list from a spreadsheet column."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from ._common import ColumnSelectionError, clean_filenames, deduplicate, extract_column, parse_column_selector, read_table


def build_parser(*, add_help: bool = True) -> argparse.ArgumentParser:
    """Create the argument parser for the excel-to-filenames tool."""
    parser = argparse.ArgumentParser(
        description=(
            "Read a column from CSV/Excel and export a cleaned filename list. "
            "Column indices are zero-based when provided as integers."
        ),
        add_help=add_help,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to the input CSV/Excel file.")
    parser.add_argument(
        "--column",
        "-c",
        required=True,
        help="Column name or zero-based index to extract (e.g., 'filename' or 0).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="filename_list.txt",
        help="Output text file path for the cleaned filenames (default: filename_list.txt).",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding for the output text file (default: utf-8).",
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
    parser.add_argument(
        "--unique",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove duplicate filenames (default: enabled).",
    )
    parser.add_argument(
        "--keep-order",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep original order when deduplicating (default: enabled).",
    )
    return parser


def process_filenames(
    input_path: Path,
    column: str | int,
    *,
    output: Path,
    encoding: str,
    strip_spaces: bool,
    drop_empty: bool,
    unique: bool,
    keep_order: bool,
) -> dict[str, int | str]:
    """Read, clean, and optionally deduplicate filenames from the given column."""
    df = read_table(input_path)
    series = extract_column(df, column)

    cleaned = clean_filenames(series.tolist(), strip_spaces=strip_spaces, drop_empty=drop_empty)
    deduped = cleaned
    removed = 0
    if unique:
        deduped, removed = deduplicate(cleaned, keep_order=keep_order)

    output.write_text("\n".join(deduped), encoding=encoding)

    return {
        "total_rows": len(series),
        "cleaned_count": len(cleaned),
        "deduped_count": len(deduped),
        "duplicates_removed": removed,
        "output_path": str(output),
    }


def main(args: Optional[List[str]] = None) -> int:
    """CLI entry for exporting filename lists."""
    parser = build_parser()
    parsed = parser.parse_args(args=args)

    input_path = Path(parsed.input)
    column_selector = parse_column_selector(parsed.column)
    output_path = Path(parsed.output)

    try:
        stats = process_filenames(
            input_path,
            column_selector,
            output=output_path,
            encoding=parsed.encoding,
            strip_spaces=parsed.strip_spaces,
            drop_empty=parsed.drop_empty,
            unique=parsed.unique,
            keep_order=parsed.keep_order,
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
    except Exception as exc:  # pragma: no cover - defensive catch for CLI
        print(f"Unexpected error: {exc}")
        return 1

    print("Filename list generated successfully.")
    print(f"Total rows: {stats['total_rows']}")
    print(f"Valid filenames after cleaning: {stats['cleaned_count']}")
    if parsed.unique:
        print(
            "After deduplication: "
            f"{stats['deduped_count']} (removed {stats['duplicates_removed']})"
        )
    print(f"Output saved to: {stats['output_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
