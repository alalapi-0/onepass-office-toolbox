"""Command-line interface for OnePass Office Toolbox.

This module exposes the entrypoint for the toolbox collection. The current
version focuses on welcoming users and showcasing the planned tool categories.
Future iterations will populate each subcommand with concrete utilities."""
from __future__ import annotations

import argparse
from textwrap import dedent

from . import __version__
from .fs_tools import organize_by_extension_main, rename_files_basic_main
from .list_tools import dedup_filename_column_main, excel_to_filename_list_main


TOOL_CATEGORIES = {
    "fs": {
        "title": "fs_tools",
        "description": "File system tools",
        "details": "文件系统工具集合：包含基础的重命名和按扩展名整理功能。",
    },
    "list": {
        "title": "list_tools",
        "description": "Excel/List tools",
        "details": "Excel/列表工具集合：包含列提取和去重分析。",
    },
    "report": {
        "title": "report_tools",
        "description": "Reporting and reconciliation tools (coming soon)",
        "details": "报告与对账工具集合，后续补充差异检查等功能。",
    },
    "text": {
        "title": "text_tools",
        "description": "Text cleanup tools (coming soon)",
        "details": "文本清洗工具集合，后续补充规范化与清洗脚本。",
    },
}


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="onepass-office-toolbox",
        description=(
            "OnePass Office Toolbox: a collection of command-line helpers for "
            "office automation tasks."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the OnePass Office Toolbox version and exit.",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="category")

    fs_parser = subparsers.add_parser(
        "fs",
        help=TOOL_CATEGORIES["fs"]["description"],
        description=dedent(
            f"""
            {TOOL_CATEGORIES['fs']['details']}

            状态: 可用工具:
            - rename-basic: 批量重命名文件（前缀/后缀/扩展名大小写）
            - organize-ext: 按扩展名整理文件到子目录
            """
        ),
    )
    fs_subparsers = fs_parser.add_subparsers(dest="fs_command", metavar="tool")
    _register_fs_tools(fs_subparsers)
    fs_parser.set_defaults(func=_handle_fs_missing, _fs_parser=fs_parser)

    list_parser = subparsers.add_parser(
        "list",
        help=TOOL_CATEGORIES["list"]["description"],
        description=dedent(
            f"""
            {TOOL_CATEGORIES['list']['details']}

            可用工具:
            - excel-to-filenames: 从 Excel/CSV 某列生成干净文件名列表
            - dedup-filename-column: 分析文件名列的重复情况并输出报告
            """
        ),
    )
    list_subparsers = list_parser.add_subparsers(dest="list_command", metavar="tool")
    _register_list_tools(list_subparsers)
    list_parser.set_defaults(func=_handle_list_missing, _list_parser=list_parser)

    for name, meta in TOOL_CATEGORIES.items():
        if name in {"fs", "list"}:
            continue
        subparsers.add_parser(
            name,
            help=meta["description"],
            description=dedent(
                f"""
                {meta['details']}

                状态: coming soon
                """
            ),
        ).set_defaults(func=_handle_placeholder)

    return parser


def _register_fs_tools(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register available fs tools as subcommands."""
    rename_parser = subparsers.add_parser(
        "rename-basic",
        help="批量重命名文件（前缀/后缀/扩展名大小写）",
        description="Batch rename files with prefix/suffix and extension case normalization.",
    )
    _add_rename_arguments(rename_parser)
    rename_parser.set_defaults(func=_dispatch_rename_basic)

    organize_parser = subparsers.add_parser(
        "organize-ext",
        help="按扩展名整理文件到子目录",
        description="Organize files into extension-named folders (dry-run by default).",
    )
    _add_organize_arguments(organize_parser)
    organize_parser.set_defaults(func=_dispatch_organize_ext)


def _register_list_tools(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register available list tools as subcommands."""
    from .list_tools import dedup_filename_column, excel_to_filename_list

    excel_parent = excel_to_filename_list.build_parser(add_help=False)
    excel_parser = subparsers.add_parser(
        "excel-to-filenames",
        parents=[excel_parent],
        add_help=True,
        help="从 Excel/CSV 某列生成干净文件名列表",
        description=excel_parent.description,
    )
    excel_parser.set_defaults(func=_dispatch_excel_to_filenames)

    dedup_parent = dedup_filename_column.build_parser(add_help=False)
    dedup_parser = subparsers.add_parser(
        "dedup-filename-column",
        parents=[dedup_parent],
        add_help=True,
        help="分析文件名列的重复情况并输出报告",
        description=dedup_parent.description,
    )
    dedup_parser.set_defaults(func=_dispatch_dedup_filename_column)


def _add_rename_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach arguments shared with the rename_files_basic module."""
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
        help="Convert file extensions to lowercase (exclusive with --upper-ext).",
    )
    parser.add_argument(
        "--upper-ext",
        action="store_true",
        help="Convert file extensions to uppercase (exclusive with --lower-ext).",
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


def _add_organize_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach arguments shared with the organize_by_extension module."""
    parser.add_argument("--dir", "-d", required=True, help="Directory to organize.")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirectories.")
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
    parser.add_argument("--apply", action="store_true", help="Apply the moves instead of dry-run.")


def _handle_fs_missing(args: argparse.Namespace) -> None:
    """Show help when fs subcommand is missing."""
    parser: argparse.ArgumentParser | None = getattr(args, "_fs_parser", None)
    if parser:
        parser.print_help()
    else:
        print("Please provide a specific fs tool. Use --help for options.")


def _handle_list_missing(args: argparse.Namespace) -> None:
    """Show help when list subcommand is missing."""
    parser: argparse.ArgumentParser | None = getattr(args, "_list_parser", None)
    if parser:
        parser.print_help()
    else:
        print("Please provide a specific list tool. Use --help for options.")


def _handle_placeholder(args: argparse.Namespace) -> None:
    """Handle stub subcommands by printing placeholder guidance."""
    meta = TOOL_CATEGORIES.get(args.command, {})
    title = meta.get("title", args.command)
    description = meta.get("details", "更多工具即将上线。")
    print(f"[{title}] {description}")


def _print_welcome() -> None:
    """Display the welcome message and available tool categories."""
    print("OnePass Office Toolbox")
    print(f"Version: {__version__}")
    print("\nAvailable tool categories:")
    for meta in TOOL_CATEGORIES.values():
        print(f"- {meta['title']} – {meta['description']}")


def _dispatch_rename_basic(args: argparse.Namespace) -> None:
    """Forward parsed arguments to the rename_files_basic tool."""
    tool_args: list[str] = ["--dir", args.dir]
    if args.recursive:
        tool_args.append("--recursive")
    if args.prefix:
        tool_args.extend(["--prefix", args.prefix])
    if args.suffix:
        tool_args.extend(["--suffix", args.suffix])
    if args.lower_ext:
        tool_args.append("--lower-ext")
    if args.upper_ext:
        tool_args.append("--upper-ext")
    if args.dry_run:
        tool_args.append("--dry-run")
    if args.apply:
        tool_args.append("--apply")

    rename_files_basic_main(tool_args)


def _dispatch_organize_ext(args: argparse.Namespace) -> None:
    """Forward parsed arguments to the organize_by_extension tool."""
    tool_args: list[str] = ["--dir", args.dir]
    if args.recursive:
        tool_args.append("--recursive")
    if args.mode:
        tool_args.extend(["--mode", args.mode])
    if args.target_root:
        tool_args.extend(["--target-root", args.target_root])
    if args.dry_run:
        tool_args.append("--dry-run")
    if args.apply:
        tool_args.append("--apply")

    organize_by_extension_main(tool_args)


def _dispatch_excel_to_filenames(args: argparse.Namespace) -> None:
    """Forward arguments to the excel_to_filename_list tool."""
    tool_args: list[str] = ["--input", args.input, "--column", str(args.column)]
    tool_args.extend(["--output", args.output, "--encoding", args.encoding])
    if not args.strip_spaces:
        tool_args.append("--no-strip-spaces")
    if not args.drop_empty:
        tool_args.append("--no-drop-empty")
    if not args.unique:
        tool_args.append("--no-unique")
    if not args.keep_order:
        tool_args.append("--no-keep-order")

    excel_to_filename_list_main(tool_args)


def _dispatch_dedup_filename_column(args: argparse.Namespace) -> None:
    """Forward arguments to the dedup_filename_column tool."""
    tool_args: list[str] = [
        "--input",
        args.input,
        "--column",
        str(args.column),
        "--unique-output",
        args.unique_output,
        "--duplicates-output",
        args.duplicates_output,
        "--encoding",
        args.encoding,
    ]
    if not args.strip_spaces:
        tool_args.append("--no-strip-spaces")
    if not args.drop_empty:
        tool_args.append("--no-drop-empty")

    dedup_filename_column_main(tool_args)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the CLI.

    Parameters
    ----------
    argv: list[str] | None
        Optional list of arguments for easier testing. Defaults to None to use
        ``sys.argv`` as parsed by ``argparse``.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        _print_welcome()
        parser.print_help()
        return

    handler = getattr(args, "func", None)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
