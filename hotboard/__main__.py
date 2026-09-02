"""命令行入口：python -m hotboard / hotboard 命令。"""

from __future__ import annotations

import argparse
import sys

from .core import fetch_all, to_console, to_json, to_markdown
from .sources import SOURCES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hotboard",
        description="全网热点实时聚合 —— 一次抓取微博/百度/知乎/B站/头条/抖音热搜",
    )
    parser.add_argument(
        "-s", "--sources",
        default=",".join(SOURCES.keys()),
        help="要抓取的平台，逗号分隔（默认全部）。可选: " + ",".join(SOURCES.keys()),
    )
    parser.add_argument(
        "-n", "--top",
        type=int, default=10,
        help="每个平台取前 N 条（默认 10）",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "markdown", "json"], default="text",
        help="输出格式（默认 text）",
    )
    parser.add_argument(
        "-o", "--output",
        help="写入文件，不指定则打印到控制台",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    invalid = [s for s in sources if s not in SOURCES]
    if invalid:
        print(f"未知平台: {', '.join(invalid)}，可选: {', '.join(SOURCES)}", file=sys.stderr)
        return 2

    payload = fetch_all(sources=sources, top=args.top)
    text = {"text": to_console, "markdown": to_markdown, "json": to_json}[args.format](payload)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"已写入 {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
