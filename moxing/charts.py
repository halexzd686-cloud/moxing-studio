from __future__ import annotations

from datetime import datetime
import math
from typing import Any, Callable

from .core import (
    H,
    W,
    ChartArtwork,
    ChartPage,
    DirectCanvas,
    EvidenceInterface,
    PRESENTATION_TARGETS,
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


# Charts with a top-left evidence plate reserve a dedicated annotation lane.
# Keeping plot geometry to the right of this boundary prevents axes, marks, and
# motion paths from disappearing behind the plate at any supported data density.
PLOT_LEFT_WITH_EVIDENCE = 276


def _contrast_text_class(fill_class: str) -> str:
    """Choose the readable foreground token for a filled data mark."""
    if fill_class == "signal-fill":
        return "on-signal"
    if fill_class == "data-fill" or fill_class.startswith("cat-"):
        return "on-fill"
    return "value"


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
    "C11": [
        {"label": "服饰", "value": 38}, {"label": "美妆", "value": 27},
        {"label": "家居", "value": 19}, {"label": "其他", "value": 16},
    ],
    "C12": {
        "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "series": [
            {"name": "GMV", "unit": "万元", "values": [820, 910, 880, 1120, 1260, 1480]},
            {"name": "订单", "unit": "单", "values": [4200, 4480, 4390, 5160, 5620, 6310]},
            {"name": "客单价", "unit": "元", "values": [195, 203, 200, 217, 224, 235]},
            {"name": "退款率", "unit": "%", "values": [8.4, 7.9, 8.1, 7.2, 6.8, 6.3]},
        ],
    },
    "C13": [
        {"label": "SKU-01", "value": 286}, {"label": "SKU-02", "value": 214},
        {"label": "SKU-03", "value": 156}, {"label": "SKU-04", "value": 102},
        {"label": "SKU-05", "value": 74}, {"label": "SKU-06", "value": 48},
    ],
    "C14": {
        "columns": ["首月", "M+1", "M+2", "M+3", "M+4", "M+5"],
        "rows": [
            {"label": "2026-01", "values": [100, 42, 31, 26, 22, 19]},
            {"label": "2026-02", "values": [100, 46, 34, 28, 24]},
            {"label": "2026-03", "values": [100, 44, 35, 30]},
            {"label": "2026-04", "values": [100, 49, 38]},
            {"label": "2026-05", "values": [100, 52]},
        ],
    },
    "C15": {
        "nodes": [
            {"id": "search", "label": "搜索", "level": 0, "value": 5200},
            {"id": "social", "label": "内容", "level": 0, "value": 3900},
            {"id": "detail", "label": "商品详情", "level": 1, "value": 6100},
            {"id": "cart", "label": "加购", "level": 2, "value": 2840},
            {"id": "buy", "label": "成交", "level": 3, "value": 1710},
        ],
        "links": [
            {"source": "search", "target": "detail", "value": 3600},
            {"source": "social", "target": "detail", "value": 2500},
            {"source": "detail", "target": "cart", "value": 2840},
            {"source": "cart", "target": "buy", "value": 1710},
        ],
    },
    "C16": [
        {"label": "爆款 A", "x": 82, "y": 6.8, "size": 920},
        {"label": "潜力 B", "x": 61, "y": 7.6, "size": 520},
        {"label": "引流 C", "x": 88, "y": 3.1, "size": 680},
        {"label": "观察 D", "x": 43, "y": 4.2, "size": 310},
        {"label": "长尾 E", "x": 27, "y": 2.4, "size": 180},
    ],
    "C17": [
        {"date": "08-12", "open": 102, "high": 108, "low": 99, "close": 106, "volume": 38},
        {"date": "08-13", "open": 106, "high": 110, "low": 103, "close": 104, "volume": 44},
        {"date": "08-14", "open": 104, "high": 112, "low": 103, "close": 111, "volume": 62},
        {"date": "08-15", "open": 111, "high": 115, "low": 108, "close": 113, "volume": 51},
        {"date": "08-16", "open": 113, "high": 114, "low": 106, "close": 108, "volume": 70},
        {"date": "08-17", "open": 108, "high": 117, "low": 107, "close": 116, "volume": 83},
        {"date": "08-18", "open": 116, "high": 121, "low": 114, "close": 119, "volume": 76},
    ],
    "C18": {
        "labels": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月"],
        "values": [100, 106, 111, 104, 108, 116, 113, 121, 127, 132],
    },
    "C19": {
        "maturities": ["1M", "3M", "6M", "1Y", "2Y", "5Y", "10Y", "30Y"],
        "series": [
            {"name": "当前", "values": [1.58, 1.62, 1.70, 1.82, 2.01, 2.28, 2.46, 2.61]},
            {"name": "一月前", "values": [1.66, 1.69, 1.73, 1.78, 1.91, 2.15, 2.34, 2.52]},
        ],
    },
    "C20": {
        "rows": ["毛利率 32%", "毛利率 34%", "毛利率 36%", "毛利率 38%", "毛利率 40%"],
        "columns": ["增长 4%", "增长 6%", "增长 8%", "增长 10%", "增长 12%"],
        "values": [[72, 78, 85, 93, 102], [79, 86, 94, 103, 113], [87, 95, 104, 114, 125], [96, 105, 115, 126, 138], [106, 116, 127, 139, 152]],
    },
    "C21": [12, 14, 15, 15, 16, 17, 18, 18, 19, 19, 20, 21, 22, 22, 23, 24, 25, 27, 29, 34, 41],
    "C22": {
        "labels": ["营收", "毛利", "投放", "客单", "复购"],
        "values": [[1, .84, .62, .48, .55], [.84, 1, .41, .57, .63], [.62, .41, 1, -.18, -.24], [.48, .57, -.18, 1, .36], [.55, .63, -.24, .36, 1]],
    },
    "C23": {
        "labels": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月"],
        "actual": [82, 88, 91, 96, 103, 109],
        "forecast": [109, 116, 123, 131, 138],
        "lower": [109, 109, 111, 114, 116],
        "upper": [109, 123, 136, 149, 162],
    },
    "C24": {
        "labels": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
        "values": [51, 48, 53, 49, 52, 55, 47, 54, 58, 50, 52, 63],
        "center": 52, "ucl": 60, "lcl": 44,
    },
}


CHARTS = {
    "C1": {"slug": "structural-rank", "name": "Structural Rank", "title": "华东规模领先，优势来自稳定增长", "family": "RANK", "state": "LEADER.LOCK"},
    "C2": {"slug": "ranked-rail", "name": "Ranked Rail", "title": "华东服务评分居首，区域差距仍可控", "family": "RANK", "state": "TOP.LOCK"},
    "C3": {"slug": "signal-trend", "name": "Signal Trend", "title": "增长在下半年加速，年末达到新高", "family": "ROUTE", "state": "TRACE.LOCK"},
    "C4": {"slug": "composition-field", "name": "Composition Field", "title": "自然搜索贡献最大，前三渠道占比达 86%", "family": "FIELD", "state": "SHARE.LOCK"},
    "C5": {"slug": "composition-bands", "name": "Composition Bands", "title": "产品 A 持续扩张，结构集中度提高", "family": "BAND", "state": "MIX.LOCK"},
    "C6": {"slug": "ledger-steps", "name": "Ledger Steps", "title": "新增和续约抵消流失，期末净增 160", "family": "LEDGER", "state": "NET.LOCK"},
    "C7": {"slug": "milestone-lanes", "name": "Milestone Lanes", "title": "核心开发进入中段，测试窗口即将开启", "family": "TIMELINE", "state": "ACTIVE.LOCK"},
    "C8": {"slug": "stage-channel", "name": "Stage Channel", "title": "付费转化是主瓶颈，续约质量相对稳定", "family": "STAGE", "state": "BOTTLENECK"},
    "C9": {"slug": "metric-lockup", "name": "Metric Lockup", "title": "经常性收入同比增长 23.8%，完成目标 85.7%", "family": "METRIC", "state": "TARGET.LOCK"},
    "C10": {"slug": "decision-interface", "name": "Decision Interface", "title": "华东营收领先，华南是唯一同比下滑区域", "family": "DECISION", "state": "RISK.LOCK"},
    "C11": {"slug": "sector-lock", "name": "Sector Lock", "title": "服饰贡献近四成，是当前结构的核心支点", "family": "SECTOR", "state": "LEADER.LOCK"},
    "C12": {"slug": "metric-small-multiples", "name": "Metric Small Multiples", "title": "增长质量同步改善，规模提升并未推高退款率", "family": "METRIC", "state": "PULSE.READY"},
    "C13": {"slug": "pareto-contribution", "name": "Pareto Contribution", "title": "前三款商品贡献近四分之三，应优先保障供给", "family": "PARETO", "state": "THRESHOLD"},
    "C14": {"slug": "cohort-matrix", "name": "Cohort Matrix", "title": "新客次月复购持续改善，五月队列达到 52%", "family": "COHORT", "state": "BEST.LOCK"},
    "C15": {"slug": "commerce-flow", "name": "Commerce Flow", "title": "商品详情到加购流失最大，是成交链路首要修复点", "family": "PORT", "state": "LEAK.LOCK"},
    "C16": {"slug": "decision-bubble-matrix", "name": "Decision Bubble Matrix", "title": "爆款 A 兼具高流量与高转化，应扩大资源投入", "family": "QUADRANT", "state": "PRIORITY"},
    "C17": {"slug": "market-candles", "name": "Market Candles", "title": "价格放量突破前高，短期趋势转强", "family": "MARKET", "state": "CHANGE.LOCK"},
    "C18": {"slug": "performance-drawdown", "name": "Performance Drawdown", "title": "累计收益创新高，最大回撤控制在 6.3%", "family": "RISK", "state": "DRAWDOWN"},
    "C19": {"slug": "yield-curve", "name": "Yield Curve", "title": "曲线整体上移且保持陡峭，期限溢价继续扩张", "family": "CURVE", "state": "SLOPE.LOCK"},
    "C20": {"slug": "sensitivity-matrix", "name": "Sensitivity Matrix", "title": "增长与毛利率同时改善时，估值弹性显著放大", "family": "MATRIX", "state": "UPSIDE.LOCK"},
    "C21": {"slug": "distribution-profile", "name": "Distribution Profile", "title": "数据主体集中在 15–25，右侧长尾需要单独核查", "family": "DISTRIBUTION", "state": "MEDIAN.LOCK"},
    "C22": {"slug": "correlation-matrix", "name": "Correlation Matrix", "title": "营收与毛利高度同向，投放与复购呈弱负相关", "family": "MATRIX", "state": "PAIR.LOCK"},
    "C23": {"slug": "forecast-fan", "name": "Forecast Fan", "title": "基准预测继续增长，远期区间明显扩大", "family": "FORECAST", "state": "RANGE.LOCK"},
    "C24": {"slug": "control-chart", "name": "Control Chart", "title": "第十二期突破控制上限，应立即排查特殊原因", "family": "CONTROL", "state": "ALARM.LOCK"},
}

CHOREOGRAPHIES = {
    "C1": "rail-rise",
    "C2": "ranked-rail",
    "C3": "path-trace",
    "C4": "field-aggregation",
    "C5": "band-routing",
    "C6": "ledger-interlock",
    "C7": "milestone-routing",
    "C8": "stage-interlock",
    "C9": "metric-readout",
    "C10": "decision-readout",
    "C11": "sector-lock", "C12": "metric-pulse", "C13": "pareto-routing", "C14": "cohort-seating",
    "C15": "flow-routing", "C16": "quadrant-lock", "C17": "market-build", "C18": "drawdown-routing",
    "C19": "curve-routing", "C20": "matrix-seating", "C21": "distribution-build", "C22": "matrix-seating",
    "C23": "forecast-routing", "C24": "control-lock",
}

