#!/usr/bin/env python3
"""Boundary-data tests for the v2 renderer."""

from __future__ import annotations

import copy
import math
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moxing import render_chart  # noqa: E402
from moxing.charts import DEFAULTS  # noqa: E402


def series_case(count: int, value_fn=lambda i: i + 1, long_label: bool = False):
    return [
        {
            "label": "这是一个用于验证结构接口布局的超长中文类目名称" if long_label else f"类目{i + 1}",
            "value": value_fn(i),
        }
        for i in range(count)
    ]


CASES = {
    "C1": [series_case(1), series_case(10), [], [{"label": "空值", "value": None}], series_case(5, lambda i: (i - 2) * 100), series_case(5, lambda _i: 100), series_case(3, long_label=True), series_case(3, lambda i: (i + 1) * 100_000_000)],
    "C2": [series_case(1), series_case(10), [], [{"label": "空值", "value": math.nan}], series_case(5, lambda i: (i - 2) * 100), series_case(5, long_label=True), series_case(5, lambda i: (i + 1) * 100_000_000)],
    "C3": [
        {"labels": ["1月"], "series": [{"name": "本期", "values": [100]}]},
        {"labels": [f"{i + 1}日" for i in range(30)], "series": [{"name": "本期", "values": list(range(30))}]},
        {"labels": [], "series": []},
        {"labels": ["1月", "2月"], "series": [{"name": "本期", "values": [None, 2]}]},
        {"labels": ["1月", "2月"], "series": [{"name": "本期", "values": [-20, 30]}]},
        {"labels": ["1月", "2月", "3月"], "series": [{"name": "本期", "values": [100, 100, 100]}]},
    ],
    "C4": [series_case(1), series_case(6), [], [{"label": "空值", "value": None}], series_case(3, lambda i: [-1, 2, 3][i]), series_case(4, lambda _i: 100), series_case(4, long_label=True)],
    "C5": [
        {"categories": ["类目1"], "series": [{"name": "产品A", "values": [100]}]},
        {"categories": [f"类目{i}" for i in range(10)], "series": [{"name": "产品A", "values": [i + 1 for i in range(10)]}]},
        {"categories": [], "series": []},
        {"categories": ["类目1"], "series": [{"name": "产品A", "values": [None]}]},
        {"categories": ["甲", "乙"], "series": [{"name": "产品A", "values": [-1, 2]}]},
    ],
    "C6": [
        [{"label": "期初", "value": 100, "type": "start"}, {"label": "期末", "value": 100, "type": "end"}],
        copy.deepcopy(DEFAULTS["C6"]), [], [{"label": "期初", "value": None, "type": "start"}],
        [{"label": "期初", "value": 100, "type": "start"}, {"label": "支出", "value": -150, "type": "decrease"}, {"label": "期末", "value": -50, "type": "end"}],
    ],
    "C7": [
        [{"task": "任务1", "start": "10-01", "end": "10-02", "progress": 50}],
        [{"task": f"任务{i}", "start": "10-01", "end": "10-02", "progress": i * 15} for i in range(10)],
        [], [{"task": "任务1", "start": None, "end": "10-02", "progress": None}],
        [{"task": "用于验证甘特图布局的超长中文任务名称", "start": "10-01", "end": "10-10", "progress": 50}],
    ],
    "C8": [
        [{"stage": "访问", "value": 100}],
        [{"stage": f"阶段{i}", "value": 100 - i * 10} for i in range(6)],
        [], [{"stage": "访问", "value": None}],
        [{"stage": f"阶段{i}", "value": 100} for i in range(4)],
    ],
    "C9": [
        copy.deepcopy(DEFAULTS["C9"]),
        {"value": None, "unit": "万元", "label": "营收"},
        {"value": -100, "unit": "万元", "label": "亏损", "target": 100, "yoy": -10},
        {"value": 200_000_000, "unit": "元", "label": "营收", "target": 300_000_000},
    ],
    "C10": [
        copy.deepcopy(DEFAULTS["C10"][:2]), copy.deepcopy(DEFAULTS["C10"]), [],
        [{"label": "区域", "value": None, "unit": "万元"}],
        [{"label": "区域甲", "value": -100, "unit": "万元", "yoy": -10}, {"label": "区域乙", "value": 100, "unit": "万元", "yoy": 10}],
    ],
}


def validate_html(source: str) -> None:
    lowered = source.lower()
    if re.search(r"(?:nan|(?<![a-z])inf(?![a-z]))", lowered):
        raise AssertionError("输出含 nan/inf")
    for attribute in ("width", "height", "r", "rx"):
        if re.search(fr'{attribute}="-\d', source):
            raise AssertionError(f"输出含负 {attribute}")
    required = ["viewBox=\"0 0 1172 500\"", "data-motion=\"align\"", "data-motion=\"lock\"", "window.Moxing", "prefers-reduced-motion"]
    for marker in required:
        if marker not in source:
            raise AssertionError(f"缺少 {marker}")
    if "http://" in lowered or "https://" in lowered:
        raise AssertionError("模板包含外部运行时 URL")


def main() -> None:
    failures = []
    passed = 0
    for chart_id, cases in CASES.items():
        for index, data in enumerate(cases):
            try:
                validate_html(render_chart(chart_id, copy.deepcopy(data)))
                passed += 1
            except Exception as exc:  # collect all failures
                failures.append(f"{chart_id}:{index}: {type(exc).__name__}: {exc}")
    print(f"passed={passed} failed={len(failures)}")
    for failure in failures:
        print(failure)
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
