from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from .core import (
    H,
    W,
    ChartPage,
    circle,
    cut_rect_path,
    evidence_plate,
    format_num,
    group,
    html_page,
    is_number,
    line,
    motion,
    nice_ceil,
    no_data,
    path,
    polygon,
    rect,
    text,
)


DEFAULTS: dict[str, Any] = {
    "C1": [
        {"label": "华东", "value": 4280}, {"label": "华南", "value": 3650},
        {"label": "华北", "value": 2980}, {"label": "西南", "value": 1820},
        {"label": "华中", "value": 1450},
    ],
    "C2": [
        {"label": "华东客户服务中心", "value": 94}, {"label": "华南客户服务中心", "value": 87},
        {"label": "华北客户服务中心", "value": 82}, {"label": "西南客户服务中心", "value": 76},
        {"label": "华中客户服务中心", "value": 71}, {"label": "西北客户服务中心", "value": 65},
    ],
    "C3": {
        "labels": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "series": [
            {"name": "2025", "values": [820, 932, 901, 934, 1290, 1330, 1320, 1450, 1380, 1520, 1610, 1750]},
            {"name": "2024", "values": [620, 710, 680, 720, 890, 940, 910, 1020, 980, 1080, 1150, 1240]},
        ],
    },
    "C4": [
        {"label": "自然搜索", "value": 37}, {"label": "付费投放", "value": 28},
        {"label": "转介绍", "value": 21}, {"label": "社交媒体", "value": 14},
    ],
    "C5": {
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
            {"name": "产品 A", "values": [42, 46, 49, 52]},
            {"name": "产品 B", "values": [31, 30, 29, 27]},
            {"name": "其他", "values": [27, 24, 22, 21]},
        ],
    },
    "C6": [
        {"label": "期初", "value": 820, "type": "start"},
        {"label": "新增", "value": 310, "type": "increase"},
        {"label": "续约", "value": 180, "type": "increase"},
        {"label": "流失", "value": -240, "type": "decrease"},
        {"label": "折扣", "value": -90, "type": "decrease"},
        {"label": "期末", "value": 980, "type": "end"},
    ],
    "C7": [
        {"task": "洞察与定义", "start": "10-01", "end": "10-08", "progress": 100},
        {"task": "视觉系统", "start": "10-05", "end": "10-16", "progress": 82},
        {"task": "核心开发", "start": "10-12", "end": "10-28", "progress": 56},
        {"task": "测试验收", "start": "10-25", "end": "11-05", "progress": 18},
        {"task": "公开发布", "start": "11-04", "end": "11-08", "progress": 0},
    ],
    "C8": [
        {"stage": "访问", "value": 12000}, {"stage": "试用", "value": 7200},
        {"stage": "激活", "value": 4380}, {"stage": "付费", "value": 1860},
        {"stage": "续约", "value": 1420},
    ],
    "C9": {"label": "年度经常性收入", "value": 128_600_000, "unit": "元", "target": 150_000_000, "yoy": 23.8, "mom": 4.6},
    "C10": [
        {"label": "华东", "value": 15200, "unit": "万元", "yoy": 18.7},
        {"label": "华北", "value": 13100, "unit": "万元", "yoy": 23.5},
        {"label": "华南", "value": 9856, "unit": "万元", "yoy": -5.2},
        {"label": "西南", "value": 7421, "unit": "万元", "yoy": 31.8},
    ],
}


CHARTS = {
    "C1": {"slug": "structural-rank", "name": "Structural Rank", "title": "华东规模领先，优势来自稳定增长"},
    "C2": {"slug": "ranked-rail", "name": "Ranked Rail", "title": "华东服务评分居首，区域差距仍可控"},
    "C3": {"slug": "signal-trend", "name": "Signal Trend", "title": "增长在下半年加速，年末达到新高"},
    "C4": {"slug": "composition-field", "name": "Composition Field", "title": "自然搜索贡献最大，前三渠道占比达 86%"},
    "C5": {"slug": "composition-bands", "name": "Composition Bands", "title": "产品 A 持续扩张，结构集中度提高"},
    "C6": {"slug": "ledger-steps", "name": "Ledger Steps", "title": "新增和续约抵消流失，期末净增 160"},
    "C7": {"slug": "milestone-lanes", "name": "Milestone Lanes", "title": "核心开发进入中段，测试窗口即将开启"},
    "C8": {"slug": "stage-channel", "name": "Stage Channel", "title": "付费转化是主瓶颈，续约质量相对稳定"},
    "C9": {"slug": "metric-lockup", "name": "Metric Lockup", "title": "经常性收入同比增长 23.8%，完成目标 85.7%"},
    "C10": {"slug": "decision-interface", "name": "Decision Interface", "title": "华东营收领先，华南是唯一同比下滑区域"},
}


