#!/usr/bin/env python3
"""Export the maintained C1–C24 default data as copyable JSON examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moxing.charts import CHARTS, DEFAULTS  # noqa: E402


def main() -> None:
    target = ROOT / "examples" / "data"
    target.mkdir(parents=True, exist_ok=True)
    for chart_id, meta in CHARTS.items():
        filename = f"c{int(chart_id[1:]):02d}-{meta['slug']}.json"
        (target / filename).write_text(
            json.dumps(DEFAULTS[chart_id], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"exported examples/data/{filename}")


if __name__ == "__main__":
    main()
