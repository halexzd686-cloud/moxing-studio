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
    "C11": [copy.deepcopy(DEFAULTS["C11"]), {"variant": "pie", "items": copy.deepcopy(DEFAULTS["C11"])}, [], [{"label": "单一类目", "value": 100}], [{"label": "无效", "value": -1}]],
    "C12": [copy.deepcopy(DEFAULTS["C12"]), {"labels": [], "series": []}, {"labels": ["1", "2"], "series": [{"name": "指标", "values": [1, 1]}]}],
    "C13": [copy.deepcopy(DEFAULTS["C13"]), [], series_case(10, lambda _i: 100), [{"label": "负值", "value": -1}]],
    "C14": [copy.deepcopy(DEFAULTS["C14"]), {"columns": [], "rows": []}, {"columns": ["M0"], "rows": [{"label": "队列", "values": [100]}]}],
    "C15": [copy.deepcopy(DEFAULTS["C15"]), {"nodes": [], "links": []}, {"nodes": [{"id": "a", "label": "A", "level": 0, "value": 1}, {"id": "b", "label": "B", "level": 1, "value": 1}], "links": []}],
    "C16": [copy.deepcopy(DEFAULTS["C16"]), [], [{"label": "单点", "x": 1, "y": 1, "size": 0}], [{"label": "无效", "x": None, "y": 1, "size": 1}]],
    "C17": [copy.deepcopy(DEFAULTS["C17"]), [], [{"date": "01", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 0}]],
    "C18": [copy.deepcopy(DEFAULTS["C18"]), {"labels": [], "values": []}, {"labels": ["1", "2"], "values": [100, 100]}],
    "C19": [copy.deepcopy(DEFAULTS["C19"]), {"maturities": [], "series": []}, {"maturities": ["1Y", "2Y"], "series": [{"name": "曲线", "values": [2, 2]}]}],
    "C20": [copy.deepcopy(DEFAULTS["C20"]), {"rows": [], "columns": [], "values": []}, {"rows": ["A"], "columns": ["B"], "values": [[100]]}],
    "C21": [copy.deepcopy(DEFAULTS["C21"]), [], [1, 1], [1, math.nan, 2]],
    "C22": [copy.deepcopy(DEFAULTS["C22"]), {"labels": [], "values": []}, {"labels": ["A"], "values": [[1]]}],
    "C23": [copy.deepcopy(DEFAULTS["C23"]), {"labels": [], "actual": [], "forecast": [], "lower": [], "upper": []}],
    "C24": [copy.deepcopy(DEFAULTS["C24"]), {"labels": [], "values": [], "center": 0, "ucl": 1, "lcl": -1}, {"labels": ["1", "2"], "values": [1, 1], "center": 1, "ucl": 2, "lcl": 0}],
}


def validate_html(source: str) -> None:
    lowered = source.lower()
    if re.search(r"(?:nan|(?<![a-z])inf(?![a-z]))", lowered):
        raise AssertionError("输出含 nan/inf")
    for attribute in ("width", "height", "r", "rx"):
        if re.search(fr'{attribute}="-\d', source):
            raise AssertionError(f"输出含负 {attribute}")
    if "viewBox=\"0 0 1172 500\"" not in source and "class=\"pi-data-field\" viewBox=\"" not in source:
        raise AssertionError("缺少 v2 或精密裁切 viewBox")
    required = ["data-motion=\"align\"", "data-motion=\"lock\"", "data-total-brief=", "data-total-story=", "window.Moxing", "duration:total", "prefers-reduced-motion"]
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
