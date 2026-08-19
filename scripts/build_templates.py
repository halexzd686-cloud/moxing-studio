#!/usr/bin/env python3
"""Build all Moxing v2 animated SVG templates."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moxing import CHARTS, render_chart  # noqa: E402


TEMPLATES = ROOT / "templates"


def main() -> None:
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    for chart_id, meta in CHARTS.items():
        number = int(chart_id[1:])
        target = TEMPLATES / f"c{number:02d}-{meta['slug']}.html"
        target.write_text(render_chart(chart_id), encoding="utf-8")
        print(f"built {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
