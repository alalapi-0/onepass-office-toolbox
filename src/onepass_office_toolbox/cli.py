"""Command-line interface for OnePass Office Toolbox.

This module exposes the entrypoint for the toolbox collection. The current
version focuses on welcoming users and showcasing the planned tool categories.
Future iterations will populate each subcommand with concrete utilities.
"""
from __future__ import annotations

import argparse
from textwrap import dedent

from . import __version__


TOOL_CATEGORIES = {
    "fs": {
        "title": "fs_tools",
        "description": "File system tools (coming soon)",
        "details": "文件系统工具集合，具体工具将在后续轮次实现。",
    },
    "list": {
        "title": "list_tools",
        "description": "Excel/List tools (coming soon)",
        "details": "Excel/列表工具集合，后续补充批量处理脚本。",
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

    for name, meta in TOOL_CATEGORIES.items():
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
