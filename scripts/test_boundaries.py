#!/usr/bin/env python3
"""对 10 个模板执行边界数据生成测试。"""
from __future__ import annotations

import copy
import importlib.util
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_templates", ROOT / "scripts" / "build_templates.py")
BT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(BT)


def series_case(count, value_fn=lambda i: i + 1, long_label=False):
    return [
        {
            "label": ("这是一个用于验证静态布局的超长中文类目名称" if long_label else f"类目{i + 1}"),
            "value": value_fn(i),
        }
        for i in range(count)
    ]


CASES = {
    1: [
        ("one", series_case(1)),
        ("many", series_case(10)),
        ("empty", []),
        ("null", [{"label": "空值", "value": None}]),
        ("negative", series_case(4, lambda i: (-1 if i % 2 else 1) * (i + 1) * 100)),
        ("equal", series_case(5, lambda _i: 100)),
        ("long", series_case(3, long_label=True)),
        ("huge", series_case(3, lambda i: (i + 1) * 100_000_000)),
    ],
    2: [
        ("one", series_case(1)), ("many", series_case(10)), ("empty", []),
        ("null", [{"label": "空值", "value": None}]),
        ("negative", series_case(5, lambda i: (i - 2) * 100)),
        ("equal", series_case(5, lambda _i: 100)),
        ("long", series_case(5, long_label=True)),
        ("huge", series_case(5, lambda i: (i + 1) * 100_000_000)),
    ],
    3: [
        ("one", {"labels": ["1月"], "series": [{"name": "本期", "values": [100]}]}),
        ("many", {"labels": [f"{i + 1}月" for i in range(30)], "series": [{"name": "本期", "values": list(range(30))}]}),
        ("empty", {"labels": [], "series": []}),
        ("null", {"labels": ["1月", "2月", "3月"], "series": [{"name": "本期", "values": [100, None, 120]}]}),
        ("negative", {"labels": ["1月", "2月"], "series": [{"name": "本期", "values": [-20, 30]}]}),
        ("equal", {"labels": ["1月", "2月", "3月"], "series": [{"name": "本期", "values": [100, 100, 100]}]}),
        ("huge", {"labels": ["1月", "2月"], "series": [{"name": "本期", "values": [100_000_000, 200_000_000]}]}),
    ],
    4: [
        ("one", series_case(1)), ("many", series_case(6)), ("empty", []),
        ("null", [{"label": "空值", "value": None}]),
        ("negative", series_case(3, lambda i: [-1, 2, 3][i])),
        ("equal", series_case(4, lambda _i: 100)),
        ("long", series_case(4, long_label=True)),
        ("huge", series_case(4, lambda i: (i + 1) * 100_000_000)),
    ],
    5: [
        ("one", {"categories": ["类目1"], "series": [{"name": "产品A", "values": [100]}]}),
        ("many", {"categories": [f"类目{i}" for i in range(10)], "series": [{"name": "产品A", "values": [i + 1 for i in range(10)]}]}),
        ("empty", {"categories": [], "series": []}),
        ("null", {"categories": ["类目1"], "series": [{"name": "产品A", "values": [None]}]}),
        ("equal", {"categories": ["甲", "乙", "丙"], "series": [{"name": "产品A", "values": [100, 100, 100]}]}),
        ("huge", {"categories": ["甲", "乙"], "series": [{"name": "产品A", "values": [100_000_000, 200_000_000]}]}),
    ],
    6: [
        ("one", [{"label": "期初", "value": 100, "type": "start"}, {"label": "期末", "value": 100, "type": "end"}]),
        ("many", copy.deepcopy(BT.C6_DATA)), ("empty", []),
        ("null", [{"label": "期初", "value": None, "type": "start"}]),
        ("negative", [{"label": "期初", "value": 100, "type": "start"}, {"label": "支出", "value": -150, "type": "decrease"}, {"label": "期末", "value": -50, "type": "end"}]),
        ("huge", [{"label": "期初", "value": 100_000_000, "type": "start"}, {"label": "期末", "value": 100_000_000, "type": "end"}]),
    ],
    7: [
        ("one", [{"task": "任务1", "start": "10-01", "end": "10-02", "progress": 50}]),
        ("many", [{"task": f"任务{i}", "start": "10-01", "end": "10-02", "progress": i * 10} for i in range(10)]),
        ("empty", []),
        ("null", [{"task": "任务1", "start": None, "end": "10-02", "progress": None}]),
        ("long", [{"task": "这是一个用于验证甘特图布局的超长中文任务名称", "start": "10-01", "end": "10-10", "progress": 50}]),
    ],
    8: [
        ("one", [{"stage": "访问", "value": 100}]),
        ("many", [{"stage": f"阶段{i}", "value": 100 - i * 10} for i in range(6)]),
        ("empty", []),
        ("null", [{"stage": "访问", "value": None}]),
        ("equal", [{"stage": f"阶段{i}", "value": 100} for i in range(4)]),
        ("huge", [{"stage": "访问", "value": 200_000_000}, {"stage": "注册", "value": 100_000_000}]),
    ],
    9: [
        ("normal", copy.deepcopy(BT.C9_DATA)),
        ("null", {"value": None, "unit": "万元", "label": "营收", "yoy": None, "mom": None}),
        ("negative", {"value": -100, "unit": "万元", "label": "亏损", "yoy": -10, "mom": -5}),
        ("huge", {"value": 200_000_000, "unit": "元", "label": "营收", "yoy": 10, "mom": 5}),
    ],
    10: [
        ("two", copy.deepcopy(BT.C10_DATA[:2])),
        ("four", copy.deepcopy(BT.C10_DATA)),
        ("empty", []),
        ("null", [{"label": "区域", "value": None, "unit": "万元", "yoy": None, "mom": None}]),
        ("negative", [{"label": "区域甲", "value": -100, "unit": "万元", "yoy": -10, "mom": -5}, {"label": "区域乙", "value": 100, "unit": "万元", "yoy": 10, "mom": 5}]),
        ("huge", [{"label": "区域甲", "value": 200_000_000, "unit": "元", "yoy": 10, "mom": 5}, {"label": "区域乙", "value": 100_000_000, "unit": "元", "yoy": 5, "mom": 2}]),
    ],
}


def validate_svg(svg):
    lowered = svg.lower()
    if re.search(r"(?:nan|(?<![a-z])inf(?![a-z]))", lowered):
        raise AssertionError("SVG 含 nan/inf")
    for attr in ("width", "height", "r", "rx"):
        if re.search(fr'{attr}="-\d', svg):
            raise AssertionError(f"SVG 含负 {attr}")
    if not ("<text" in svg or "暂无" in svg):
        raise AssertionError("SVG 没有静态文本")


def main():
    failures = []
    passed = 0
    for chart, cases in CASES.items():
        data_name = f"C{chart}_DATA"
        original = copy.deepcopy(getattr(BT, data_name))
        builder = getattr(BT, f"build_c{chart}_svg")
        for case_name, data in cases:
            try:
                setattr(BT, data_name, copy.deepcopy(data))
                svg = builder()
                validate_svg(svg)
                passed += 1
            except Exception as exc:  # 汇总全部失败，不在首个 case 停止
                failures.append(f"C{chart}:{case_name}: {type(exc).__name__}: {exc}")
            finally:
                setattr(BT, data_name, copy.deepcopy(original))
    print(f"passed={passed} failed={len(failures)}")
    for item in failures:
        print(item)
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