PROFILE_TOTALS = {
    "C1": {"brief": 1100, "standard": 1750, "story": 3000},
    "C2": {"brief": 1100, "standard": 1800, "story": 3400},
    "C3": {"brief": 1200, "standard": 1900, "story": 3200},
    "C4": {"brief": 1100, "standard": 1900, "story": 3600},
    "C5": {"brief": 1200, "standard": 2200, "story": 4000},
    "C6": {"brief": 1200, "standard": 2200, "story": 4000},
    "C7": {"brief": 1200, "standard": 2100, "story": 4000},
    "C8": {"brief": 1200, "standard": 2100, "story": 3500},
    "C9": {"brief": 1100, "standard": 1800, "story": 3000},
    "C10": {"brief": 1100, "standard": 1800, "story": 3200},
    "C11": {"brief": 1100, "standard": 1850, "story": 3300},
    "C12": {"brief": 1200, "standard": 2100, "story": 3800},
    "C13": {"brief": 1200, "standard": 2100, "story": 3900},
    "C14": {"brief": 1200, "standard": 2200, "story": 4100},
    "C15": {"brief": 1200, "standard": 2200, "story": 4100},
    "C16": {"brief": 1100, "standard": 1900, "story": 3500},
    "C17": {"brief": 1200, "standard": 2100, "story": 3900},
    "C18": {"brief": 1200, "standard": 2100, "story": 3900},
    "C19": {"brief": 1100, "standard": 1900, "story": 3500},
    "C20": {"brief": 1200, "standard": 2200, "story": 4100},
    "C21": {"brief": 1100, "standard": 1900, "story": 3500},
    "C22": {"brief": 1200, "standard": 2200, "story": 4100},
    "C23": {"brief": 1200, "standard": 2100, "story": 3900},
    "C24": {"brief": 1100, "standard": 1900, "story": 3500},
}


def _valid_series(data: Any, label_key: str = "label") -> list[dict[str, Any]]:
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict) and is_number(item.get("value")) and str(item.get(label_key, "")).strip()]


