"""Organize files into subdirectories based on their extensions.

This tool scans a directory, optionally including subdirectories, and moves
files into extension-named folders. Files without extensions are placed in a
``no_ext`` directory. It defaults to a dry-run mode; supply ``--apply`` to
execute moves. If the target filename already exists, the script appends an
incrementing suffix (``_1``, ``_2``, etc.) to avoid overwriting.

Future work may add a ``type`` mode to group files by broader categories like
images, documents, or audio. Currently only the ``ext`` mode is implemented.

Example usage
-------------
Run in dry-run mode on the sample directory:

```
python -m onepass_office_toolbox.cli fs organize-ext --dir sample_data/fs_demo --dry-run
```
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for organizing files."""
    parser = argparse.ArgumentParser(
        description=(
            "Organize files into extension-based folders. Defaults to dry-run; "
            "use --apply to move files."
        )
    )
    parser.add_argument("--dir", "-d", required=True, help="Directory to organize.")
    parser.add_argument(
        "--recursive", "-r", action="store_true", help="Recurse into subdirectories.",
    )
    parser.add_argument(
        "--mode",
        choices=["ext"],
        default="ext",
        help="Organization mode. Currently only 'ext' is supported.",
    )
    parser.add_argument(
        "--target-root",
        help=(
            "Root directory where organized files will be placed. Defaults to the "
            "source directory."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview planned moves without applying them (default behavior).",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply the moves instead of dry-run."
    )
    return parser.parse_args(args)


def iter_files(base_dir: Path, recursive: bool) -> Iterable[Path]:
    """Yield files under ``base_dir`` respecting the recursive flag."""
    if recursive:
        yield from (p for p in base_dir.rglob("*") if p.is_file())
    else:
        yield from (p for p in base_dir.iterdir() if p.is_file())


def build_target_path(file_path: Path, target_root: Path) -> Path:
    """Determine the destination path for a file based on its extension."""
    ext = file_path.suffix.lower().lstrip(".")
    folder_name = ext if ext else "no_ext"
    return target_root / folder_name / file_path.name


def resolve_conflict(target: Path) -> Path:
    """Return a unique target path by appending numeric suffixes if necessary."""
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
    """Execute the organize-by-extension workflow."""
    parsed = parse_args(args)
    base_dir = Path(parsed.dir)

    if not base_dir.exists() or not base_dir.is_dir():
        print(f"Error: directory not found - {base_dir}")
        return 1

    target_root = Path(parsed.target_root) if parsed.target_root else base_dir
    dry_run = True if parsed.dry_run or not parsed.apply else False
    status_label = "DRY-RUN" if dry_run else "APPLY"

    files = list(iter_files(base_dir, parsed.recursive))
    if not files:
        print("No files found to organize.")
        return 0

    for file_path in files:
        destination = build_target_path(file_path, target_root)
        if destination.exists() and destination != file_path:
            destination = resolve_conflict(destination)

        print(f"[{status_label}] {file_path} -> {destination}")

        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            file_path.rename(destination)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