def _valid_series(data: Any, label_key: str = "label") -> list[dict[str, Any]]:
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict) and is_number(item.get("value")) and str(item.get(label_key, "")).strip()]


def build_c1(data: Any) -> str:
    items = _valid_series(data)[:10]
    if not items:
        return no_data()
    max_value = max(max(item["value"], 0) for item in items) or 1
    top = max(range(len(items)), key=lambda index: items[index]["value"])
    total_positive = sum(max(0, item["value"]) for item in items) or 1
    x0, x1, baseline, top_y = 300, 1134, 426, 88
    parts = [
        text(0, 32, "01 / RAIL ASSEMBLY", cls="index muted", size=13),
        text(0, 90, format_num(items[top]["value"]), cls="value title-font", size=52, weight=700, extra=motion("lock", 1350)),
        text(0, 117, f"{items[top]['label']} / 当前最高", cls="muted", size=15),
        evidence_plate(0, 278, "E-01", "SHARE", f"{items[top]['value'] / total_positive * 100:.1f}%", "占当前类目合计", delay=1420, width=226),
        line(x0, baseline, x1, baseline, cls="rail-strong", extra=f'pathLength="1" {motion("align", 80)}'),
    ]
    for tick in range(6):
        x = x0 + (x1 - x0) * tick / 5
        parts += [line(x, baseline - 8, x, baseline + 8, cls="rail", extra=motion("align", 120 + tick * 35)), text(x, 466, format_num(max_value * tick / 5), cls="muted index", anchor="middle", size=11)]
    band = (x1 - x0) / len(items)
    width = min(78, band * 0.56)
    for index, item in enumerate(items):
        height = max(2, max(0, item["value"]) / max_value * (baseline - top_y))
        x = x0 + band * index + (band - width) / 2
        y = baseline - height
        cls = "signal-fill" if index == top else ("data-fill" if index < 3 else "secondary-fill")
        shape = path(cut_rect_path(x, y, width, height, 7), cls=cls, extra=motion("dock", 330 + index * 85, dy=34))
        seam = line(x + width * .5, baseline, x + width * .5, baseline + 11, cls="rail", extra=motion("align", 620 + index * 45))
        parts += [shape, seam, text(x + width / 2, y - 13, format_num(item["value"]), cls="value", anchor="middle", size=15, weight=650, extra=motion("lock", 970 + index * 45)), text(x + width / 2, baseline + 30, item["label"], cls="muted", anchor="middle", size=13)]
        if index == top:
            parts += [path(f"M {x-7} {y+18} V {y-7} H {x+18}", cls="signal-stroke", extra=f'pathLength="1" {motion("lock", 1280)}')]
    return "\n".join(parts)


def build_c2(data: Any) -> str:
    items = sorted(_valid_series(data), key=lambda item: item["value"], reverse=True)[:10]
    if not items:
        return no_data()
    maximum = max(max(item["value"], 0) for item in items) or 1
    x0, x1, y0 = 330, 1116, 70
    row = min(64, 378 / max(1, len(items)))
    parts = [text(0, 28, "02 / RANKED DATUM", cls="index muted", size=13), evidence_plate(0, 74, "R-01", "TOP", format_num(items[0]["value"]), items[0]["label"][:12], delay=1300, width=242)]
    for index, item in enumerate(items):
        y = y0 + index * row
        end = x0 + (x1 - x0) * max(0, item["value"]) / maximum
        parts += [
            text(0, y + 18, f"{index + 1:02d}", cls="index muted", size=12),
            text(44, y + 18, item["label"], cls="label", size=14, weight=600 if index == 0 else None),
            line(x0, y + 12, x1, y + 12, cls="grid", extra=f'pathLength="1" {motion("align", 80 + index * 35)}'),
            path(cut_rect_path(x0, y, max(4, end - x0), 24, 5), cls="signal-fill" if index == 0 else "data-fill", extra=motion("dock", 280 + index * 70, dx=-28)),
            line(end, y - 5, end, y + 30, cls="rail", extra=motion("align", 680 + index * 55)),
            text(min(x1 - 2, end + 12), y + 18, format_num(item["value"]), cls="value", size=14, weight=650, extra=motion("lock", 900 + index * 40)),
        ]
    return "\n".join(parts)


