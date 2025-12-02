"""Batch rename files with optional prefixes, suffixes, and extension casing.

This script provides a minimal yet practical renaming helper for files within a
single directory. It supports recursively scanning subdirectories, adding a
consistent prefix or suffix to file basenames, and normalizing extension
capitalization. By default it runs in dry-run mode to avoid accidental changes;
pass ``--apply`` to perform the rename operations.

Conflict handling: if the planned destination already exists, the script will
append an incrementing ``_1``, ``_2`` suffix to the basename to avoid
overwriting. This behavior is also reflected in the CLI help text.

Example usage
-------------
Run in dry-run mode on the sample directory:

```
python -m onepass_office_toolbox.cli fs rename-basic --dir sample_data/fs_demo --dry-run
```
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional


def iter_files(base_dir: Path, recursive: bool) -> Iterable[Path]:
    """Yield file paths under ``base_dir`` honoring the recursion flag."""
    if recursive:
        yield from (p for p in base_dir.rglob("*") if p.is_file())
    else:
        yield from (p for p in base_dir.iterdir() if p.is_file())


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the renaming tool."""
    parser = argparse.ArgumentParser(
        description=(
            "Batch rename files with optional prefix/suffix and extension case "
            "normalization. Defaults to dry-run; pass --apply to execute."
        )
    )
    parser.add_argument("--dir", "-d", required=True, help="Target directory to process.")
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Recurse into subdirectories when scanning for files.",
    )
    parser.add_argument("--prefix", help="Prefix to add before the file basename.")
    parser.add_argument("--suffix", help="Suffix to add after the file basename.")
    parser.add_argument(
        "--lower-ext",
        action="store_true",
        help="Convert file extensions to lowercase (mutually exclusive with --upper-ext).",
    )
    parser.add_argument(
        "--upper-ext",
        action="store_true",
        help="Convert file extensions to uppercase (mutually exclusive with --lower-ext).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print planned renames without applying them (default behavior).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the renames. If omitted, the command performs a dry-run.",
    )
    return parser.parse_args(args)


def build_new_name(path: Path, prefix: str | None, suffix: str | None, ext_mode: str | None) -> str:
    """Construct the new filename based on provided transformations."""
    stem = path.stem
    extension = path.suffix

    if prefix:
        stem = f"{prefix}{stem}"
    if suffix:
        stem = f"{stem}{suffix}"

    if ext_mode == "lower":
        extension = extension.lower()
    elif ext_mode == "upper":
        extension = extension.upper()

    return f"{stem}{extension}"


def resolve_conflict(target: Path) -> Path:
    """Generate a non-conflicting path by appending numbered suffixes."""
    if not target.exists():
        return target

    stem = target.stem
    extension = target.suffix
    counter = 1
    parent = target.parent
    while True:
        candidate = parent / f"{stem}_{counter}{extension}"
        if not candidate.exists():
            return candidate
        counter += 1


def main(args: Optional[List[str]] = None) -> int:
    """Run the rename utility based on provided CLI arguments."""
    parsed = parse_args(args)

    if parsed.lower_ext and parsed.upper_ext:
        print("Error: --lower-ext and --upper-ext cannot be used together.")
        return 1

    ext_mode: str | None
    if parsed.lower_ext:
        ext_mode = "lower"
    elif parsed.upper_ext:
        ext_mode = "upper"
    else:
        ext_mode = None

    base_dir = Path(parsed.dir)
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"Error: directory not found - {base_dir}")
        return 1

    dry_run = True if parsed.dry_run or not parsed.apply else False

    status_label = "DRY-RUN" if dry_run else "APPLY"
    files = list(iter_files(base_dir, parsed.recursive))

    if not files:
        print("No files found to rename.")
        return 0

    for file_path in files:
        new_name = build_new_name(file_path, parsed.prefix, parsed.suffix, ext_mode)
        target_path = file_path.with_name(new_name)

        if target_path.exists() and target_path != file_path:
            target_path = resolve_conflict(target_path)

        action_label = f"[{status_label}]"
        print(f"{action_label} {file_path} -> {target_path}")

        if not dry_run and target_path != file_path:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.rename(target_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
