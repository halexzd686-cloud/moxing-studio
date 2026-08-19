#!/usr/bin/env python3
"""Render a custom Moxing v2 chart from JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moxing import render_chart  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a Moxing v2 animated SVG chart")
    parser.add_argument("--chart", required=True, help="C1 through C10")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--data", type=Path, help="UTF-8 JSON data file")
    source.add_argument("--data-json", help="inline JSON data")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title")
    parser.add_argument("--subtitle", default="单位与时间范围见图内标注")
    parser.add_argument("--footer", default="数据来源：用户提供 · 口径：见副标题")
    parser.add_argument("--surface", choices=["light", "dark"], default="light")
    parser.add_argument("--mode", choices=["brief", "editorial"], default="editorial")
    parser.add_argument("--linked-fonts", action="store_true", help="link repository font assets instead of embedding them")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = None
    if args.data:
        data = json.loads(args.data.read_text(encoding="utf-8"))
    elif args.data_json:
        data = json.loads(args.data_json)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_chart(
            args.chart,
            data,
            title=args.title,
            subtitle=args.subtitle,
            footer=args.footer,
            surface=args.surface,
            mode=args.mode,
            embed_fonts=not args.linked_fonts,
        ),
        encoding="utf-8",
    )
    print(f"rendered {output}")


if __name__ == "__main__":
    main()