def build_c3(data: Any) -> str:
    labels = data.get("labels", []) if isinstance(data, dict) else []
    raw_series = data.get("series", []) if isinstance(data, dict) else []
    series = []
    for item in raw_series[:4]:
        values = item.get("values", []) if isinstance(item, dict) else []
        if labels and len(values) == len(labels) and all(is_number(v) for v in values):
            series.append({"name": str(item.get("name", "系列")), "values": values})
    if not labels or not series:
        return no_data()
    values = [v for item in series for v in item["values"]]
    low, high = min(values), max(values)
    padding = max((high - low) * .16, abs(high) * .04, 1)
    y_min = low - padding
    y_max = high + padding
    x0, x1, y0, y1 = 292, 1126, 74, 420
    x = lambda i: x0 + (x1 - x0) * i / max(1, len(labels) - 1)
    y = lambda v: y1 - (v - y_min) / max(1e-9, y_max - y_min) * (y1 - y0)
    latest = series[0]["values"][-1]
    peak_index = max(range(len(series[0]["values"])), key=lambda i: series[0]["values"][i])
    parts = [text(0, 28, "03 / PATH ROUTING", cls="index muted", size=13), evidence_plate(0, 74, "T-01", "LATEST", format_num(latest), f"{series[0]['name']} / {labels[-1]}", delay=1420, width=230)]
    for tick in range(5):
        yy = y0 + (y1 - y0) * tick / 4
        value = y_max - (y_max - y_min) * tick / 4
        parts += [line(x0, yy, x1, yy, cls="grid", extra=f'pathLength="1" {motion("align", 70 + tick * 35)}'), text(x0 - 14, yy + 4, format_num(value), cls="muted index", anchor="end", size=11)]
    step = max(1, len(labels) // 6)
    for index in range(0, len(labels), step):
        parts.append(text(x(index), y1 + 32, labels[index], cls="muted", anchor="middle", size=12))
    for series_index, item in enumerate(series):
        d = " ".join(("M" if index == 0 else "L") + f" {x(index):.2f} {y(value):.2f}" for index, value in enumerate(item["values"]))
        cls = "signal-stroke" if series_index == 0 else "secondary-stroke"
        parts.append(path(d, cls=cls, extra=f'pathLength="1" {motion("route", 300 + series_index * 120, duration=720)}'))
        for index, value in enumerate(item["values"]):
            if index in {0, len(labels) - 1, peak_index} or (series_index == 0 and index % max(1, len(labels)//5) == 0):
                point_cls = "signal-fill" if series_index == 0 and index in {peak_index, len(labels)-1} else "hollow"
                parts.append(circle(x(index), y(value), 4.5 if series_index == 0 else 3.5, cls=point_cls, extra=motion("dock", 650 + index * 35, dy=10)))
    px, py = x(peak_index), y(series[0]["values"][peak_index])
    parts += [line(px, py - 12, px, y0, cls="rail", extra=f'pathLength="1" {motion("align", 1100)}'), text(px, y0 - 10, f"PEAK / {labels[peak_index]}", cls="index signal-text", anchor="middle", size=11, extra=motion("lock", 1280))]
    return "\n".join(parts)


def build_c4(data: Any) -> str:
    items = [item for item in _valid_series(data) if item["value"] > 0][:6]
    if not items:
        return no_data()
    total = sum(item["value"] for item in items)
    shares = [item["value"] / total for item in items]
    units = 40
    raw = [share * units for share in shares]
    counts = [int(value) for value in raw]
    for index in sorted(range(len(items)), key=lambda i: raw[i] - counts[i], reverse=True)[: units - sum(counts)]:
        counts[index] += 1
    largest = max(range(len(items)), key=lambda i: items[i]["value"])
    parts = [text(0, 28, "04 / COMPOSITION BAY", cls="index muted", size=13), evidence_plate(0, 74, "F-01", "SHARE", f"{shares[largest]*100:.0f}%", items[largest]["label"], delay=1480, width=230)]
    start_x, start_y, cell_w, cell_h, gap = 310, 116, 34, 48, 6
    cumulative = []
    for idx, count in enumerate(counts):
        cumulative.extend([idx] * count)
    for index in range(units):
        row, col = divmod(index, 10)
        x, y = start_x + col * (cell_w + gap), start_y + row * (cell_h + gap)
        category = cumulative[index]
        cls = "signal-fill" if category == largest else f"cat-{category % 4 + 1}"
        parts.append(path(cut_rect_path(x, y, cell_w, cell_h, 5), cls=cls, extra=motion("dock", 260 + index * 22, dy=18)))
        parts.append(line(x + cell_w / 2, y + cell_h, x + cell_w / 2, y + cell_h + 5, cls="grid", extra=motion("align", 440 + index * 10)))
    legend_x = 770
    for index, item in enumerate(items):
        y = 108 + index * 58
        cls = "signal-fill" if index == largest else f"cat-{index % 4 + 1}"
        parts += [rect(legend_x, y, 12, 24, cls=cls, extra=motion("dock", 660 + index * 60, dx=-10)), text(legend_x + 28, y + 15, item["label"], size=14), text(1118, y + 15, f"{shares[index]*100:.1f}%", cls="value index", anchor="end", size=14, weight=650)]
    parts += [line(start_x, 382, start_x + 394, 382, cls="rail-strong", extra=f'pathLength="1" {motion("align", 100)}'), text(start_x, 410, "40 MODULES / EACH = 2.5%", cls="index muted", size=11)]
    return "\n".join(parts)


def build_c5(data: Any) -> str:
    categories = data.get("categories", []) if isinstance(data, dict) else []
    series = data.get("series", [])[:4] if isinstance(data, dict) else []
    valid = bool(categories) and series and all(len(item.get("values", [])) == len(categories) and all(is_number(v) and v >= 0 for v in item.get("values", [])) for item in series)
    if not valid:
        return no_data()
    totals = [sum(item["values"][i] for item in series) for i in range(len(categories))]
    if not any(totals):
        return no_data()
    parts = [text(0, 28, "05 / BAND AGGREGATION", cls="index muted", size=13), evidence_plate(0, 74, "B-01", "MIX", f"{series[0]['values'][-1]/max(1, totals[-1])*100:.0f}%", f"{series[0].get('name','主系列')} / 最新", delay=1450, width=230)]
    x0, x1, y0 = 318, 1122, 95
    row = min(78, 320 / max(1, len(categories)))
    for cat_index, category in enumerate(categories):
        y = y0 + cat_index * row
        total = totals[cat_index] or 1
        parts += [text(x0 - 20, y + 23, category, cls="muted", anchor="end", size=13), line(x0, y + 31, x1, y + 31, cls="grid", extra=f'pathLength="1" {motion("align", 80 + cat_index * 40)}')]
        cursor = x0
        for series_index, item in enumerate(series):
            width = (x1 - x0) * item["values"][cat_index] / total
            cls = "signal-fill" if series_index == 0 else f"cat-{series_index + 1}"
            parts.append(path(cut_rect_path(cursor, y, max(1, width - 4), 42, 5), cls=cls, extra=motion("dock", 320 + cat_index * 85 + series_index * 55, dx=-18)))
            if width > 74:
                parts.append(text(cursor + width / 2, y + 26, f"{item['values'][cat_index]/total*100:.0f}%", cls="index", anchor="middle", size=12, weight=650))
            cursor += width
    for index, item in enumerate(series):
        x = x0 + index * 190
        parts += [rect(x, 442, 12, 12, cls="signal-fill" if index == 0 else f"cat-{index+1}"), text(x + 22, 453, item.get("name", f"系列{index+1}"), cls="muted", size=12)]
    return "\n".join(parts)


def build_c6(data: Any) -> str:
    items = _valid_series(data)[:8]
    if len(items) < 2:
        return no_data()
    levels = []
    running = 0.0
    for index, item in enumerate(items):
        kind = item.get("type", "increase")
        if kind == "start":
            start, end = 0, item["value"]
            running = item["value"]
        elif kind == "end":
            start, end = 0, item["value"]
            running = item["value"]
        else:
            start, end = running, running + item["value"]
            running = end
        levels.append((start, end))
    min_v = min(0, *(min(pair) for pair in levels))
    max_v = max(1, *(max(pair) for pair in levels))
    pad = (max_v - min_v) * .12 or 1
    min_v -= pad
    max_v += pad
    x0, x1, y0, y1 = 300, 1126, 70, 418
    y = lambda v: y1 - (v - min_v) / (max_v - min_v) * (y1 - y0)
    band = (x1 - x0) / len(items)
    width = min(76, band * .58)
    final_delta = levels[-1][1] - levels[0][1]
    parts = [text(0, 28, "06 / LEDGER INTERLOCK", cls="index muted", size=13), evidence_plate(0, 74, "L-01", "NET", f"{final_delta:+,.0f}", "期初至期末", delay=1500, width=230), line(x0, y(0), x1, y(0), cls="rail-strong", extra=f'pathLength="1" {motion("align", 80)}')]
    for index, (item, pair) in enumerate(zip(items, levels)):
        start, end = pair
        top, bottom = min(y(start), y(end)), max(y(start), y(end))
        height = max(4, bottom - top)
        x = x0 + band * index + (band - width) / 2
        kind = item.get("type", "increase")
        cls = "signal-fill" if kind == "decrease" else ("data-fill" if kind in {"start", "end"} else "cat-1")
        parts += [path(cut_rect_path(x, top, width, height, 6), cls=cls, extra=motion("dock", 300 + index * 95, dy=26)), text(x + width / 2, top - 12, format_num(item["value"]), cls="value", anchor="middle", size=14, weight=650, extra=motion("lock", 900 + index * 45)), text(x + width / 2, y1 + 34, item["label"], cls="muted", anchor="middle", size=12)]
        if index < len(items) - 1:
            next_x = x0 + band * (index + 1) + (band - width) / 2
            parts.append(line(x + width, y(end), next_x, y(end), cls="rail", extra=f'pathLength="1" {motion("route", 620 + index * 90)}'))
    return "\n".join(parts)


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    for pattern in ("%m-%d", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value, pattern)
            return parsed.replace(year=2026) if pattern == "%m-%d" else parsed
        except ValueError:
            continue
    return None


def build_c7(data: Any) -> str:
    items = []
    if isinstance(data, list):
        for item in data[:10]:
            if not isinstance(item, dict):
                continue
            start = _parse_date(item.get("start"))
            end = _parse_date(item.get("end"))
            if start and end and end >= start:
                items.append({**item, "_start": start, "_end": end, "progress": min(100, max(0, item.get("progress", 0) if is_number(item.get("progress")) else 0))})
    if not items:
        return no_data()
    minimum = min(item["_start"] for item in items)
    maximum = max(item["_end"] for item in items)
    span = max(1, (maximum - minimum).days)
    x0, x1, y0 = 330, 1128, 72
    row = min(68, 340 / len(items))
    pos = lambda dt: x0 + (x1 - x0) * (dt - minimum).days / span
    parts = [text(0, 28, "07 / MILESTONE LANES", cls="index muted", size=13), evidence_plate(0, 74, "M-01", "ACTIVE", f"{sum(0 < item['progress'] < 100 for item in items)}", "进行中的任务", delay=1450, width=230), line(x0, 50, x1, 50, cls="rail-strong", extra=f'pathLength="1" {motion("align", 80)}')]
    for tick in range(6):
        x = x0 + (x1 - x0) * tick / 5
        parts += [line(x, 43, x, 420, cls="grid", extra=f'pathLength="1" {motion("align", 100 + tick * 35)}'), text(x, 35, f"D+{round(span* tick/5)}", cls="index muted", anchor="middle", size=11)]
    for index, item in enumerate(items):
        y = y0 + index * row
        start, end = pos(item["_start"]), pos(item["_end"])
        width = max(8, end - start)
        parts += [text(0, y + 19, f"{index+1:02d}", cls="index muted", size=11), text(42, y + 19, item.get("task", "任务"), size=14), line(x0, y + 12, x1, y + 12, cls="grid", extra=motion("align", 140 + index * 35)), path(cut_rect_path(start, y, width, 26, 5), cls="panel-stroke", extra=motion("dock", 320 + index * 90, dx=-24)), rect(start, y, width * item["progress"] / 100, 26, cls="signal-fill" if 0 < item["progress"] < 100 else "data-fill", extra=motion("route", 680 + index * 70)), line(end, y - 5, end, y + 34, cls="rail", extra=motion("lock", 920 + index * 55)), text(x1, y + 19, f"{item['progress']:.0f}%", cls="index muted", anchor="end", size=12)]
    return "\n".join(parts)


def build_c8(data: Any) -> str:
    items = [item for item in _valid_series(data, "stage") if item["value"] > 0][:6]
    if len(items) < 2:
        return no_data()
    maximum = max(item["value"] for item in items)
    retention = items[-1]["value"] / items[0]["value"] * 100
    losses = [1 - items[i + 1]["value"] / items[i]["value"] for i in range(len(items) - 1)]
    bottleneck = max(range(len(losses)), key=lambda i: losses[i])
    parts = [text(0, 28, "08 / STAGE INTERLOCK", cls="index muted", size=13), evidence_plate(0, 74, "S-01", "RETENTION", f"{retention:.1f}%", "首阶段至末阶段", delay=1520, width=230)]
    x0, x1, center = 302, 1130, 250
    band = (x1 - x0) / len(items)
    centers = []
    for index, item in enumerate(items):
        cx = x0 + band * (index + .5)
        height = 74 + 210 * item["value"] / maximum
        y = center - height / 2
        width = min(104, band * .66)
        centers.append((cx, y, height, width))
        cls = "signal-fill" if index == bottleneck + 1 else ("data-fill" if index == 0 else "cat-1")
        parts += [path(cut_rect_path(cx - width/2, y, width, height, 8), cls=cls, extra=motion("dock", 300 + index * 120, dx=-28)), line(cx, y - 14, cx, y + height + 14, cls="rail", extra=motion("align", 180 + index * 60)), text(cx, y - 24, item["stage"], cls="label", anchor="middle", size=14, weight=650), text(cx, y + height/2 + 6, format_num(item["value"]), cls="value", anchor="middle", size=16, weight=650)]
        if index:
            prev = centers[index - 1]
            parts.append(line(prev[0] + prev[3]/2, center, cx - width/2, center, cls="signal-stroke" if index == bottleneck + 1 else "rail", extra=f'pathLength="1" {motion("route", 680 + index * 110)}'))
            loss = 100 * (1 - item["value"] / items[index - 1]["value"])
            parts.append(text((prev[0] + cx)/2, center - 16, f"−{loss:.0f}%", cls="signal-text index" if index == bottleneck + 1 else "muted index", anchor="middle", size=11, extra=motion("lock", 1040 + index*55)))
    parts.append(line(x0, 420, x1, 420, cls="rail-strong", extra=f'pathLength="1" {motion("align", 90)}'))
    return "\n".join(parts)


def build_c9(data: Any) -> str:
    if not isinstance(data, dict) or not is_number(data.get("value")):
        return no_data()
    value, target = data["value"], data.get("target") if is_number(data.get("target")) and data.get("target") > 0 else None
    completion = value / target * 100 if target else None
    yoy = data.get("yoy")
    parts = [
        text(0, 28, "09 / METRIC LOCKUP", cls="index muted", size=13),
        path(cut_rect_path(0, 74, 680, 336, 14), cls="panel-stroke", extra=motion("dock", 280, dy=22)),
        text(34, 122, data.get("label", "核心指标"), cls="muted", size=16),
        text(34, 235, format_num(value), cls="value title-font", size=84, weight=700, extra=motion("lock", 920)),
        text(38, 275, data.get("unit", ""), cls="muted", size=18),
        line(38, 326, 622, 326, cls="rail-strong", extra=f'pathLength="1" {motion("align", 120)}'),
    ]
    if target:
        ratio = min(1, max(0, value / target))
        x = 38 + 584 * ratio
        parts += [line(38, 326, x, 326, cls="signal-stroke", extra=f'pathLength="1" {motion("route", 650, duration=680)}'), line(x, 313, x, 339, cls="signal-stroke", extra=motion("lock", 1240)), text(622, 355, f"TARGET {format_num(target)}", cls="index muted", anchor="end", size=11)]
    parts += [evidence_plate(732, 74, "K-01", "YOY", f"{yoy:+.1f}%" if is_number(yoy) else "—", "同比变化", delay=1150, width=190), evidence_plate(940, 74, "K-02", "TARGET", f"{completion:.1f}%" if completion is not None else "—", "目标完成度", delay=1280, width=190), evidence_plate(732, 192, "K-03", "MOM", f"{data.get('mom'):+.1f}%" if is_number(data.get("mom")) else "—", "环比变化", delay=1380, width=190)]
    return "\n".join(parts)


def build_c10(data: Any) -> str:
    items = _valid_series(data)[:4]
    if len(items) < 2:
        return no_data()
    hero = max(range(len(items)), key=lambda index: items[index]["value"])
    risks = [index for index, item in enumerate(items) if is_number(item.get("yoy")) and item["yoy"] < 0]
    parts = [text(0, 28, "10 / DECISION INTERFACE", cls="index muted", size=13), path(cut_rect_path(0, 66, 520, 356, 14), cls="panel-stroke", extra=motion("dock", 260, dx=-20)), text(36, 114, "LEADING REGION", cls="index muted", size=12), text(36, 158, items[hero]["label"], cls="title-font", size=30, weight=700), text(36, 265, format_num(items[hero]["value"]), cls="value title-font", size=74, weight=700, extra=motion("lock", 940)), text(40, 300, items[hero].get("unit", ""), cls="muted", size=16), line(36, 340, 474, 340, cls="rail-strong", extra=f'pathLength="1" {motion("align", 120)}')]
    if is_number(items[hero].get("yoy")):
        parts += [text(36, 382, f"YOY {items[hero]['yoy']:+.1f}%", cls="index signal-text", size=14, weight=650, extra=motion("lock", 1160)), path("M 24 78 V 56 H 46", cls="signal-stroke", extra=f'pathLength="1" {motion("lock", 1080)}')]
    x0, x1, y0 = 586, 1130, 78
    others = [item for index, item in enumerate(items) if index != hero]
    maximum = max(item["value"] for item in items) or 1
    for index, item in enumerate(others):
        y = y0 + index * 112
        ratio = max(0, item["value"]) / maximum
        is_risk = is_number(item.get("yoy")) and item["yoy"] < 0
        parts += [text(x0, y, f"{index+1:02d}", cls="index muted", size=11), text(x0 + 42, y, item["label"], size=16, weight=650), text(x1, y, format_num(item["value"]), cls="value", anchor="end", size=18, weight=650), line(x0 + 42, y + 30, x1, y + 30, cls="grid", extra=f'pathLength="1" {motion("align", 180 + index*60)}'), path(cut_rect_path(x0 + 42, y + 19, max(6, (x1-x0-42)*ratio), 22, 5), cls="signal-fill" if is_risk else "data-fill", extra=motion("dock", 430 + index*130, dx=-24)), text(x1, y + 61, f"YOY {item.get('yoy'):+.1f}%" if is_number(item.get("yoy")) else "YOY —", cls="signal-text index" if is_risk else "muted index", anchor="end", size=12, extra=motion("lock", 950 + index*80))]
    if risks:
        risk = items[risks[0]]
        parts.append(evidence_plate(586, 374, "D-01", "RISK", f"{risk.get('yoy'):+.1f}%", f"{risk['label']} / 同比", delay=1420, width=244))
    return "\n".join(parts)


BUILDERS: dict[str, Callable[[Any], str]] = {
    "C1": build_c1, "C2": build_c2, "C3": build_c3, "C4": build_c4, "C5": build_c5,
    "C6": build_c6, "C7": build_c7, "C8": build_c8, "C9": build_c9, "C10": build_c10,
}


def render_chart(
    chart_id: str,
    data: Any | None = None,
    *,
    title: str | None = None,
    subtitle: str = "单位与时间范围见图内标注 · v2 editorial mode",
    footer: str = "数据来源：Moxing 示例数据 · 口径：演示",
    surface: str = "light",
    mode: str = "editorial",
    embed_fonts: bool = False,
) -> str:
    key = chart_id.upper()
    if key not in CHARTS:
        raise KeyError(f"未知图表编号：{chart_id}")
    meta = CHARTS[key]
    source = DEFAULTS[key] if data is None else data
    page = ChartPage(
        chart_id=key,
        slug=meta["slug"],
        public_name=meta["name"],
        title=title or meta["title"],
        subtitle=subtitle,
        footer=footer,
        svg=BUILDERS[key](source),
        data=source,
        total_ms=1900 if key in {"C3", "C7", "C8"} else 1750,
        surface=surface if surface in {"light", "dark"} else "light",
        mode=mode if mode in {"brief", "editorial"} else "editorial",
    )
    return html_page(page, embed_fonts=embed_fonts)