def build_c1(data: Any) -> str | ChartArtwork:
    items = _valid_series(data)[:10]
    if not items:
        return no_data()
    max_value = max(max(item["value"], 0) for item in items) or 1
    top = max(range(len(items)), key=lambda index: items[index]["value"])
    x0, x1, baseline, grid_top = 92, 1128, 424, 124

    raw_step = max_value / 3
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude
    step = next(candidate for candidate in (1, 1.5, 2, 2.5, 4, 5, 10) if normalized <= candidate) * magnitude
    axis_max = step * 3

    field_parts = [
        text(0, 28, "01 / DIRECT RANK FIELD", cls="index muted", size=12),
        line(x0, baseline, x1, baseline, cls="rail-strong", extra=f'pathLength="1" {motion("align", 80, brief=40, story=120, duration=240, duration_brief=150, duration_story=320)}'),
    ]
    for tick in range(4):
        y = baseline - (baseline - grid_top) * tick / 3
        if tick:
            field_parts.append(line(x0, y, x1, y, cls="grid", extra=motion("align", 110 + tick * 40, brief=60 + tick * 22, story=170 + tick * 60)))
        field_parts.append(text(74, y + 4, format_num(step * tick), cls="index muted", anchor="end", size=12))

    center_start, center_end = 212, 980
    if len(items) == 1:
        centers_x = [(center_start + center_end) / 2]
        width = 128
    else:
        spacing = (center_end - center_start) / (len(items) - 1)
        centers_x = [center_start + spacing * index for index in range(len(items))]
        width = min(128, spacing * .67)

    plot_parts: list[str] = []
    centers: list[tuple[float, float]] = []
    for index, item in enumerate(items):
        height = max(2, max(0, item["value"]) / axis_max * (baseline - grid_top))
        x = centers_x[index] - width / 2
        y = baseline - height
        cls = "signal-fill" if index == top else ("data-fill" if index <= 1 else f"cat-{min(3, index - 1)}")
        centers.append((x + width / 2, y))
        shape = path(cut_rect_path(x, y, width, height, 7), cls=cls, extra=motion("dock", 320 + index * 95, dy=42, brief=170 + index * 52, story=520 + index * 160, duration=520, duration_brief=340, duration_story=760, choreo="rail-rise"))
        if height >= 46:
            value_y = min(baseline - 12, y + 37)
            value_cls = f"value {_contrast_text_class(cls)}"
        else:
            value_y = y - 10
            value_cls = "value"
        plot_parts += [
            shape,
            text(x + width / 2, value_y, format_num(item["value"]), cls=value_cls, anchor="middle", size=15, weight=700, extra=motion("lock", 930 + index * 52, brief=520 + index * 32, story=1540 + index * 118, choreo="readout")),
            text(x + width / 2, 460, item["label"], cls="muted", anchor="middle", size=13),
        ]

    target_x, target_y = centers[top]
    target_left = target_x - width / 2
    target_right = target_x + width / 2
    target_height = baseline - target_y
    bracket_y = round(max(56, target_y - (52 if target_height < 46 else 28)), 2)
    lock_parts = [
        rect(target_x - 8, baseline - 8, 16, 16, cls="pm-socket-signal"),
        path(f"M {target_left-17} {bracket_y+19} V {bracket_y} H {target_left+2} M {target_right-2} {bracket_y} H {target_right+17} V {bracket_y+19}", cls="pm-focus-corner"),
        text(target_x, bracket_y - 15, f"R{top + 1:02d} / {format_num(items[top]['value'])}", cls="pm-address pm-address-signal", anchor="middle", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(field_parts),
        presentation=DirectCanvas(
            foreground_svg="\n".join(lock_parts),
            plot_svg="\n".join(plot_parts),
            lock_delay=1080,
            lock_delay_brief=700,
            lock_delay_story=1500,
            compiled_motion=True,
        ),
    )


def build_c2(data: Any) -> str | ChartArtwork:
    items = sorted(_valid_series(data), key=lambda item: item["value"], reverse=True)[:10]
    if not items:
        return no_data()
    maximum = max(max(item["value"], 0) for item in items) or 1
    x0, x1, y0 = 330, 1116, 120
    row = min(58, 306 / max(1, len(items) - 1))
    parts = []
    ends: list[tuple[float, float]] = []
    for index, item in enumerate(items):
        y = y0 + index * row
        end = x0 + (x1 - x0) * max(0, item["value"]) / maximum
        ends.append((end, y + 12))
        heading = group(
            [
                text(0, y + 18, f"{index + 1:02d}", cls="index muted", size=12),
                text(44, y + 18, item["label"], cls="label", size=14, weight=600 if index == 0 else None),
            ],
            cls="rank-heading",
            extra=motion("lock", 120 + index * 45, brief=60 + index * 25, story=200 + index * 90, choreo="readout"),
        )
        bar_standard = 280 + index * 75
        bar_brief = 150 + index * 40
        bar_story = 500 + index * 150
        parts += [
            heading,
            line(x0, y + 12, x1, y + 12, cls="grid", extra=f'pathLength="1" {motion("align", 80 + index * 35, brief=35 + index * 18, story=120 + index * 65)}'),
            path(cut_rect_path(x0, y, max(4, end - x0), 24, 5), cls="signal-fill" if index == 0 else "data-fill", extra=motion("dock", bar_standard, dx=-32, brief=bar_brief, story=bar_story, duration=420, duration_brief=280, duration_story=620, choreo="rail-slide")),
            line(end, y - 5, end, y + 30, cls="rail", extra=motion("align", bar_standard + 350, brief=bar_brief + 230, story=bar_story + 540)),
            text(min(x1 - 2, end + 12), y + 18, format_num(item["value"]), cls="value", size=14, weight=650, extra=motion("lock", bar_standard + 360, brief=bar_brief + 235, story=bar_story + 550, choreo="readout")),
        ]
    overlay = []
    for index, (_end, cy) in enumerate(ends):
        overlay.append(rect(x0 - 4, cy - 4, 8, 8, cls="pm-socket-signal" if index == 0 else "pm-socket"))
    target_x, target_y = ends[0]
    lock_y = target_y - 30
    overlay += [
        circle(target_x, lock_y, 13, cls="pm-lock-ring"),
        path(f"M {target_x} {lock_y+13} V {target_y-5}", cls="pm-lock-cross"),
        text(min(x1 - 18, target_x - 18), lock_y - 18, "R01 / TOP", cls="pm-address pm-address-signal", anchor="end", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=DirectCanvas(foreground_svg="\n".join(overlay), lock_delay=1120, lock_delay_brief=680, lock_delay_story=2100, compiled_motion=True),
    )


def build_c3(data: Any) -> str | ChartArtwork:
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
    evidence = evidence_plate(0, 74, "T-01", "LATEST", format_num(latest), f"{series[0]['name']} / {labels[-1]}", delay=1540, width=230, brief=1020, story=2820, choreo="readout")
    parts = [text(0, 28, "03 / PATH ROUTING", cls="index muted", size=13)]
    for tick in range(5):
        yy = y0 + (y1 - y0) * tick / 4
        value = y_max - (y_max - y_min) * tick / 4
        parts += [line(x0, yy, x1, yy, cls="grid", extra=f'pathLength="1" {motion("align", 70 + tick * 35, brief=40 + tick * 18, story=120 + tick * 55)}'), text(x0 - 14, yy + 4, format_num(value), cls="muted index", anchor="end", size=12)]
    step = max(1, len(labels) // 6)
    for index in range(0, len(labels), step):
        parts.append(text(x(index), y1 + 32, labels[index], cls="muted", anchor="middle", size=12))
    for series_index, item in enumerate(series):
        d = " ".join(("M" if index == 0 else "L") + f" {x(index):.2f} {y(value):.2f}" for index, value in enumerate(item["values"]))
        cls = "signal-stroke" if series_index == 0 else "secondary-stroke"
        route_start = 360 + series_index * 120
        route_brief = 180 + series_index * 80
        route_story = 650 + series_index * 180
        parts.append(path(d, cls=cls, extra=f'pathLength="1" {motion("route", route_start, duration=800, brief=route_brief, story=route_story, duration_brief=600, duration_story=1250, choreo="trace")}'))
        for index, value in enumerate(item["values"]):
            if index in {0, len(labels) - 1, peak_index} or (series_index == 0 and index % max(1, len(labels)//5) == 0):
                point_cls = "signal-fill" if series_index == 0 and index in {peak_index, len(labels)-1} else "hollow"
                progress = index / max(1, len(labels) - 1)
                parts.append(circle(x(index), y(value), 4.5 if series_index == 0 else 3.5, cls=point_cls, extra=motion("dock", round(route_start + progress * 800), dy=10, brief=round(route_brief + progress * 600), story=round(route_story + progress * 1250), duration=220, duration_brief=150, duration_story=260, choreo="pin")))
    px, py = x(peak_index), y(series[0]["values"][peak_index])
    parts += [line(px, py - 12, px, y0, cls="rail", extra=f'pathLength="1" {motion("align", 1220, brief=820, story=2140)}'), text(px, y0 - 10, f"PEAK / {labels[peak_index]}", cls="index signal-text", anchor="middle", size=12, extra=motion("lock", 1400, brief=950, story=2480, choreo="alarm"))]
    first_y = y(series[0]["values"][0])
    latest_y = y(latest)
    foreground = "\n".join([
        rect(x0 - 6, first_y - 6, 12, 12, cls="pi-socket", extra='style="--pi-delay:180ms"'),
        circle(x1, latest_y, 14, cls="pi-lock-ring"),
        path(f"M {x1-20} {latest_y} H {x1-12} M {x1+12} {latest_y} H {x1+20} M {x1} {latest_y-20} V {latest_y-12}", cls="pi-lock-cross"),
        text(x1 - 21, latest_y + 27, f"E03 / T{len(labels):02d}", cls="pi-address pi-address-signal", anchor="end", size=10),
    ])
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=EvidenceInterface("E03", "0 64 230 114", 248, 1280, evidence, foreground),
    )


def build_c4(data: Any) -> str | ChartArtwork:
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
    parts = []
    start_x, start_y, cell_w, cell_h, gap = 92, 116, 34, 48, 6
    cumulative = []
    for idx, count in enumerate(counts):
        cumulative.extend([idx] * count)
    for index in range(units):
        row, col = divmod(index, 10)
        x, y = start_x + col * (cell_w + gap), start_y + row * (cell_h + gap)
        category = cumulative[index]
        cls = "signal-fill" if category == largest else f"cat-{category % 4 + 1}"
        parts.append(path(cut_rect_path(x, y, cell_w, cell_h, 5), cls=cls, extra=motion("dock", 240 + index * 18, dy=18, brief=120 + index * 10, story=400 + index * 35, duration=360, duration_brief=240, duration_story=520, choreo="field-seat")))
        parts.append(line(x + cell_w / 2, y + cell_h, x + cell_w / 2, y + cell_h + 5, cls="grid", extra=motion("align", 500 + index * 10, brief=300 + index * 5, story=850 + index * 20)))
    legend_x = 688
    for index, item in enumerate(items):
        y = 108 + index * 58
        cls = "signal-fill" if index == largest else f"cat-{index % 4 + 1}"
        legend = group(
            [rect(legend_x, y, 12, 24, cls=cls), text(legend_x + 28, y + 15, item["label"], size=14), text(1118, y + 15, f"{shares[index]*100:.1f}%", cls="value index", anchor="end", size=14, weight=650)],
            cls="field-legend",
            extra=motion("lock", 980 + index * 80, brief=600 + index * 45, story=2080 + index * 150, choreo="readout"),
        )
        parts.append(legend)
    parts += [line(start_x, 382, start_x + 394, 382, cls="rail-strong", extra=f'pathLength="1" {motion("align", 100, brief=45, story=140)}'), text(start_x, 410, "40 MODULES / EACH = 2.5%", cls="index muted", size=12)]
    last_dominant = max(0, sum(counts[:largest + 1]) - 1)
    focus_row, focus_col = divmod(last_dominant, 10)
    focus_x = start_x + focus_col * (cell_w + gap)
    focus_y = start_y + focus_row * (cell_h + gap)
    left, right, top_y, bottom = focus_x - 2, focus_x + cell_w + 2, focus_y - 2, focus_y + cell_h + 2
    arm = 10
    focus_path = (
        f"M {left} {top_y+arm} V {top_y} H {left+arm} "
        f"M {right-arm} {top_y} H {right} V {top_y+arm} "
        f"M {right} {bottom-arm} V {bottom} H {right-arm} "
        f"M {left+arm} {bottom} H {left} V {bottom-arm}"
    )
    foreground = "\n".join([
        rect(start_x - 4, 378, 8, 8, cls="pm-socket"),
        path(focus_path, cls="pm-focus-corner"),
        text(legend_x - 38, 410, f"F{counts[largest]:02d} / LEADER", cls="pm-address pm-address-signal", size=10, anchor="end"),
    ])
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=DirectCanvas(foreground_svg=foreground, lock_delay=1080, lock_delay_brief=650, lock_delay_story=2050, compiled_motion=True),
    )


def build_c5(data: Any) -> str | ChartArtwork:
    categories = data.get("categories", []) if isinstance(data, dict) else []
    series = data.get("series", [])[:4] if isinstance(data, dict) else []
    valid = bool(categories) and series and all(len(item.get("values", [])) == len(categories) and all(is_number(v) and v >= 0 for v in item.get("values", [])) for item in series)
    if not valid:
        return no_data()
    totals = [sum(item["values"][i] for item in series) for i in range(len(categories))]
    if not any(totals):
        return no_data()
    category_span = max(1, len(categories) - 1)
    standard_step = min(130, 900 / category_span)
    brief_step = min(70, 450 / category_span)
    story_step = min(240, 1600 / category_span)
    parts = []
    x0, x1, y0 = 156, 1122, 95
    row = min(78, 320 / max(1, len(categories)))
    for cat_index, category in enumerate(categories):
        y = y0 + cat_index * row
        total = totals[cat_index] or 1
        row_standard = round(120 + cat_index * standard_step * .55)
        row_brief = round(55 + cat_index * brief_step * .45)
        row_story = round(180 + cat_index * story_step * .55)
        parts += [text(x0 - 20, y + 23, category, cls="muted", anchor="end", size=13, extra=motion("lock", row_standard, brief=row_brief, story=row_story, choreo="readout")), line(x0, y + 31, x1, y + 31, cls="grid", extra=f'pathLength="1" {motion("align", row_standard, brief=row_brief, story=row_story)}')]
        cursor = x0
        for series_index, item in enumerate(series):
            width = (x1 - x0) * item["values"][cat_index] / total
            cls = "signal-fill" if series_index == 0 else f"cat-{series_index + 1}"
            segment_standard = round(280 + cat_index * standard_step + series_index * 70)
            segment_brief = round(150 + cat_index * brief_step + series_index * 40)
            segment_story = round(700 + cat_index * story_step + series_index * 120)
            parts.append(path(cut_rect_path(cursor, y, max(1, width - 4), 42, 5), cls=cls, extra=motion("dock", segment_standard, dx=-18, brief=segment_brief, story=segment_story, duration=420, duration_brief=280, duration_story=620, choreo="band-fill")))
            if width > 74:
                parts.append(text(cursor + width / 2, y + 26, f"{item['values'][cat_index]/total*100:.0f}%", cls=f"index {_contrast_text_class(cls)}", anchor="middle", size=12, weight=700, extra=motion("lock", segment_standard + 300, brief=segment_brief + 190, story=segment_story + 470, choreo="readout")))
            cursor += width
    for index, item in enumerate(series):
        x = x0 + index * 190
        parts.append(group([rect(x, 442, 12, 12, cls="signal-fill" if index == 0 else f"cat-{index+1}"), text(x + 22, 453, item.get("name", f"系列{index+1}"), cls="muted", size=12)], cls="band-legend", extra=motion("lock", 1180 + index * 70, brief=700 + index * 40, story=2500 + index * 140, choreo="readout")))
    latest_y = y0 + (len(categories) - 1) * row
    primary_end = x0 + (x1 - x0) * series[0]["values"][-1] / max(1, totals[-1])
    overlay = []
    for index in range(len(categories)):
        cy = y0 + index * row + 21
        overlay.append(rect(x0 - 4, cy - 4, 8, 8, cls="pm-socket-signal" if index == len(categories) - 1 else "pm-socket"))
    overlay += [
        circle(primary_end, latest_y + 21, 13, cls="pm-lock-ring"),
        text(primary_end, latest_y - 3, f"Q{len(categories):02d} / LATEST MIX", cls="pm-address pm-address-signal", anchor="middle", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=DirectCanvas(foreground_svg="\n".join(overlay), lock_delay=1160, lock_delay_brief=700, lock_delay_story=2400, compiled_motion=True),
    )


def build_c6(data: Any) -> str | ChartArtwork:
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
    extra_steps = max(0, len(items) - 6)
    evidence = evidence_plate(0, 74, "L-01", "NET", f"{final_delta:+,.0f}", "期初至期末", delay=1750 + extra_steps * 50, width=230, brief=950 + extra_steps * 25, story=3300 + extra_steps * 100, choreo="alarm")
    parts = [line(x0, y(0), x1, y(0), cls="rail-strong", extra=f'pathLength="1" {motion("align", 80, brief=35, story=120)}')]
    centers: list[tuple[float, float, float]] = []
    for index, (item, pair) in enumerate(zip(items, levels)):
        start, end = pair
        top, bottom = min(y(start), y(end)), max(y(start), y(end))
        height = max(4, bottom - top)
        x = x0 + band * index + (band - width) / 2
        kind = item.get("type", "increase")
        cls = "signal-fill" if kind == "decrease" else ("data-fill" if kind in {"start", "end"} else "cat-1")
        centers.append((x + width / 2, top, bottom))
        stage_standard = 220 if index == 0 else 620 + (index - 1) * 150
        stage_brief = 90 if index == 0 else 350 + (index - 1) * 80
        stage_story = 360 if index == 0 else 1100 + (index - 1) * 300
        parts += [path(cut_rect_path(x, top, width, height, 6), cls=cls, extra=motion("dock", stage_standard, dy=26, brief=stage_brief, story=stage_story, duration=320, duration_brief=220, duration_story=540, choreo="field-seat")), text(x + width / 2, top - 12, format_num(item["value"]), cls="value", anchor="middle", size=14, weight=650, extra=motion("lock", stage_standard + 260, brief=stage_brief + 170, story=stage_story + 430, choreo="readout")), text(x + width / 2, y1 + 34, item["label"], cls="muted", anchor="middle", size=12, extra=motion("lock", stage_standard, brief=stage_brief, story=stage_story, choreo="readout"))]
        if index < len(items) - 1:
            next_x = x0 + band * (index + 1) + (band - width) / 2
            parts.append(line(x + width, y(end), next_x, y(end), cls="rail", extra=f'pathLength="1" {motion("route", 450 + index * 150, brief=240 + index * 80, story=780 + index * 300, duration=190, duration_brief=140, duration_story=360, choreo="trace")}'))
    overlay = []
    for index, (cx, _top, bottom) in enumerate(centers):
        overlay.append(rect(cx - 4, bottom - 4, 8, 8, cls="pi-socket-signal" if index == len(centers) - 1 else "pi-socket"))
    target_x, target_top, _target_bottom = centers[-1]
    target_edge = target_x + width / 2
    lock_x = target_edge + 30
    lock_y = target_top - 34
    overlay += [
        circle(lock_x, lock_y, 13, cls="pi-lock-ring"),
        path(f"M {lock_x} {lock_y+13} V {target_top-5} H {target_edge}", cls="pi-lock-cross"),
        text(lock_x, lock_y - 19, "E06 / NET", cls="pi-address pi-address-signal", anchor="middle", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=EvidenceInterface("E06", "0 64 230 114", 260, 1160, evidence, "\n".join(overlay)),
    )


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


def build_c7(data: Any) -> str | ChartArtwork:
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
    x0, x1, y0 = 330, 1128, 136
    row = min(62, 300 / max(1, len(items) - 1))
    pos = lambda dt: x0 + (x1 - x0) * (dt - minimum).days / span
    active_indices = [index for index, item in enumerate(items) if 0 < item["progress"] < 100]
    parts = [line(x0, 110, x1, 110, cls="rail-strong", extra=f'pathLength="1" {motion("align", 80, brief=35, story=120)}')]
    progress_points: list[tuple[float, float]] = []
    for tick in range(6):
        x = x0 + (x1 - x0) * tick / 5
        parts += [line(x, 103, x, 460, cls="grid", extra=f'pathLength="1" {motion("align", 100 + tick * 35, brief=45 + tick * 18, story=160 + tick * 55)}'), text(x, 95, f"D+{round(span* tick/5)}", cls="index muted", anchor="middle", size=12)]
    for index, item in enumerate(items):
        y = y0 + index * row
        start, end = pos(item["_start"]), pos(item["_end"])
        width = max(8, end - start)
        task_standard = 360 + index * 100
        task_brief = 180 + index * 55
        task_story = 700 + index * 210
        progress_points.append((start + width * item["progress"] / 100, y + 13))
        heading = group([text(244, y + 19, f"{index+1:02d}", cls="index muted", anchor="end", size=12), text(258, y + 19, item.get("task", "任务"), size=14), text(x1, y + 19, f"{item['progress']:.0f}%", cls="index muted", anchor="end", size=12)], cls="milestone-heading", extra=motion("lock", 240 + index * 50, brief=120 + index * 25, story=420 + index * 95, choreo="readout"))
        parts += [heading, line(x0, y + 12, x1, y + 12, cls="grid", extra=motion("align", 140 + index * 35, brief=70 + index * 18, story=220 + index * 70)), path(cut_rect_path(start, y, width, 26, 5), cls="panel-stroke", extra=motion("dock", task_standard, dx=-24, brief=task_brief, story=task_story, duration=350, duration_brief=220, duration_story=540, choreo="interlock")), rect(start, y, width * item["progress"] / 100, 26, cls="signal-fill" if 0 < item["progress"] < 100 else "data-fill", extra=motion("route", task_standard + 250, brief=task_brief + 150, story=task_story + 390, duration=320, duration_brief=220, duration_story=600, choreo="band-fill")), line(end, y - 5, end, y + 34, cls="rail", extra=motion("lock", task_standard + 500, brief=task_brief + 300, story=task_story + 780, choreo="readout"))]
    focus_index = min(active_indices, key=lambda index: abs(items[index]["progress"] - 50)) if active_indices else max(0, len(items) - 1)
    target_x, target_y = progress_points[focus_index]
    overlay = []
    for index, item in enumerate(items):
        socket_x = pos(item["_start"])
        socket_y = y0 + index * row + 13
        overlay.append(rect(socket_x - 4, socket_y - 4, 8, 8, cls="pm-socket-signal" if index == focus_index else "pm-socket"))
    overlay += [
        circle(target_x, target_y, 13, cls="pm-lock-ring"),
        text(target_x, target_y - 22, f"M{focus_index + 1:02d} / ACTIVE", cls="pm-address pm-address-signal", anchor="middle", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=DirectCanvas(foreground_svg="\n".join(overlay), lock_delay=1140, lock_delay_brief=680, lock_delay_story=2300, compiled_motion=True),
    )


def build_c8(data: Any) -> str | ChartArtwork:
    items = [item for item in _valid_series(data, "stage") if item["value"] > 0][:6]
    if len(items) < 2:
        return no_data()
    maximum = max(item["value"] for item in items)
    retention = items[-1]["value"] / items[0]["value"] * 100
    losses = [1 - items[i + 1]["value"] / items[i]["value"] for i in range(len(items) - 1)]
    bottleneck = max(range(len(losses)), key=lambda i: losses[i])
    plate_standard = 1600 + max(0, len(items) - 5) * 170
    plate_brief = 960 + max(0, len(items) - 5) * 80
    plate_story = 3040 + max(0, len(items) - 5) * 320
    evidence = evidence_plate(0, 74, "S-01", "RETENTION", f"{retention:.1f}%", "首阶段至末阶段", delay=plate_standard, width=230, brief=plate_brief, story=plate_story, choreo="readout")
    parts = [text(0, 28, "08 / STAGE INTERLOCK", cls="index muted", size=13)]
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
        stage_standard = 220 if index == 0 else 560 + (index - 1) * 190
        stage_brief = 90 if index == 0 else 340 + (index - 1) * 110
        stage_story = 360 if index == 0 else 1080 + (index - 1) * 400
        stage_module = group(
            [
                path(cut_rect_path(cx - width/2, y, width, height, 8), cls=cls),
                text(cx, y - 24, item["stage"], cls="label", anchor="middle", size=14, weight=650),
                text(cx, y + height/2 + 6, format_num(item["value"]), cls=f"value {_contrast_text_class(cls)}", anchor="middle", size=16, weight=650),
            ],
            cls="stage-module",
            extra=motion("dock", stage_standard, dx=-34, brief=stage_brief, story=stage_story, duration=320, duration_brief=220, duration_story=540, choreo="interlock"),
        )
        # Datum rails sit below the stage blocks so they never cut through values.
        parts += [line(cx, y - 14, cx, y + height + 14, cls="rail pi-stage-axis", extra=motion("align", 130 + index * 50, brief=45 + index * 24, story=160 + index * 95)), stage_module]
        if index:
            prev = centers[index - 1]
            connector_standard = 440 + (index - 1) * 190
            connector_brief = 240 + (index - 1) * 110
            connector_story = 780 + (index - 1) * 400
            parts.append(line(prev[0] + prev[3]/2, center, cx - width/2, center, cls="signal-stroke" if index == bottleneck + 1 else "rail", extra=f'pathLength="1" {motion("route", connector_standard, brief=connector_brief, story=connector_story, duration=180, duration_brief=140, duration_story=360, choreo="trace")}'))
            loss = 100 * (1 - item["value"] / items[index - 1]["value"])
            parts.append(text((prev[0] + cx)/2, center - 16, f"−{loss:.0f}%", cls="signal-text index" if index == bottleneck + 1 else "muted index", anchor="middle", size=12, extra=motion("lock", connector_standard + 190, brief=connector_brief + 135, story=connector_story + 380, choreo="alarm" if index == bottleneck + 1 else "readout")))
    parts.append(line(x0, 420, x1, 420, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=100, duration=240, duration_brief=150, duration_story=320)}'))
    target_x = (centers[bottleneck][0] + centers[bottleneck + 1][0]) / 2
    loss = losses[bottleneck] * 100
    overlay = []
    for index, (cx, _y, _height, _width) in enumerate(centers):
        signal = index == bottleneck + 1
        overlay += [
            rect(cx - 4, 416, 8, 8, cls="pi-socket-signal" if signal else "pi-socket", extra="" if signal else f'style="--pi-delay:{180 + index * 120}ms"'),
            text(cx, 443, f"S{index + 1}", cls="pi-address pi-address-signal" if signal else "pi-address", anchor="middle", size=9),
        ]
    overlay += [
        circle(target_x, center, 13, cls="pi-lock-ring"),
        path(f"M {target_x-18} {center} H {target_x-11} M {target_x+11} {center} H {target_x+18}", cls="pi-lock-cross"),
        text(target_x, center + 29, f"E08 / Δ{loss:.0f}", cls="pi-address pi-address-signal", anchor="middle", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=EvidenceInterface("E08", "0 64 230 114", 280, 1180, evidence, "\n".join(overlay)),
    )


def build_c9(data: Any) -> str | ChartArtwork:
    if not isinstance(data, dict) or not is_number(data.get("value")):
        return no_data()
    value, target = data["value"], data.get("target") if is_number(data.get("target")) and data.get("target") > 0 else None
    completion = value / target * 100 if target else None
    yoy = data.get("yoy")
    metric_meta = group([text(34, 122, data.get("label", "核心指标"), cls="muted", size=16), text(38, 275, data.get("unit", ""), cls="muted", size=18)], cls="metric-meta", extra=motion("lock", 400, brief=200, story=600, choreo="readout"))
    parts = [
        path(cut_rect_path(0, 74, 680, 336, 14), cls="panel-stroke", extra=motion("dock", 180, dx=-22, brief=70, story=250, duration=460, duration_brief=300, duration_story=620, choreo="interlock")),
        metric_meta,
        text(34, 235, format_num(value), cls="value title-font", size=84, weight=700, extra=motion("lock", 650, brief=330, story=900, duration=320, duration_brief=220, duration_story=440, choreo="readout")),
        line(38, 326, 622, 326, cls="rail-strong", extra=f'pathLength="1" {motion("align", 120, brief=45, story=170)}'),
    ]
    target_x = 622
    if target:
        ratio = min(1, max(0, value / target))
        target_x = 38 + 584 * ratio
        parts += [line(38, 326, target_x, 326, cls="signal-stroke", extra=f'pathLength="1" {motion("route", 820, duration=620, brief=480, story=1450, duration_brief=420, duration_story=900, choreo="trace")}'), line(target_x, 313, target_x, 339, cls="signal-stroke", extra=motion("lock", 1240, brief=850, story=2380, choreo="readout")), text(622, 355, f"TARGET {format_num(target)}", cls="index muted", anchor="end", size=12)]
    context_rows = [
        ("YOY", f"{yoy:+.1f}%" if is_number(yoy) else "—"),
        ("MOM", f"{data.get('mom'):+.1f}%" if is_number(data.get("mom")) else "—"),
        ("TARGET", format_num(target) if target else "—"),
    ]
    context = [line(732, 84, 1128, 84, cls="rail-strong")]
    for index, (label, rendered) in enumerate(context_rows):
        cy = 124 + index * 88
        context += [
            text(732, cy, f"0{index + 1} / {label}", cls="index muted", size=12),
            text(1128, cy + 32, rendered, cls="value", anchor="end", size=26, weight=650),
            line(732, cy + 48, 1128, cy + 48, cls="grid"),
        ]
    parts.append(group(context, cls="metric-context"))
    if completion is not None:
        lock_code = "TGT"
    elif is_number(yoy):
        lock_code = "YOY"
    else:
        lock_code = "VAL"
    foreground = "\n".join([
        rect(34, 322, 8, 8, cls="pm-socket"),
        circle(target_x, 326, 13, cls="pm-lock-ring"),
        text(target_x, 300, f"KPI / {lock_code}", cls="pm-address pm-address-signal", anchor="middle", size=10),
    ])
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=DirectCanvas(foreground_svg=foreground, lock_delay=1060, lock_delay_brief=620, lock_delay_story=1950, compiled_motion=True),
    )


def build_c10(data: Any) -> str | ChartArtwork:
    items = _valid_series(data)[:4]
    if len(items) < 2:
        return no_data()
    hero = max(range(len(items)), key=lambda index: items[index]["value"])
    risks = [index for index, item in enumerate(items) if is_number(item.get("yoy")) and item["yoy"] < 0]
    hero_meta = group(
        [
            text(36, 114, "LEADING REGION", cls="index muted", size=12),
            text(36, 158, items[hero]["label"], cls="title-font", size=30, weight=700),
            text(40, 300, items[hero].get("unit", ""), cls="muted", size=16),
        ],
        cls="decision-hero-meta",
        extra=motion("lock", 420, brief=210, story=620, choreo="readout"),
    )
    parts = [path(cut_rect_path(0, 66, 520, 356, 14), cls="panel-stroke", extra=motion("dock", 200, dx=-24, brief=80, story=260, duration=460, duration_brief=300, duration_story=620, choreo="interlock")), hero_meta, text(36, 265, format_num(items[hero]["value"]), cls="value title-font", size=74, weight=700, extra=motion("lock", 660, brief=320, story=850, duration=320, duration_brief=220, duration_story=440, choreo="readout")), line(36, 340, 474, 340, cls="rail-strong", extra=f'pathLength="1" {motion("align", 120, brief=45, story=180)}')]
    if is_number(items[hero].get("yoy")):
        parts += [text(36, 382, f"YOY {items[hero]['yoy']:+.1f}%", cls="index signal-text", size=14, weight=650, extra=motion("lock", 930, brief=520, story=1320, choreo="readout")), path("M 24 78 V 56 H 46", cls="signal-stroke", extra=f'pathLength="1" {motion("lock", 850, brief=460, story=1200, choreo="readout")}')]
    x0, x1, y0 = 586, 1130, 78
    other_indices = [index for index in range(len(items)) if index != hero]
    others = [items[index] for index in other_indices]
    row_targets: dict[int, tuple[float, float]] = {}
    maximum = max(item["value"] for item in items) or 1
    for index, item in enumerate(others):
        y = y0 + index * 112
        ratio = max(0, item["value"]) / maximum
        is_risk = is_number(item.get("yoy")) and item["yoy"] < 0
        row_standard = 520 + index * 90
        row_brief = 300 + index * 45
        row_story = 1450 + index * 220
        row_heading = group(
            [
                text(x0, y, f"{index+1:02d}", cls="index muted", size=12),
                text(x0 + 42, y, item["label"], size=16, weight=650),
                text(x1, y, format_num(item["value"]), cls="value", anchor="end", size=18, weight=650),
            ],
            cls="decision-row-heading",
            extra=motion("lock", row_standard, brief=row_brief, story=row_story, choreo="readout"),
        )
        row_targets[other_indices[index]] = (x0 + 42 + max(6, (x1-x0-42)*ratio), y + 30)
        parts += [row_heading, line(x0 + 42, y + 30, x1, y + 30, cls="grid", extra=f'pathLength="1" {motion("align", row_standard, brief=row_brief, story=row_story)}'), path(cut_rect_path(x0 + 42, y + 19, max(6, (x1-x0-42)*ratio), 22, 5), cls="signal-fill" if is_risk else "data-fill", extra=motion("dock", 760 + index * 190, dx=-28, brief=450 + index * 100, story=1650 + index * 320, duration=440, duration_brief=280, duration_story=620, choreo="interlock")), text(x1, y + 61, f"YOY {item.get('yoy'):+.1f}%" if is_number(item.get("yoy")) else "YOY —", cls="signal-text index" if is_risk else "muted index", anchor="end", size=12, extra=motion("lock", 1080 + index * 135, brief=700 + index * 70, story=2320 + index * 270, choreo="alarm" if is_risk else "readout"))]
    if risks:
        focus_index = risks[0]
        target_x, target_y = row_targets.get(focus_index, (474, 340))
        lock_code = f"R{focus_index + 1:02d}"
    else:
        focus_index = hero
        target_x, target_y = 474, 340
        lock_code = f"L{hero + 1:02d}"
    overlay = []
    for original_index, (px, py) in row_targets.items():
        overlay.append(rect(x0 + 38, py - 4, 8, 8, cls="pm-socket-signal" if original_index == focus_index else "pm-socket"))
    overlay += [
        circle(target_x, target_y, 13, cls="pm-lock-ring"),
        text(target_x, target_y - 18, f"DECISION / {lock_code}", cls="pm-address pm-address-signal", anchor="middle", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=DirectCanvas(foreground_svg="\n".join(overlay), lock_delay=1120, lock_delay_brief=680, lock_delay_story=2200, compiled_motion=True),
    )


def _polyline(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points)


def _scale(value: float, low: float, high: float, start: float, end: float) -> float:
    if high == low:
        return (start + end) / 2
    return start + (value - low) / (high - low) * (end - start)


def _arc_band(cx: float, cy: float, inner: float, outer: float, start: float, end: float) -> str:
    end = min(end, start + math.tau - .0001)
    large = 1 if end - start > math.pi else 0
    p1 = (cx + outer * math.cos(start), cy + outer * math.sin(start))
    p2 = (cx + outer * math.cos(end), cy + outer * math.sin(end))
    if inner <= 0:
        return f"M {cx:.2f} {cy:.2f} L {p1[0]:.2f} {p1[1]:.2f} A {outer} {outer} 0 {large} 1 {p2[0]:.2f} {p2[1]:.2f} Z"
    p3 = (cx + inner * math.cos(end), cy + inner * math.sin(end))
    p4 = (cx + inner * math.cos(start), cy + inner * math.sin(start))
    return (
        f"M {p1[0]:.2f} {p1[1]:.2f} A {outer} {outer} 0 {large} 1 {p2[0]:.2f} {p2[1]:.2f} "
        f"L {p3[0]:.2f} {p3[1]:.2f} A {inner} {inner} 0 {large} 0 {p4[0]:.2f} {p4[1]:.2f} Z"
    )


def build_c11(data: Any) -> str:
    variant = str(data.get("variant", "donut")).lower() if isinstance(data, dict) else "donut"
    source = data.get("items", []) if isinstance(data, dict) else data
    items = [item for item in _valid_series(source) if item["value"] > 0][:6]
    if not items:
        return no_data()
    total = sum(item["value"] for item in items)
    leader = max(range(len(items)), key=lambda index: items[index]["value"])
    cx, cy, inner, outer = 360, 252, 0 if variant == "pie" else 108, 184
    parts = [
        text(0, 28, "11 / SECTOR LOCK", cls="index muted", size=13),
        circle(cx, cy, outer + 18, cls="hollow", extra=motion("align", 70, brief=30, story=110, duration=260)),
    ]
    if inner:
        parts.append(circle(cx, cy, inner - 14, cls="panel-stroke", extra=motion("dock", 180, brief=80, story=260, choreo="field-seat")))
    angle = -math.pi / 2
    classes = ["data-fill", "cat-1", "cat-2", "cat-3", "secondary-fill", "cat-4"]
    for index, item in enumerate(items):
        sweep = math.tau * item["value"] / total
        gap = min(.025, sweep * .08)
        segment = path(
            _arc_band(cx, cy, inner, outer, angle + gap, angle + sweep - gap),
            cls="signal-fill" if index == leader else classes[index],
            extra=motion("dock", 260 + index * 95, brief=130 + index * 50, story=480 + index * 170, duration=430, duration_brief=280, duration_story=650, choreo="field-seat"),
        )
        parts.append(segment)
        angle += sweep
    share = items[leader]["value"] / total * 100
    parts.append(line(650, 80, 1118, 80, cls="rail-strong", extra=f'pathLength="1" {motion("align", 90, brief=35, story=140)}'))
    if inner:
        parts += [text(cx, cy - 8, f"{share:.1f}%", cls="value title-font", anchor="middle", size=48, weight=700, extra=motion("lock", 1050, brief=610, story=1950, choreo="readout")), text(cx, cy + 28, items[leader]["label"], cls="muted", anchor="middle", size=15)]
    for index, item in enumerate(items):
        y = 118 + index * 54
        parts += [
            rect(650, y, 18, 18, cls="signal-fill" if index == leader else classes[index], extra=motion("dock", 440 + index * 70, dx=-16, brief=230 + index * 35, story=820 + index * 120, choreo="interlock")),
            text(686, y + 15, item["label"], size=15, weight=650 if index == leader else None),
            text(1118, y + 15, f"{item['value'] / total * 100:.1f}%", cls="value index", anchor="end", size=14),
            line(686, y + 28, 1118, y + 28, cls="grid"),
        ]
    parts.append(evidence_plate(888, 390, "S-11", "LEADER", f"{share:.1f}%", "最大构成占比", delay=1480, width=230, brief=860, story=2820, choreo="alarm"))
    return "\n".join(parts)


def build_c12(data: Any) -> str:
    labels = data.get("labels", []) if isinstance(data, dict) else []
    raw = data.get("series", []) if isinstance(data, dict) else []
    series = []
    for item in raw[:4]:
        values = item.get("values", []) if isinstance(item, dict) else []
        if labels and len(values) == len(labels) and all(is_number(value) for value in values):
            series.append(item)
    if not labels or not series:
        return no_data()
    parts = [text(0, 28, "12 / METRIC SMALL MULTIPLES", cls="index muted", size=13)]
    panel_w, panel_h = 548, 188
    for index, item in enumerate(series):
        col, row_i = index % 2, index // 2
        x, y = col * 584, 62 + row_i * 216
        values = item["values"]
        low, high = min(values), max(values)
        pad = max((high - low) * .15, abs(high) * .03, 1)
        px0, px1, py0, py1 = x + 24, x + panel_w - 24, y + 54, y + panel_h - 28
        points = [(_scale(i, 0, max(1, len(values) - 1), px0, px1), _scale(value, low - pad, high + pad, py1, py0)) for i, value in enumerate(values)]
        delta = values[-1] - values[0]
        panel_delay = 150 + index * 120
        parts += [
            path(cut_rect_path(x, y, panel_w, panel_h, 10), cls="panel-stroke", extra=motion("dock", panel_delay, dy=18, brief=70 + index * 55, story=260 + index * 240, choreo="field-seat")),
            text(x + 22, y + 30, f"{index + 1:02d} / {item.get('name', '指标')}", cls="index muted", size=12),
            text(x + panel_w - 22, y + 31, f"{delta:+.1f} {item.get('unit', '')}", cls="index signal-text" if delta >= 0 else "index muted", anchor="end", size=12, extra=motion("lock", 1380 + index * 80, brief=800 + index * 45, story=2640 + index * 160, choreo="alarm" if index == 0 else "readout")),
            line(px0, py1, px1, py1, cls="grid", extra=f'pathLength="1" {motion("align", panel_delay + 80, brief=panel_delay // 2, story=panel_delay * 2)}'),
            path(_polyline(points), cls="signal-stroke" if index == 0 else "data-stroke", extra=f'pathLength="1" {motion("route", panel_delay + 260, brief=160 + index * 80, story=620 + index * 300, choreo="trace")}'),
            text(px0, py1 + 18, labels[0], cls="index muted", size=12),
            text(px1, py1 + 18, labels[-1], cls="index muted", anchor="end", size=12),
            text(px1, points[-1][1] - 10, format_num(values[-1]), cls="value", anchor="end", size=16, weight=650, extra=motion("lock", panel_delay + 680, brief=460 + index * 70, story=1320 + index * 340, choreo="readout")),
        ]
    return "\n".join(parts)


def build_c13(data: Any) -> str:
    items = sorted([item for item in _valid_series(data) if item["value"] >= 0], key=lambda item: item["value"], reverse=True)[:10]
    if not items or sum(item["value"] for item in items) <= 0:
        return no_data()
    total = sum(item["value"] for item in items)
    cumulative, threshold = [], len(items) - 1
    running = 0.0
    for index, item in enumerate(items):
        running += item["value"]
        cumulative.append(running / total * 100)
        if cumulative[-1] >= 80 and threshold == len(items) - 1:
            threshold = index
    x0, x1, y0, y1 = PLOT_LEFT_WITH_EVIDENCE, 1126, 80, 410
    band = (x1 - x0) / len(items)
    maximum = max(item["value"] for item in items)
    parts = [text(0, 28, "13 / PARETO CONTRIBUTION", cls="index muted", size=13), line(x0, y1, x1, y1, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    curve = []
    for index, item in enumerate(items):
        width = band * .52
        height = item["value"] / maximum * 258
        x = x0 + band * index + (band - width) / 2
        y = y1 - height
        curve.append((x + width / 2, _scale(cumulative[index], 0, 100, y1, y0)))
        parts += [
            path(cut_rect_path(x, y, width, height, 6), cls="signal-fill" if index <= threshold else "data-fill", extra=motion("dock", 220 + index * 75, dy=24, brief=110 + index * 38, story=420 + index * 135, choreo="rail-rise")),
            text(x + width / 2, y - 10, format_num(item["value"]), cls="value", anchor="middle", size=13, extra=motion("lock", 700 + index * 50, brief=400 + index * 28, story=1320 + index * 100, choreo="readout")),
            text(x + width / 2, y1 + 26, item["label"], cls="index muted", anchor="middle", size=12),
        ]
    y80 = _scale(80, 0, 100, y1, y0)
    parts += [
        line(x0, y80, x1, y80, cls="rail", extra=f'pathLength="1" {motion("align", 180, brief=80, story=280)}'),
        text(x1, y80 - 8, "80%", cls="index signal-text", anchor="end", size=12),
        path(_polyline(curve), cls="signal-stroke", extra=f'pathLength="1" {motion("route", 720, brief=420, story=1420, duration=620, duration_brief=420, duration_story=980, choreo="trace")}'),
        evidence_plate(0, 76, "P-13", "CORE", f"TOP {threshold + 1}", f"贡献 {cumulative[threshold]:.1f}%", delay=1510, width=190, brief=900, story=2920, choreo="alarm"),
    ]
    return "\n".join(parts)


def build_c14(data: Any) -> str:
    columns = data.get("columns", []) if isinstance(data, dict) else []
    rows = data.get("rows", []) if isinstance(data, dict) else []
    valid = [row for row in rows[:8] if isinstance(row, dict) and str(row.get("label", "")).strip() and isinstance(row.get("values"), list)]
    if not columns or not valid:
        return no_data()
    columns = columns[:8]
    x0, y0 = 260, 86
    cell_w = 850 / len(columns)
    cell_h = min(58, 320 / len(valid))
    parts = [text(0, 28, "14 / COHORT MATRIX", cls="index muted", size=13), line(x0, 62, x0 + cell_w * len(columns), 62, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    for col, label in enumerate(columns):
        parts.append(text(x0 + cell_w * (col + .5), 52, label, cls="index muted", anchor="middle", size=12))
    best = (0.0, "—", "—")
    for row_i, row in enumerate(valid):
        y = y0 + row_i * cell_h
        parts.append(text(0, y + cell_h * .62, row["label"], cls="index muted", size=12))
        for col, value in enumerate(row["values"][:len(columns)]):
            if not is_number(value):
                continue
            x = x0 + col * cell_w
            cls = "signal-fill" if value >= 50 and col > 0 else ("data-fill" if value >= 75 else "cat-1" if value >= 40 else "panel-stroke")
            delay = 220 + row_i * 90 + col * 45
            parts += [
                rect(x + 3, y + 3, cell_w - 6, cell_h - 6, cls=cls, extra=motion("dock", delay, dy=12, brief=100 + row_i * 40 + col * 20, story=420 + row_i * 160 + col * 90, choreo="field-seat")),
                text(x + cell_w / 2, y + cell_h * .62, f"{value:.0f}%", cls=_contrast_text_class(cls), anchor="middle", size=13, weight=650, extra=motion("lock", delay + 250, brief=delay // 2 + 160, story=delay * 2 + 320, choreo="readout")),
            ]
            if col > 0 and value > best[0]:
                best = (value, row["label"], columns[col])
    parts.append(evidence_plate(0, 350, "C-14", "BEST", f"{best[0]:.0f}%", f"{best[1]} / {best[2]}", delay=1740, width=220, brief=980, story=3280, choreo="alarm"))
    return "\n".join(parts)


def build_c15(data: Any) -> str | ChartArtwork:
    nodes = data.get("nodes", []) if isinstance(data, dict) else []
    links = data.get("links", []) if isinstance(data, dict) else []
    nodes = [node for node in nodes[:12] if isinstance(node, dict) and str(node.get("id", "")).strip() and is_number(node.get("level")) and is_number(node.get("value")) and node["value"] >= 0]
    if len(nodes) < 2:
        return no_data()
    by_level: dict[int, list[dict[str, Any]]] = {}
    for node in nodes:
        by_level.setdefault(int(node["level"]), []).append(node)
    levels = sorted(by_level)
    positions: dict[str, tuple[float, float, float, float]] = {}
    maximum = max(node["value"] for node in nodes) or 1
    for level_i, level in enumerate(levels):
        group_nodes = by_level[level]
        x = _scale(level_i, 0, max(1, len(levels) - 1), PLOT_LEFT_WITH_EVIDENCE, 1040)
        for row_i, node in enumerate(group_nodes):
            y = 120 + (row_i + .5) * 300 / len(group_nodes)
            height = 42 + 74 * math.sqrt(node["value"] / maximum)
            positions[str(node["id"])] = (x, y - height / 2, 112, height)
    valid_links = [item for item in links[:18] if isinstance(item, dict) and str(item.get("source")) in positions and str(item.get("target")) in positions and is_number(item.get("value")) and item["value"] >= 0]
    parts = [text(0, 28, "15 / COMMERCE FLOW", cls="index muted", size=13), line(PLOT_LEFT_WITH_EVIDENCE, 442, 1130, 442, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    link_max = max((item["value"] for item in valid_links), default=1) or 1
    for index, item in enumerate(valid_links):
        sx, sy, sw, sh = positions[str(item["source"])]
        tx, ty, _tw, th = positions[str(item["target"])]
        start, end = (sx + sw, sy + sh / 2), (tx, ty + th / 2)
        bend = (start[0] + end[0]) / 2
        d = f"M {start[0]} {start[1]} C {bend} {start[1]} {bend} {end[1]} {end[0]} {end[1]}"
        width = 2 + 12 * math.sqrt(item["value"] / link_max)
        parts.append(path(d, cls="secondary-stroke", extra=f'stroke-width="{width:.1f}" pathLength="1" {motion("route", 320 + index * 120, brief=160 + index * 65, story=620 + index * 240, duration=480, duration_brief=300, duration_story=760, choreo="trace")}'))
    for index, node in enumerate(nodes):
        x, y, width, height = positions[str(node["id"])]
        fill_cls = "signal-fill" if node["level"] == max(levels) else "data-fill"
        label_cls = _contrast_text_class(fill_cls)
        parts += [
            path(cut_rect_path(x, y, width, height, 8), cls=fill_cls, extra=motion("dock", 220 + index * 110, dx=-22, brief=100 + index * 55, story=420 + index * 210, choreo="interlock")),
            text(x + width / 2, y + height / 2 - 2, node.get("label", node["id"]), cls=label_cls, anchor="middle", size=13, weight=650),
            text(x + width / 2, y + height / 2 + 20, format_num(node["value"]), cls=f"index {label_cls}", anchor="middle", size=12),
        ]
    if not valid_links:
        return "\n".join(parts)
    weakest_index = min(range(len(valid_links)), key=lambda index: valid_links[index]["value"])
    weakest = valid_links[weakest_index]
    evidence = evidence_plate(0, 86, "F-15", "LEAK", format_num(weakest["value"]), "最小有效流量", delay=1740, width=200, brief=980, story=3300, choreo="alarm")
    ports: list[tuple[float, float]] = []
    for item in valid_links:
        sx, sy, sw, sh = positions[str(item["source"])]
        tx, ty, _tw, th = positions[str(item["target"])]
        for port in ((sx + sw, sy + sh / 2), (tx, ty + th / 2)):
            if not any(abs(port[0] - x) < .01 and abs(port[1] - y) < .01 for x, y in ports):
                ports.append(port)
    weak_sx, weak_sy, weak_sw, weak_sh = positions[str(weakest["source"])]
    weak_tx, weak_ty, _weak_tw, weak_th = positions[str(weakest["target"])]
    weak_start = (weak_sx + weak_sw, weak_sy + weak_sh / 2)
    weak_end = (weak_tx, weak_ty + weak_th / 2)
    target_x = (weak_start[0] + weak_end[0]) / 2
    target_y = (weak_start[1] + weak_end[1]) / 2
    overlay = []
    for index, (px, py) in enumerate(ports):
        signal = abs(px - weak_end[0]) < .01 and abs(py - weak_end[1]) < .01
        overlay.append(rect(px - 4, py - 4, 8, 8, cls="pi-socket-signal" if signal else "pi-socket", extra="" if signal else f'style="--pi-delay:{180 + index * 100}ms"'))
    overlay += [
        circle(target_x, target_y, 14, cls="pi-lock-ring"),
        text(target_x, target_y + 30, f"E15 / L{weakest_index + 1:02d}", cls="pi-address pi-address-signal", anchor="middle", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=EvidenceInterface("E15", "0 76 200 114", 250, 1100, evidence, "\n".join(overlay)),
    )


def build_c16(data: Any) -> str:
    items = [item for item in data[:12] if isinstance(item, dict) and str(item.get("label", "")).strip() and all(is_number(item.get(key)) for key in ("x", "y", "size")) and item["size"] >= 0] if isinstance(data, list) else []
    if not items:
        return no_data()
    x_values, y_values = [item["x"] for item in items], [item["y"] for item in items]
    x_low, x_high, y_low, y_high = min(x_values), max(x_values), min(y_values), max(y_values)
    x_pad, y_pad = max((x_high - x_low) * .12, 1), max((y_high - y_low) * .15, 1)
    x0, x1, y0, y1 = PLOT_LEFT_WITH_EVIDENCE, 1118, 74, 420
    mid_x, mid_y = (x_low + x_high) / 2, (y_low + y_high) / 2
    x_mid, y_mid = _scale(mid_x, x_low - x_pad, x_high + x_pad, x0, x1), _scale(mid_y, y_low - y_pad, y_high + y_pad, y1, y0)
    leader = max(range(len(items)), key=lambda i: items[i]["x"] * items[i]["y"])
    max_size = max(item["size"] for item in items) or 1
    parts = [
        text(0, 28, "16 / DECISION BUBBLE MATRIX", cls="index muted", size=13),
        line(x0, y1, x1, y1, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}'),
        line(x0, y0, x0, y1, cls="rail-strong", extra=f'pathLength="1" {motion("align", 90, brief=40, story=140)}'),
        line(x_mid, y0, x_mid, y1, cls="grid"), line(x0, y_mid, x1, y_mid, cls="grid"),
        text(x1, y1 + 28, "X / 规模或收益 →", cls="index muted", anchor="end", size=12),
        text(x0, y0 - 12, "Y / 效率或质量 ↑", cls="index muted", size=12),
    ]
    for index, item in enumerate(items):
        x = _scale(item["x"], x_low - x_pad, x_high + x_pad, x0, x1)
        y = _scale(item["y"], y_low - y_pad, y_high + y_pad, y1, y0)
        radius = 12 + 28 * math.sqrt(item["size"] / max_size)
        fill_cls = "signal-fill" if index == leader else "cat-1"
        parts += [
            circle(x, y, radius, cls=fill_cls, extra=motion("dock", 300 + index * 110, dy=18, brief=150 + index * 58, story=560 + index * 220, choreo="pin")),
            text(x, y + 4, f"{index + 1:02d}", cls=f"index {_contrast_text_class(fill_cls)}", anchor="middle", size=12),
            text(x + radius + 8, y - radius - 4, item["label"], size=13, weight=650 if index == leader else None, extra=motion("lock", 720 + index * 70, brief=430 + index * 40, story=1380 + index * 150, choreo="readout")),
        ]
    parts.append(evidence_plate(0, 82, "D-16", "PRIORITY", items[leader]["label"], "综合位置最优", delay=1580, width=220, brief=900, story=3020, choreo="alarm"))
    return "\n".join(parts)


def build_c17(data: Any) -> str:
    items = [item for item in data[:20] if isinstance(item, dict) and str(item.get("date", "")).strip() and all(is_number(item.get(key)) for key in ("open", "high", "low", "close", "volume")) and item["high"] >= max(item["open"], item["close"], item["low"])] if isinstance(data, list) else []
    if not items:
        return no_data()
    low, high = min(item["low"] for item in items), max(item["high"] for item in items)
    volume_max = max(item["volume"] for item in items) or 1
    x0, x1, price_top, price_bottom, volume_bottom = PLOT_LEFT_WITH_EVIDENCE, 1118, 64, 338, 432
    band = (x1 - x0) / len(items)
    y = lambda value: _scale(value, low, high, price_bottom, price_top)
    parts = [text(0, 28, "17 / MARKET CANDLES", cls="index muted", size=13), line(x0, price_bottom, x1, price_bottom, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}'), line(x0, volume_bottom, x1, volume_bottom, cls="rail")]
    for tick in range(5):
        value = low + (high - low) * tick / 4
        yy = y(value)
        parts += [line(x0, yy, x1, yy, cls="grid"), text(x0 - 18, yy + 4, f"{value:.1f}", cls="index muted", anchor="end", size=12)]
    for index, item in enumerate(items):
        cx = x0 + band * (index + .5)
        up = item["close"] >= item["open"]
        body_top, body_bottom = min(y(item["open"]), y(item["close"])), max(y(item["open"]), y(item["close"]))
        cls = "signal-fill" if up else "data-fill"
        delay = 220 + index * 105
        parts += [
            line(cx, y(item["high"]), cx, y(item["low"]), cls="signal-stroke" if up else "data-stroke", extra=motion("align", delay, brief=110 + index * 50, story=420 + index * 210)),
            rect(cx - min(19, band * .24), body_top, min(38, band * .48), max(3, body_bottom - body_top), cls=cls, extra=motion("dock", delay + 120, dy=16, brief=delay // 2 + 80, story=delay * 2 + 180, choreo="field-seat")),
            rect(cx - min(15, band * .20), volume_bottom - 70 * item["volume"] / volume_max, min(30, band * .40), 70 * item["volume"] / volume_max, cls="secondary-fill", extra=motion("dock", delay + 80, dy=12, brief=delay // 2, story=delay * 2, choreo="rail-rise")),
            text(cx, volume_bottom + 22, item["date"], cls="index muted", anchor="middle", size=12),
        ]
    change = (items[-1]["close"] / items[0]["open"] - 1) * 100 if items[0]["open"] else 0
    parts.append(evidence_plate(0, 78, "M-17", "CHANGE", f"{change:+.1f}%", "区间开盘至收盘", delay=1680, width=220, brief=960, story=3220, choreo="alarm"))
    return "\n".join(parts)


def build_c18(data: Any) -> str:
    labels = data.get("labels", []) if isinstance(data, dict) else []
    values = data.get("values", []) if isinstance(data, dict) else []
    if not labels or len(labels) != len(values) or not all(is_number(value) and value > 0 for value in values):
        return no_data()
    peak, drawdowns, max_dd = values[0], [], 0.0
    for value in values:
        peak = max(peak, value)
        dd = value / peak - 1
        drawdowns.append(dd)
        max_dd = min(max_dd, dd)
    x0, x1, top, split, bottom = PLOT_LEFT_WITH_EVIDENCE, 1118, 66, 294, 430
    xs = [_scale(i, 0, max(1, len(values) - 1), x0, x1) for i in range(len(values))]
    perf = [(x, _scale(value, min(values), max(values), split - 24, top)) for x, value in zip(xs, values)]
    under = [(x, _scale(dd, max_dd if max_dd < 0 else -1, 0, bottom, split + 28)) for x, dd in zip(xs, drawdowns)]
    area = [(x0, split + 28)] + under + [(x1, split + 28)]
    parts = [
        text(0, 28, "18 / PERFORMANCE DRAWDOWN", cls="index muted", size=13),
        line(x0, split, x1, split, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}'),
        path(_polyline(perf), cls="data-stroke", extra=f'pathLength="1" {motion("route", 260, brief=130, story=500, duration=720, duration_brief=460, duration_story=1100, choreo="trace")}'),
        polygon(area, cls="cat-1", extra=motion("dock", 740, dy=12, brief=420, story=1480, choreo="band-fill")),
        path(_polyline(under), cls="signal-stroke", extra=f'pathLength="1" {motion("route", 820, brief=480, story=1640, duration=620, duration_brief=420, duration_story=980, choreo="trace")}'),
        text(x0, top - 10, "累计净值", cls="index muted", size=12), text(x0, split + 48, "回撤区间", cls="index muted", size=12),
        text(x0, bottom + 22, labels[0], cls="index muted", size=12), text(x1, bottom + 22, labels[-1], cls="index muted", anchor="end", size=12),
        evidence_plate(0, 80, "R-18", "MAX DD", f"{max_dd * 100:.1f}%", "历史最大回撤", delay=1540, width=210, brief=880, story=2940, choreo="alarm"),
    ]
    return "\n".join(parts)


def build_c19(data: Any) -> str:
    labels = data.get("maturities", []) if isinstance(data, dict) else []
    raw = data.get("series", []) if isinstance(data, dict) else []
    series = [item for item in raw[:3] if isinstance(item, dict) and isinstance(item.get("values"), list) and len(item["values"]) == len(labels) and all(is_number(value) for value in item["values"])]
    if len(labels) < 2 or not series:
        return no_data()
    all_values = [value for item in series for value in item["values"]]
    low, high = min(all_values), max(all_values)
    pad = max((high - low) * .18, .1)
    x0, x1, y0, y1 = PLOT_LEFT_WITH_EVIDENCE, 1118, 76, 408
    parts = [text(0, 28, "19 / YIELD CURVE", cls="index muted", size=13), line(x0, y1, x1, y1, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    for tick in range(5):
        yy = y1 - (y1 - y0) * tick / 4
        value = low - pad + (high - low + 2 * pad) * tick / 4
        parts += [line(x0, yy, x1, yy, cls="grid"), text(x0 - 18, yy + 4, f"{value:.2f}%", cls="index muted", anchor="end", size=12)]
    for index, item in enumerate(series):
        points = [(_scale(i, 0, len(labels) - 1, x0, x1), _scale(value, low - pad, high + pad, y1, y0)) for i, value in enumerate(item["values"])]
        parts += [path(_polyline(points), cls="signal-stroke" if index == 0 else "secondary-stroke", extra=f'pathLength="1" {motion("route", 280 + index * 180, brief=140 + index * 100, story=520 + index * 420, duration=650, duration_brief=420, duration_story=980, choreo="trace")}'), text(x1, points[-1][1] - 10 - index * 18, item.get("name", f"系列{index + 1}"), cls="index signal-text" if index == 0 else "index muted", anchor="end", size=12, extra=motion("lock", 980 + index * 180, brief=580 + index * 100, story=1920 + index * 360, choreo="readout"))]
        for point in points:
            parts.append(circle(point[0], point[1], 4 if index == 0 else 3, cls="signal-fill" if index == 0 else "data-fill", extra=motion("dock", 520 + index * 120, brief=290 + index * 70, story=980 + index * 280, choreo="pin")))
    for index, label in enumerate(labels):
        parts.append(text(_scale(index, 0, len(labels) - 1, x0, x1), y1 + 28, label, cls="index muted", anchor="middle", size=12))
    slope = series[0]["values"][-1] - series[0]["values"][0]
    parts.append(evidence_plate(0, 82, "Y-19", "SLOPE", f"{slope:+.2f}pp", "长端减短端", delay=1480, width=210, brief=850, story=2820, choreo="alarm"))
    return "\n".join(parts)


def _matrix_data(data: Any, row_key: str = "rows") -> tuple[list[str], list[str], list[list[float]]]:
    if not isinstance(data, dict):
        return [], [], []
    rows, columns, values = data.get(row_key, []), data.get("columns", data.get("labels", [])), data.get("values", [])
    if not rows or not columns or len(values) != len(rows):
        return [], [], []
    clean = []
    for row in values:
        if not isinstance(row, list) or len(row) != len(columns) or not all(is_number(value) for value in row):
            return [], [], []
        clean.append(row)
    return [str(value) for value in rows], [str(value) for value in columns], clean


def build_c20(data: Any) -> str:
    rows, columns, values = _matrix_data(data)
    if not rows or len(rows) > 8 or len(columns) > 8:
        return no_data()
    flat = [value for row in values for value in row]
    low, high = min(flat), max(flat)
    best = max((value, row_i, col_i) for row_i, row in enumerate(values) for col_i, value in enumerate(row))
    x0, y0 = 270, 80
    cell_w, cell_h = 840 / len(columns), min(62, 330 / len(rows))
    parts = [text(0, 28, "20 / SENSITIVITY MATRIX", cls="index muted", size=13), line(x0, 58, x0 + cell_w * len(columns), 58, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    for col, label in enumerate(columns):
        parts.append(text(x0 + cell_w * (col + .5), 48, label, cls="index muted", anchor="middle", size=12))
    for row_i, label in enumerate(rows):
        y = y0 + row_i * cell_h
        parts.append(text(0, y + cell_h * .62, label, cls="index muted", size=12))
        for col_i, value in enumerate(values[row_i]):
            x = x0 + col_i * cell_w
            ratio = (value - low) / (high - low or 1)
            cls = "signal-fill" if (value, row_i, col_i) == best else ("data-fill" if ratio > .72 else "cat-1" if ratio > .38 else "panel-stroke")
            delay = 220 + row_i * 80 + col_i * 55
            parts += [rect(x + 3, y + 3, cell_w - 6, cell_h - 6, cls=cls, extra=motion("dock", delay, dy=12, brief=100 + row_i * 35 + col_i * 24, story=420 + row_i * 150 + col_i * 100, choreo="field-seat")), text(x + cell_w / 2, y + cell_h * .62, format_num(value), cls=_contrast_text_class(cls), anchor="middle", size=14, weight=650, extra=motion("lock", delay + 240, brief=delay // 2 + 150, story=delay * 2 + 300, choreo="readout"))]
    parts.append(evidence_plate(0, 348, "S-20", "UPSIDE", format_num(best[0]), f"{rows[best[1]]} / {columns[best[2]]}", delay=1780, width=246, brief=1020, story=3400, choreo="alarm"))
    return "\n".join(parts)


def _percentile(values: list[float], ratio: float) -> float:
    position = (len(values) - 1) * ratio
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return values[low]
    return values[low] + (values[high] - values[low]) * (position - low)


def build_c21(data: Any) -> str:
    values = sorted(value for value in data if is_number(value)) if isinstance(data, list) else []
    if len(values) < 2:
        return no_data()
    low, high = values[0], values[-1]
    bins = min(10, max(5, round(math.sqrt(len(values)))))
    counts = [0] * bins
    for value in values:
        index = min(bins - 1, int((value - low) / (high - low or 1) * bins))
        counts[index] += 1
    x0, x1, top, base = PLOT_LEFT_WITH_EVIDENCE, 1118, 84, 336
    band = (x1 - x0) / bins
    maximum = max(counts)
    parts = [text(0, 28, "21 / DISTRIBUTION PROFILE", cls="index muted", size=13), line(x0, base, x1, base, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    for index, count in enumerate(counts):
        height = count / maximum * (base - top)
        x = x0 + index * band + 3
        parts += [rect(x, base - height, band - 6, height, cls="signal-fill" if count == maximum else "data-fill", extra=motion("dock", 240 + index * 80, dy=24, brief=120 + index * 42, story=440 + index * 150, choreo="rail-rise")), text(x + (band - 6) / 2, base - height - 10, count, cls="index muted", anchor="middle", size=12)]
    q1, median, q3 = _percentile(values, .25), _percentile(values, .5), _percentile(values, .75)
    pos = lambda value: _scale(value, low, high, x0, x1)
    box_y = 394
    parts += [
        line(pos(low), box_y, pos(high), box_y, cls="rail", extra=f'pathLength="1" {motion("align", 650, brief=380, story=1280)}'),
        rect(pos(q1), box_y - 22, max(4, pos(q3) - pos(q1)), 44, cls="panel-stroke", extra=motion("dock", 820, dx=-16, brief=480, story=1580, choreo="interlock")),
        line(pos(median), box_y - 28, pos(median), box_y + 28, cls="signal-stroke", extra=motion("lock", 1120, brief=650, story=2180, choreo="alarm")),
        text(x0, 446, format_num(low), cls="index muted", size=12), text(x1, 446, format_num(high), cls="index muted", anchor="end", size=12),
        evidence_plate(0, 82, "D-21", "MEDIAN", format_num(median), f"IQR {format_num(q3 - q1)}", delay=1480, width=200, brief=850, story=2840, choreo="readout"),
    ]
    return "\n".join(parts)


def build_c22(data: Any) -> str | ChartArtwork:
    labels = data.get("labels", []) if isinstance(data, dict) else []
    values = data.get("values", []) if isinstance(data, dict) else []
    if not labels or len(labels) > 8 or len(values) != len(labels) or any(not isinstance(row, list) or len(row) != len(labels) or not all(is_number(value) and -1 <= value <= 1 for value in row) for row in values):
        return no_data()
    x0, y0 = 300, 70
    size = min(72, 350 / len(labels))
    strongest = max(((abs(value), value, row, col) for row, line_values in enumerate(values) for col, value in enumerate(line_values) if row != col), key=lambda item: item[0], default=(0, 0, 0, 0))
    parts = [text(0, 28, "22 / CORRELATION MATRIX", cls="index muted", size=13), line(x0, 52, x0 + size * len(labels), 52, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    for index, label in enumerate(labels):
        parts += [text(x0 + size * (index + .5), 42, label, cls="index muted", anchor="middle", size=12), text(288, y0 + size * (index + .62), label, cls="index muted", anchor="end", size=12)]
    for row, line_values in enumerate(values):
        for col, value in enumerate(line_values):
            x, y = x0 + col * size, y0 + row * size
            is_focus = row != col and abs(value) == strongest[0]
            cls = "signal-fill" if is_focus else ("data-fill" if value >= .65 else "cat-1" if value >= 0 else "cat-4")
            delay = 200 + row * 70 + col * 45
            parts += [rect(x + 3, y + 3, size - 6, size - 6, cls=cls, extra=motion("dock", delay, dy=10, brief=90 + row * 32 + col * 20, story=380 + row * 140 + col * 85, choreo="field-seat")), text(x + size / 2, y + size * .61, f"{value:+.2f}" if value != 1 else "1.00", cls=_contrast_text_class(cls), anchor="middle", size=12, weight=650, extra=motion("lock", delay + 230, brief=delay // 2 + 140, story=delay * 2 + 290, choreo="readout"))]
    evidence = evidence_plate(0, 346, "C-22", "STRONG", f"{strongest[1]:+.2f}", f"{labels[strongest[2]]} × {labels[strongest[3]]}", delay=1820, width=230, brief=1030, story=3480, choreo="alarm")
    focus_row, focus_col = strongest[2], strongest[3]
    focus_x, focus_y = x0 + focus_col * size, y0 + focus_row * size
    inset, arm = 1, min(16, size * .24)
    left, right, top, bottom = focus_x - inset, focus_x + size + inset, focus_y - inset, focus_y + size + inset
    overlay = []
    for index in range(len(labels)):
        col_x = x0 + size * (index + .5)
        row_y = y0 + size * (index + .56)
        signal = index == focus_col
        overlay += [
            text(col_x, 65, f"C{index + 1}", cls="pi-address pi-address-signal" if signal else "pi-address", anchor="middle", size=9),
            text(286, row_y, f"R{index + 1}", cls="pi-address pi-address-signal" if signal else "pi-address", anchor="end", size=9),
        ]
    focus_path = (
        f"M {left} {top+arm} V {top} H {left+arm} "
        f"M {right-arm} {top} H {right} V {top+arm} "
        f"M {right} {bottom-arm} V {bottom} H {right-arm} "
        f"M {left+arm} {bottom} H {left} V {bottom-arm}"
    )
    overlay += [
        path(focus_path, cls="pi-focus-corner"),
        text(x0 + size * len(labels) + 10, top + 19, f"E22 / A{focus_col + 1:02d}", cls="pi-address pi-address-signal", size=10),
    ]
    return ChartArtwork(
        svg="\n".join(parts),
        presentation=EvidenceInterface("E22", "0 336 230 114", 255, 980, evidence, "\n".join(overlay)),
    )


def build_c23(data: Any) -> str:
    if not isinstance(data, dict):
        return no_data()
    labels, actual, forecast, lower, upper = (data.get(key, []) for key in ("labels", "actual", "forecast", "lower", "upper"))
    if len(labels) < 3 or len(actual) < 2 or len(forecast) < 2 or not (len(forecast) == len(lower) == len(upper)) or len(actual) + len(forecast) - 1 != len(labels) or not all(is_number(value) for seq in (actual, forecast, lower, upper) for value in seq) or any(lo > mid or mid > hi for lo, mid, hi in zip(lower, forecast, upper)):
        return no_data()
    all_values = actual + lower + upper
    low, high = min(all_values), max(all_values)
    pad = max((high - low) * .12, 1)
    x0, x1, y0, y1 = PLOT_LEFT_WITH_EVIDENCE, 1118, 72, 414
    xs = [_scale(index, 0, len(labels) - 1, x0, x1) for index in range(len(labels))]
    y = lambda value: _scale(value, low - pad, high + pad, y1, y0)
    split = len(actual) - 1
    actual_points = [(xs[index], y(value)) for index, value in enumerate(actual)]
    forecast_points = [(xs[split + index], y(value)) for index, value in enumerate(forecast)]
    upper_points = [(xs[split + index], y(value)) for index, value in enumerate(upper)]
    lower_points = [(xs[split + index], y(value)) for index, value in enumerate(lower)]
    band = upper_points + list(reversed(lower_points))
    parts = [
        text(0, 28, "23 / FORECAST FAN", cls="index muted", size=13),
        line(x0, y1, x1, y1, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}'),
        line(xs[split], y0, xs[split], y1, cls="rail", extra=motion("align", 160, brief=70, story=250)),
        text(xs[split], y0 - 10, "FORECAST →", cls="index signal-text", size=12),
        polygon(band, cls="cat-1", extra=motion("dock", 520, dx=-20, brief=300, story=1020, choreo="band-fill")),
        path(_polyline(actual_points), cls="data-stroke", extra=f'pathLength="1" {motion("route", 240, brief=120, story=460, duration=600, duration_brief=380, duration_story=900, choreo="trace")}'),
        path(_polyline(forecast_points), cls="signal-stroke", extra=f'pathLength="1" {motion("route", 760, brief=440, story=1480, duration=650, duration_brief=420, duration_story=980, choreo="trace")}'),
    ]
    for index, label in enumerate(labels):
        if index in {0, split, len(labels) - 1}:
            parts.append(text(xs[index], y1 + 28, label, cls="index muted", anchor="middle", size=12))
    uncertainty = upper[-1] - lower[-1]
    parts.append(evidence_plate(0, 82, "F-23", "RANGE", format_num(uncertainty), "末期预测区间宽度", delay=1580, width=226, brief=900, story=3040, choreo="alarm"))
    return "\n".join(parts)


def build_c24(data: Any) -> str:
    if not isinstance(data, dict):
        return no_data()
    labels, values = data.get("labels", []), data.get("values", [])
    center, ucl, lcl = data.get("center"), data.get("ucl"), data.get("lcl")
    if not labels or len(labels) != len(values) or not all(is_number(value) for value in values) or not all(is_number(value) for value in (center, ucl, lcl)) or not lcl < center < ucl:
        return no_data()
    low, high = min(min(values), lcl), max(max(values), ucl)
    pad = max((high - low) * .15, 1)
    x0, x1, y0, y1 = PLOT_LEFT_WITH_EVIDENCE, 1118, 72, 414
    xs = [_scale(index, 0, max(1, len(values) - 1), x0, x1) for index in range(len(values))]
    y = lambda value: _scale(value, low - pad, high + pad, y1, y0)
    points = [(x, y(value)) for x, value in zip(xs, values)]
    breaches = [index for index, value in enumerate(values) if value > ucl or value < lcl]
    parts = [text(0, 28, "24 / CONTROL CHART", cls="index muted", size=13), line(x0, y1, x1, y1, cls="rail-strong", extra=f'pathLength="1" {motion("align", 70, brief=30, story=110)}')]
    for label, value, cls in (("UCL", ucl, "signal-stroke"), ("CENTER", center, "rail"), ("LCL", lcl, "signal-stroke")):
        yy = y(value)
        parts += [line(x0, yy, x1, yy, cls=cls, extra=f'pathLength="1" {motion("align", 150, brief=70, story=240)}'), text(x1, yy - 7, f"{label} {format_num(value)}", cls="index signal-text" if label != "CENTER" else "index muted", anchor="end", size=12)]
    parts.append(path(_polyline(points), cls="data-stroke", extra=f'pathLength="1" {motion("route", 360, brief=190, story=700, duration=680, duration_brief=440, duration_story=1040, choreo="trace")}'))
    for index, ((x, yy), value) in enumerate(zip(points, values)):
        alarm = index in breaches
        parts += [circle(x, yy, 7 if alarm else 4, cls="signal-fill" if alarm else "data-fill", extra=motion("dock", 620 + index * 55, dy=14, brief=350 + index * 28, story=1220 + index * 110, choreo="pin")), text(x, y1 + 27, labels[index], cls="index muted", anchor="middle", size=12)]
        if alarm:
            parts.append(path(f"M {x-13} {yy-13} V {yy-27} H {x+3}", cls="signal-stroke", extra=f'pathLength="1" {motion("lock", 1250 + index * 35, brief=740 + index * 18, story=2380 + index * 70, choreo="alarm")}'))
    parts.append(evidence_plate(0, 82, "Q-24", "ALARM", str(len(breaches)), "超出控制界限", delay=1580, width=210, brief=900, story=3020, choreo="alarm"))
    return "\n".join(parts)


BUILDERS: dict[str, Callable[[Any], str | ChartArtwork]] = {
    "C1": build_c1, "C2": build_c2, "C3": build_c3, "C4": build_c4, "C5": build_c5,
    "C6": build_c6, "C7": build_c7, "C8": build_c8, "C9": build_c9, "C10": build_c10,
    "C11": build_c11, "C12": build_c12, "C13": build_c13, "C14": build_c14,
    "C15": build_c15, "C16": build_c16, "C17": build_c17, "C18": build_c18,
    "C19": build_c19, "C20": build_c20, "C21": build_c21, "C22": build_c22,
    "C23": build_c23, "C24": build_c24,
}


def _data_signature(data: Any) -> str:
    """Summarise the live contract shape without exposing or inventing values."""
    if isinstance(data, list):
        return f"{len(data):02d}I"
    if not isinstance(data, dict):
        return "00I"

    rows = data.get("rows")
    columns = data.get("columns")
    if isinstance(rows, list) and isinstance(columns, list):
        return f"{len(rows):02d}R · {len(columns):02d}C"

    nodes = data.get("nodes")
    links = data.get("links")
    if isinstance(nodes, list) and isinstance(links, list):
        return f"{len(nodes):02d}N · {len(links):02d}R"

    axis = next((data.get(key) for key in ("labels", "categories", "maturities") if isinstance(data.get(key), list)), None)
    series = data.get("series")
    if isinstance(axis, list):
        if isinstance(series, list):
            return f"{len(axis):02d}T · {len(series):02d}S"
        return f"{len(axis):02d}T"

    items = data.get("items")
    if isinstance(items, list):
        return f"{len(items):02d}I"
    return f"{len(data):02d}F"


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
    artwork = BUILDERS[key](source)
    svg = artwork.svg if isinstance(artwork, ChartArtwork) else artwork
    presentation = artwork.presentation if isinstance(artwork, ChartArtwork) else DirectCanvas()
    page = ChartPage(
        chart_id=key,
        slug=meta["slug"],
        public_name=meta["name"],
        title=title or meta["title"],
        subtitle=subtitle,
        footer=footer,
        svg=svg,
        data=source,
        family=meta["family"],
        data_signature=_data_signature(source),
        interface_state=meta["state"],
        total_ms=1900 if key in {"C3", "C7", "C8"} else 1750,
        profile_totals=PROFILE_TOTALS.get(key, {}),
        choreography=CHOREOGRAPHIES.get(key, "structural"),
        surface=surface if surface in {"light", "dark"} else "light",
        mode=mode if mode in {"brief", "editorial"} else "editorial",
        presentation=presentation,
        presentation_target=PRESENTATION_TARGETS[key],
    )
    return html_page(page, embed_fonts=embed_fonts)
