#!/usr/bin/env python3
"""
moxing-studio 模板生成器（v1.1 静态 SVG 版）

用 Python 在生成阶段完成全部布局计算，把 SVG 坐标写死为具体数字，
产出零运行时 JS 依赖的模板文件：
  templates/c01-bar.html   C1 柱状图
  templates/c02-hbar.html  C2 条形图

保留三个标记块供 gallery.html 的主题替换引擎使用：
  /* __CSS_THEME_START__ */ ... /* __CSS_THEME_END__ */
  // __JS_THEME_START__    ... // __JS_THEME_END__
  // __DATA_START__        ... // __DATA_END__
每个模板仅含一个 hover tooltip 的 <script>（渐进增强，删除后图表完整）。
"""
import json
import math
import os

# ===== 主题 token（paper，模板默认值；与 tokens/themes.js 保持一致） =====
THEME = {
    "BG": "#FAFAF7",
    "TXT": "#23262B",
    "MUT": "#8A8F98",
    "GRID": "#E4E3DE",
    "DATA": "#2F6B4F",
    "RAMP": ["#2F6B4F", "#5E9478", "#93BCA4", "#C5DBCF"],
    "CAT": ["#2F6B4F", "#C46A4A", "#4A6FA5", "#D9A441"],
    "HERO": "#C46A4A",
    "FONT": "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
    "LINE_WIDTH": 2,
    "RADIUS": 12,
    "DARK": False,
}

# 画布定尺：1280×720，padding 40/48/32/48
PAGE_W, PAGE_H = 1280, 720
PAD_T, PAD_R, PAD_B, PAD_L = 40, 48, 32, 48
# 图表区域（chart-body 的 SVG viewBox 尺寸）
W, H = PAGE_W - PAD_L - PAD_R, PAGE_H - PAD_T - PAD_B - 40 - 30  # 1184 × 578

HERE = os.path.dirname(os.path.abspath(__file__))
TPL_DIR = os.path.join(HERE, "..", "templates")


# ===== 工具函数（与原 JS 版逻辑一一对应） =====
def format_num(v):
    """≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位（整数不带小数点）"""
    if isinstance(v, float) and v == int(v):
        v = int(v)
    a = abs(v)
    if a >= 1e8:
        s = f"{v / 1e8:.2f}".rstrip("0").rstrip(".")
        return s + "亿"
    if a >= 1e4:
        s = f"{v / 1e4:.1f}"
        if s.endswith(".0"):
            s = s[:-2]
        return s + "万"
    return f"{v:,}"


def nice_ceil(v):
    """向上取整到好看的数字（1 / 2 / 2.5 / 5 / 10 的倍数）"""
    if v <= 0:
        return 1
    exp = math.floor(math.log10(v))
    base = 10 ** exp
    n = v / base
    if n <= 1:
        return base
    if n <= 2:
        return 2 * base
    if n <= 2.5:
        return 2.5 * base
    if n <= 5:
        return 5 * base
    return 10 * base


def nice_floor(v):
    if v >= 0:
        return 0
    return -nice_ceil(-v)


def fmt(n):
    """坐标数值格式化：整数输出整数，否则最多两位小数"""
    r = round(n, 2)
    if r == int(r):
        return str(int(r))
    return f"{r:.2f}".rstrip("0")


def estimate_text_width(text, font_size=12):
    """
    静态估算文本宽度（替代运行时 canvas measureText）。
    CJK 字符 ≈ font_size，ASCII ≈ font_size * 0.56。
    宁可偏宽不可偏窄（左边距宁大勿小）。
    """
    w = 0.0
    for ch in text:
        w += font_size if ord(ch) > 0x2E7F else font_size * 0.56
    return w


def is_number(value):
    """仅接受有限实数；None、布尔值、NaN、Infinity 都视为空值。"""
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def no_data_svg(message="暂无可用数据"):
    """边界数据为空或不符合图型契约时，保持定尺并给出静态空状态。"""
    return text(W / 2, H / 2, message, "middle", 24, THEME["MUT"], weight=600)


# ===== SVG 元素拼装 =====
def line(x1, y1, x2, y2, stroke, sw=1):
    return (f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def text(x, y, content, anchor, size, fill, weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{fmt(x)}" y="{fmt(y)}" text-anchor="{anchor}" font-size="{size}"'
            f'{w} fill="{fill}" font-family="{THEME["FONT"]}"{extra}>{content}</text>')


def rect(x, y, w_, h_, rx, fill, tip):
    return (f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w_)}" height="{fmt(h_)}" '
            f'rx="{rx}" fill="{fill}" data-tip="{tip}"/>')


# ===== C1 柱状图 =====
C1_DATA = [
    {"label": "华东", "value": 4280},
    {"label": "华南", "value": 3650},
    {"label": "华北", "value": 2980},
    {"label": "西南", "value": 1820},
    {"label": "华中", "value": 1450},
]
C1_TITLE = "Q3 华东区贡献了近半增长"
C1_SUBTITLE = "单位：万元 | 2025 年 Q3"
C1_FOOTER = "数据来源：内部 CRM 系统 | 口径：含税收入"


def build_c1_svg():
    data = [d for d in C1_DATA if is_number(d.get("value"))]
    if not data:
        return no_data_svg()
    n = len(data)
    hero_idx = max(range(n), key=lambda i: abs(data[i]["value"]))

    margin = {"top": 20, "right": 24, "bottom": 48, "left": 72}
    inner_w = W - margin["left"] - margin["right"]
    inner_h = H - margin["top"] - margin["bottom"]

    max_v = max(d["value"] for d in data + [{"value": 0}])
    min_v = min(d["value"] for d in data + [{"value": 0}])
    y_max, y_min = nice_ceil(max_v), nice_floor(min_v)
    y_range = y_max - y_min

    def y(v):
        return margin["top"] + inner_h - ((v - y_min) / y_range) * inner_h

    parts = []

    # 网格线 + Y 轴刻度标签（6 条：0..yMax 五等分）
    tick_count = 5
    for i in range(tick_count + 1):
        v = y_min + (y_range / tick_count) * i
        yy = y(v)
        parts.append(line(margin["left"], yy, W - margin["right"], yy,
                          THEME["GRID"], 1))
        parts.append(text(margin["left"] - 10, yy + 4, format_num(v),
                          "end", 12, THEME["MUT"]))

    # 柱子
    band_w = inner_w / n
    bar_w = min(band_w * 0.4, 120) if n == 1 else band_w * 0.55

    for i, d in enumerate(data):
        cx = margin["left"] + band_w * i + band_w / 2
        bx = cx - bar_w / 2
        by = y(max(d["value"], 0))
        bh = abs(y(d["value"]) - y(0))
        fill = THEME["DATA"] if i == hero_idx else THEME["RAMP"][2]

        parts.append(rect(bx, by, bar_w, max(bh, 1), THEME["RADIUS"], fill,
                          f"{d['label']}: {format_num(d['value'])}"))

        # 数据标签（柱顶上方 8px）
        label_y = by - 8 if d["value"] >= 0 else by + bh + 18
        parts.append(text(cx, label_y, format_num(d["value"]),
                          "middle", 14, THEME["TXT"], weight=600))

        # X 轴类目标签
        parts.append(text(cx, H - margin["bottom"] + 24, d["label"],
                          "middle", 12, THEME["MUT"]))

    # 零线（有正有负时）
    if min_v < 0 < max_v:
        parts.append(line(margin["left"], y(0), W - margin["right"], y(0),
                          THEME["MUT"], THEME["LINE_WIDTH"]))

    return "\n    ".join(parts)


# ===== C2 条形图 =====
C2_DATA = [
    {"label": "华东区客户服务中心", "value": 94},
    {"label": "华南区客户服务中心", "value": 87},
    {"label": "华北区客户服务中心", "value": 82},
    {"label": "西南区客户服务中心", "value": 76},
    {"label": "华中区客户服务中心", "value": 71},
    {"label": "西北区客户服务中心", "value": 65},
    {"label": "东北区客户服务中心", "value": 58},
]
C2_TITLE = "客户满意度排名：华东区领跑全国"
C2_SUBTITLE = "单位：分（百分制） | 2025 年 Q3"
C2_FOOTER = "数据来源：客户满意度调研 | 样本量：12,847 份有效问卷"


def build_c2_svg():
    # 按数值降序（第一名在顶）
    data = sorted(
        [d for d in C2_DATA if is_number(d.get("value"))],
        key=lambda d: -d["value"],
    )
    if not data:
        return no_data_svg()
    n = len(data)
    hero_idx = max(range(n), key=lambda i: abs(data[i]["value"]))

    # 左边距 = 最长类目标签宽度 + 16，封顶 280（静态估算，替代 canvas 测量）
    max_label_w = max(estimate_text_width(d["label"], 12) for d in data)
    label_margin = min(math.ceil(max_label_w) + 16, 280)

    margin = {"top": 20, "right": 80, "bottom": 40, "left": label_margin}
    inner_w = W - margin["left"] - margin["right"]
    inner_h = H - margin["top"] - margin["bottom"]

    max_v = max(d["value"] for d in data + [{"value": 0}])
    min_v = min(d["value"] for d in data + [{"value": 0}])
    x_max, x_min = nice_ceil(max_v), nice_floor(min_v)
    x_range = x_max - x_min

    def x(v):
        return margin["left"] + ((v - x_min) / x_range) * inner_w

    parts = []

    # 竖向网格线 + X 轴刻度标签（6 条：0..xMax 五等分）
    tick_count = 5
    for i in range(tick_count + 1):
        v = x_min + (x_range / tick_count) * i
        xx = x(v)
        parts.append(line(xx, margin["top"], xx, H - margin["bottom"],
                          THEME["GRID"], 1))
        parts.append(text(xx, H - margin["bottom"] + 20, format_num(v),
                          "middle", 12, THEME["MUT"]))

    # 条形
    band_h = inner_h / n
    bar_h = min(band_h * 0.5, 48) if n == 1 else band_h * 0.55

    for i, d in enumerate(data):
        cy = margin["top"] + band_h * i + band_h / 2
        by = cy - bar_h / 2
        bx = x(min(d["value"], 0))
        bw = abs(x(d["value"]) - x(0))
        fill = THEME["DATA"] if i == hero_idx else THEME["RAMP"][2]

        parts.append(rect(bx, by, max(bw, 1), bar_h, THEME["RADIUS"], fill,
                          f"{d['label']}: {format_num(d['value'])}"))

        # 数据标签（条形末端外侧 8px）
        if d["value"] >= 0:
            label_x, anchor = x(d["value"]) + 8, "start"
        else:
            label_x, anchor = x(d["value"]) - 8, "end"
        parts.append(text(label_x, cy + 5, format_num(d["value"]),
                          anchor, 14, THEME["TXT"], weight=600))

        # Y 轴类目标签（左侧）
        parts.append(text(margin["left"] - 10, cy + 4, d["label"],
                          "end", 12, THEME["MUT"]))

    # 零线（有正有负时）
    if min_v < 0 < max_v:
        parts.append(line(x(0), margin["top"], x(0), H - margin["bottom"],
                          THEME["MUT"], THEME["LINE_WIDTH"]))

    return "\n    ".join(parts)


# ===== C3 折线图 =====
# 数据：两条序列——今年 vs 去年同期，12 个月
C3_DATA = {
    "labels": ["1月", "2月", "3月", "4月", "5月", "6月",
               "7月", "8月", "9月", "10月", "11月", "12月"],
    "series": [
        {"name": "2025 年", "values": [820, 932, 901, 934, 1290, 1330, 1320, 1450, 1380, 1520, 1610, 1750]},
        {"name": "2024 年", "values": [620, 710, 680, 720, 890, 940, 910, 1020, 980, 1080, 1150, 1240]},
    ],
}
C3_TITLE = "下半年用户增长提速，11 月创新高"
C3_SUBTITLE = "单位：万人 | 2024–2025 年月度活跃用户"
C3_FOOTER = "数据来源：产品分析平台 | 口径：月活跃去重用户"
# 面积模式开关（True = 填充面积图，False = 纯线图）
C3_FILL_AREA = False


def build_c3_svg(fill_area=False):
    labels = C3_DATA.get("labels", [])
    series = C3_DATA.get("series", [])
    if (not labels or not series or
            any(len(s.get("values", [])) != len(labels) for s in series) or
            any(not is_number(v) for s in series for v in s.get("values", []))):
        return no_data_svg()
    n_points = len(labels)
    n_series = len(series)

    margin = {"top": 40, "right": 40, "bottom": 48, "left": 72}
    inner_w = W - margin["left"] - margin["right"]
    inner_h = H - margin["top"] - margin["bottom"]

    # Y 轴范围必须包含 0；有负数时以零线分隔正负值。
    all_vals = [v for s in series for v in s["values"]]
    y_max = nice_ceil(max(all_vals + [0]))
    y_min = nice_floor(min(all_vals + [0]))
    y_range = y_max - y_min

    def y(v):
        return margin["top"] + inner_h - ((v - y_min) / y_range) * inner_h

    def x(i):
        if n_points == 1:
            return margin["left"] + inner_w / 2
        return margin["left"] + (i / (n_points - 1)) * inner_w

    parts = []

    # ── 网格线 + Y 轴刻度 ──
    tick_count = 5
    for i in range(tick_count + 1):
        v = y_min + (y_range / tick_count) * i
        yy = y(v)
        parts.append(line(margin["left"], yy, W - margin["right"], yy,
                          THEME["GRID"], 1))
        parts.append(text(margin["left"] - 10, yy + 4, format_num(v),
                          "end", 12, THEME["MUT"]))

    # ── X 轴标签（间隔抽取，避免拥挤） ──
    # 最多显示 ~8 个标签
    max_labels = 8
    step = max(1, math.ceil(n_points / max_labels))
    for i in range(0, n_points, step):
        parts.append(text(x(i), H - margin["bottom"] + 24, labels[i],
                          "middle", 12, THEME["MUT"]))

    # ── 图例（右上角） ──
    legend_x = W - margin["right"]
    legend_y = margin["top"] - 16
    for si in range(n_series - 1, -1, -1):
        s = series[si]
        color = THEME["DATA"] if si == 0 else THEME["RAMP"][2]
        name_w = estimate_text_width(s["name"], 12)
        parts.append(text(legend_x, legend_y, s["name"],
                          "end", 12, THEME["TXT"], weight=600))
        legend_x -= name_w + 8
        # 图例色线
        parts.append(line(legend_x - 20, legend_y - 4, legend_x, legend_y - 4,
                          color, THEME["LINE_WIDTH"]))
        legend_x -= 20 + 16  # 线长 + 间距

    # ── 数据线 + 面积 + 数据点 ──
    for si, s in enumerate(series):
        color = THEME["DATA"] if si == 0 else THEME["RAMP"][2]
        values = s["values"]

        # 构建 path
        points = [(x(i), y(v)) for i, v in enumerate(values)]
        path_d = "M " + " L ".join(f"{fmt(px)} {fmt(py)}" for px, py in points)

        # 面积填充（在数据线下面）
        if fill_area:
            area_d = path_d + f" L {fmt(points[-1][0])} {fmt(y(0))} L {fmt(points[0][0])} {fmt(y(0))} Z"
            parts.append(f'<path d="{area_d}" fill="{color}" opacity="0.12" stroke="none"/>')

        # 数据线
        parts.append(f'<path d="{path_d}" fill="none" stroke="{color}" '
                     f'stroke-width="{THEME["LINE_WIDTH"]}" stroke-linejoin="round" stroke-linecap="round"/>')

        # 数据点（小圆点）
        for pi, (px, py) in enumerate(points):
            parts.append(f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="4" '
                         f'fill="{color}" stroke="{THEME["BG"]}" stroke-width="1.5" '
                         f'data-tip="{s["name"]} {labels[pi]}: {format_num(values[pi])}"/>')

        # 关键数据标签：首点、末点、最大值、最小值
        n = len(values)
        max_idx = values.index(max(values))
        min_idx = values.index(min(values))
        key_indices = {0, n - 1, max_idx, min_idx}
        for pi in sorted(key_indices):
            if pi < 0 or pi >= n:
                continue
            px, py = points[pi]
            label_y = py - 12
            # 末点标签右侧对齐防溢出
            anchor = "middle"
            if pi == n - 1 and px > W - margin["right"] - 40:
                anchor = "end"
                px += 4
            parts.append(text(px, label_y, format_num(values[pi]),
                              anchor, 14, THEME["TXT"], weight=600))

    return "\n    ".join(parts)


# ===== C4 环形图 =====
C4_DATA = [
    {"label": "华东区", "value": 4280},
    {"label": "华南区", "value": 3650},
    {"label": "华北区", "value": 2980},
    {"label": "其他区", "value": 3270},
]
C4_TITLE = "华东区贡献近半营收"
C4_SUBTITLE = "单位：万元 | 2025 年 Q3 营收构成"
C4_FOOTER = "数据来源：内部 CRM 系统 | 口径：含税收入"


def build_c4_svg():
    # 环形图只接受正值；空值、零和负数不参与构成计算。
    data = [d for d in C4_DATA if is_number(d.get("value")) and d["value"] > 0]
    if not data:
        return no_data_svg()
    n = len(data)
    total = sum(d["value"] for d in data)

    # 环形图参数
    cx, cy = W / 2, H / 2 + 10  # 中心点（略下移，给标题留空间）
    outer_r = min(W, H) * 0.32   # 外半径
    inner_r = outer_r * 0.55     # 内半径（环形厚度）
    label_r = outer_r + 24       # 标签位置半径

    # 颜色分配：≤4 类用 CAT，>4 类降级 RAMP
    if n <= 4:
        colors = THEME["CAT"]
    else:
        colors = THEME["RAMP"]

    # 找主角（最大值）
    hero_idx = max(range(n), key=lambda i: data[i]["value"])

    # 计算角度（从 12 点开始，顺时针）
    angles = []
    start = -90  # 12 点方向
    for d in data:
        sweep = (d["value"] / total) * 360
        angles.append((start, start + sweep))
        start += sweep

    parts = []

    # ── 扇区 ──
    for i, d in enumerate(data):
        a0, a1 = angles[i]
        # 主角用 HERO 色，其余按数值排名分配（跳过 HERO 色，避免重复）
        if i == hero_idx:
            color = THEME["HERO"]
        else:
            # 非主角按数值降序排名
            non_hero_sorted = sorted(
                [(idx, d_) for idx, d_ in enumerate(data) if idx != hero_idx],
                key=lambda x: -x[1]["value"]
            )
            rank = next(r for r, (idx, _) in enumerate(non_hero_sorted) if idx == i)
            # 过滤掉 HERO 色后的可用颜色
            available = [c for c in colors if c != THEME["HERO"]]
            color = available[rank % len(available)]

        # 转换为弧度
        rad0 = math.radians(a0)
        rad1 = math.radians(a1)

        # 外弧
        x0o = cx + outer_r * math.cos(rad0)
        y0o = cy + outer_r * math.sin(rad0)
        x1o = cx + outer_r * math.cos(rad1)
        y1o = cy + outer_r * math.sin(rad1)

        # 内弧
        x0i = cx + inner_r * math.cos(rad0)
        y0i = cy + inner_r * math.sin(rad0)
        x1i = cx + inner_r * math.cos(rad1)
        y1i = cy + inner_r * math.sin(rad1)

        large_arc = 1 if (a1 - a0) > 180 else 0

        path_d = (
            f"M {fmt(x0i)} {fmt(y0i)} "
            f"L {fmt(x0o)} {fmt(y0o)} "
            f"A {fmt(outer_r)} {fmt(outer_r)} 0 {large_arc} 1 {fmt(x1o)} {fmt(y1o)} "
            f"L {fmt(x1i)} {fmt(y1i)} "
            f"A {fmt(inner_r)} {fmt(inner_r)} 0 {large_arc} 0 {fmt(x0i)} {fmt(y0i)} "
            f"Z"
        )

        parts.append(f'<path d="{path_d}" fill="{color}" '
                     f'data-tip="{d["label"]}: {format_num(d["value"])} ({d["value"]/total*100:.1f}%)"/>')

        # ── 标签（扇区外侧） ──
        mid_angle = math.radians((a0 + a1) / 2)
        lx = cx + label_r * math.cos(mid_angle)
        ly = cy + label_r * math.sin(mid_angle)

        # 根据象限调整锚点
        cos_mid = math.cos(mid_angle)
        if abs(cos_mid) < 0.3:
            anchor = "middle"
        elif cos_mid > 0:
            anchor = "start"
        else:
            anchor = "end"

        pct = d["value"] / total * 100
        label_text = f'{d["label"]} {pct:.1f}%'
        parts.append(text(lx, ly, label_text, anchor, 14, THEME["TXT"], weight=600))

    # ── 中心文字（总计） ──
    parts.append(text(cx, cy - 8, format_num(total), "middle", 28, THEME["TXT"], weight=700))
    parts.append(text(cx, cy + 16, "总计", "middle", 14, THEME["MUT"]))

    return "\n    ".join(parts)


# ===== C5 堆叠柱 =====
# 数据：4 个区域 × 3 个产品线的营收构成
C5_DATA = {
    "categories": ["华东区", "华南区", "华北区", "西南区"],
    "series": [
        {"name": "产品 A", "values": [1800, 1500, 1200, 800]},
        {"name": "产品 B", "values": [1400, 1200, 980, 620]},
        {"name": "产品 C", "values": [1080, 950, 800, 400]},
    ],
}
C5_TITLE = "产品 A 仍是各区域营收主力"
C5_SUBTITLE = "单位：万元 | 2025 年 Q3 各区域产品营收构成"
C5_FOOTER = "数据来源：内部 CRM 系统 | 口径：含税收入"


def build_c5_svg():
    categories = C5_DATA.get("categories", [])
    raw_series = C5_DATA.get("series", [])
    if not categories or not raw_series:
        return no_data_svg()
    series = []
    for item in raw_series[:4]:
        values = item.get("values", [])
        normalized = [
            value if is_number(value) and value >= 0 else 0
            for value in (list(values) + [0] * len(categories))[:len(categories)]
        ]
        series.append({"name": item.get("name", "未命名"), "values": normalized})
    n_cat = len(categories)
    n_ser = len(series)

    margin = {"top": 40, "right": 24, "bottom": 48, "left": 72}
    inner_w = W - margin["left"] - margin["right"]
    inner_h = H - margin["top"] - margin["bottom"]

    # Y 轴范围：堆叠总和的最大值，从 0 开始
    totals = [sum(series[si]["values"][ci] for si in range(n_ser)) for ci in range(n_cat)]
    y_max = nice_ceil(max(totals + [0]))
    y_min = 0
    y_range = y_max - y_min

    def y(v):
        return margin["top"] + inner_h - ((v - y_min) / y_range) * inner_h

    parts = []

    # ── 网格线 + Y 轴刻度 ──
    tick_count = 5
    for i in range(tick_count + 1):
        v = y_min + (y_range / tick_count) * i
        yy = y(v)
        parts.append(line(margin["left"], yy, W - margin["right"], yy,
                          THEME["GRID"], 1))
        parts.append(text(margin["left"] - 10, yy + 4, format_num(v),
                          "end", 12, THEME["MUT"]))

    # ── 图例（右上角） ──
    legend_x = W - margin["right"]
    legend_y = margin["top"] - 16
    for si in range(n_ser - 1, -1, -1):
        s = series[si]
        color = THEME["CAT"][si % len(THEME["CAT"])]
        name_w = estimate_text_width(s["name"], 12)
        parts.append(text(legend_x, legend_y, s["name"],
                          "end", 12, THEME["TXT"], weight=600))
        legend_x -= name_w + 8
        # 图例色块
        parts.append(f'<rect x="{fmt(legend_x - 12)}" y="{fmt(legend_y - 10)}" '
                     f'width="12" height="12" rx="2" fill="{color}"/>')
        legend_x -= 12 + 16

    # ── 堆叠柱 ──
    band_w = inner_w / n_cat
    bar_w = min(band_w * 0.5, 120) if n_cat == 1 else band_w * 0.6

    for ci, cat in enumerate(categories):
        cx = margin["left"] + band_w * ci + band_w / 2
        bx = cx - bar_w / 2

        # 从底部开始堆叠
        stack_y = y(0)  # 底部位置
        for si, s in enumerate(series):
            value = s["values"][ci]
            bar_h = abs(y(value) - y(0))
            by = stack_y - bar_h

            color = THEME["CAT"][si % len(THEME["CAT"])]
            parts.append(rect(bx, by, bar_w, max(bar_h, 1), 0, color,
                              f"{cat} {s['name']}: {format_num(value)}"))

            # 数值标签（如果空间够，显示在段中心）
            if bar_h > 20:
                label_y = by + bar_h / 2 + 5
                # 根据背景色亮度选择文字颜色（简化：深色背景用白字）
                text_color = THEME["BG"] if si == 0 else THEME["TXT"]
                parts.append(text(cx, label_y, format_num(value),
                                  "middle", 12, text_color, weight=600))

            stack_y = by

        # 总计标签（柱顶上方）
        total = totals[ci]
        parts.append(text(cx, stack_y - 8, format_num(total),
                          "middle", 14, THEME["TXT"], weight=700))

        # X 轴类目标签
        parts.append(text(cx, H - margin["bottom"] + 24, cat,
                          "middle", 12, THEME["MUT"]))

    return "\n    ".join(parts)


# ===== C6 瀑布图 =====
# 数据：年初余额 → 各项增减 → 年末余额
C6_DATA = [
    {"label": "年初余额", "value": 1200, "type": "start"},
    {"label": "销售收入", "value": 850, "type": "increase"},
    {"label": "投资收益", "value": 320, "type": "increase"},
    {"label": "运营成本", "value": -480, "type": "decrease"},
    {"label": "人力成本", "value": -290, "type": "decrease"},
    {"label": "税费", "value": -150, "type": "decrease"},
    {"label": "年末余额", "value": 1450, "type": "end"},
]
C6_TITLE = "全年现金净流入 250 万"
C6_SUBTITLE = "单位：万元 | 2025 年度现金流分解"
C6_FOOTER = "数据来源：财务系统 | 口径：经营活动现金流"


def build_c6_svg():
    data = [
        d for d in C6_DATA
        if is_number(d.get("value")) and d.get("type") in {"start", "increase", "decrease", "end"}
    ]
    if not data:
        return no_data_svg()
    n = len(data)

    margin = {"top": 40, "right": 24, "bottom": 48, "left": 72}
    inner_w = W - margin["left"] - margin["right"]
    inner_h = H - margin["top"] - margin["bottom"]

    # 计算累计值
    cumulative = []
    running = 0
    for d in data:
        if d["type"] == "start":
            running = d["value"]
            cumulative.append(running)
        elif d["type"] == "end":
            cumulative.append(running)  # 终点柱的高度就是累计值
        else:
            running += d["value"]
            cumulative.append(running)

    # Y 轴范围
    all_vals = [v for v in cumulative] + [0]
    y_max = nice_ceil(max(all_vals))
    y_min = nice_floor(min(all_vals))
    y_range = y_max - y_min

    def y(v):
        return margin["top"] + inner_h - ((v - y_min) / y_range) * inner_h

    parts = []

    # ── 网格线 + Y 轴刻度 ──
    tick_count = 5
    for i in range(tick_count + 1):
        v = y_min + (y_range / tick_count) * i
        yy = y(v)
        parts.append(line(margin["left"], yy, W - margin["right"], yy,
                          THEME["GRID"], 1))
        parts.append(text(margin["left"] - 10, yy + 4, format_num(v),
                          "end", 12, THEME["MUT"]))

    # ── 瀑布柱 ──
    band_w = inner_w / n
    bar_w = min(band_w * 0.5, 80) if n == 1 else band_w * 0.6

    for i, d in enumerate(data):
        cx = margin["left"] + band_w * i + band_w / 2
        bx = cx - bar_w / 2

        if d["type"] == "start" or d["type"] == "end":
            # 起点/终点柱：从 0 到累计值
            bar_top = y(cumulative[i])
            bar_bottom = y(0)
            bar_h = abs(bar_bottom - bar_top)
            color = THEME["DATA"]
        else:
            # 增减柱：从前一个累计值到当前累计值
            prev_cum = cumulative[i - 1] if i > 0 else 0
            curr_cum = cumulative[i]
            bar_top = y(max(prev_cum, curr_cum))
            bar_bottom = y(min(prev_cum, curr_cum))
            bar_h = abs(bar_bottom - bar_top)
            # 正增长用绿色（DATA），负增长用橙红色（HERO）
            color = THEME["DATA"] if d["value"] > 0 else THEME["HERO"]

        parts.append(rect(bx, bar_top, bar_w, max(bar_h, 1), 0, color,
                          f"{d['label']}: {format_num(d['value'])}"))

        # 数值标签
        if d["type"] == "start" or d["type"] == "end":
            label_y = bar_top - 8
            label_text = format_num(d["value"])
        else:
            label_y = bar_top - 8
            label_text = f"+{format_num(d['value'])}" if d["value"] > 0 else format_num(d["value"])
        parts.append(text(cx, label_y, label_text,
                          "middle", 14, THEME["TXT"], weight=600))

        # X 轴类目标签
        parts.append(text(cx, H - margin["bottom"] + 24, d["label"],
                          "middle", 12, THEME["MUT"]))

        # 连接线（虚线，连接到下一个柱）
        if i < n - 1:
            next_cx = margin["left"] + band_w * (i + 1) + band_w / 2
            next_bx = next_cx - bar_w / 2
            connect_y = y(cumulative[i])
            parts.append(f'<line x1="{fmt(cx + bar_w/2)}" y1="{fmt(connect_y)}" '
                         f'x2="{fmt(next_bx)}" y2="{fmt(connect_y)}" '
                         f'stroke="{THEME["MUT"]}" stroke-width="1" stroke-dasharray="4,4"/>')

    return "\n    ".join(parts)


# ===== C7 甘特图 =====
# 数据：Q4 产品迭代的任务排期
C7_DATA = [
    {"task": "需求评审", "start": "10-01", "end": "10-05", "progress": 100},
    {"task": "UI 设计", "start": "10-06", "end": "10-15", "progress": 100},
    {"task": "前端开发", "start": "10-16", "end": "11-05", "progress": 85},
    {"task": "后端开发", "start": "10-16", "end": "11-08", "progress": 80},
    {"task": "联调测试", "start": "11-09", "end": "11-20", "progress": 40},
    {"task": "灰度发布", "start": "11-21", "end": "11-25", "progress": 0},
    {"task": "正式发布", "start": "11-26", "end": "11-30", "progress": 0},
]
C7_TITLE = "Q4 产品迭代排期：11 月底发布"
C7_SUBTITLE = "时间：2025 年 Q4 | 进度：截至 11 月 10 日"
C7_FOOTER = "数据来源：项目管理工具 | 负责人：产品团队"


def parse_date(date_str):
    """解析 MM-DD 格式的日期为天数（从 10-01 开始）"""
    month, day = map(int, date_str.split("-"))
    # 简化：10 月 = 0, 11 月 = 31
    days_in_oct = 31
    if month == 10:
        return day - 1
    elif month == 11:
        return days_in_oct + day - 1
    return 0


def build_c7_svg():
    data = []
    for item in C7_DATA:
        try:
            start, end = parse_date(item.get("start")), parse_date(item.get("end"))
        except (AttributeError, TypeError, ValueError):
            continue
        if end < start:
            continue
        progress = item.get("progress", 0)
        progress = progress if is_number(progress) else 0
        data.append({**item, "progress": max(0, min(100, progress))})
    if not data:
        return no_data_svg()
    n = len(data)

    # 大量留白（编辑感）
    margin = {"top": 60, "right": 60, "bottom": 50, "left": 140}
    inner_w = W - margin["left"] - margin["right"]
    inner_h = H - margin["top"] - margin["bottom"]

    # 时间范围：10-01 到 11-30（60 天）
    all_dates = []
    for d in data:
        all_dates.append(parse_date(d["start"]))
        all_dates.append(parse_date(d["end"]))
    x_min = min(all_dates)
    x_max = max(all_dates)
    x_range = max(x_max - x_min, 1)

    def x(day):
        """将天数映射到 X 坐标"""
        return margin["left"] + ((day - x_min) / x_range) * inner_w

    def date_label(day):
        """将天数转换回日期标签"""
        if day < 31:
            return f"10-{day + 1:02d}"
        else:
            return f"11-{day - 31 + 1:02d}"

    parts = []

    # ── 时间轴网格线（发丝线，每周一条） ──
    # 10-01, 10-08, 10-15, 10-22, 10-29, 11-05, 11-12, 11-19, 11-26
    tick_days = [0, 7, 14, 21, 28, 35, 42, 49, 56]
    for day in tick_days:
        if day > x_max:
            break
        xx = x(day)
        parts.append(f'<line x1="{fmt(xx)}" y1="{fmt(margin["top"])}" x2="{fmt(xx)}" y2="{fmt(H - margin["bottom"])}" '
                     f'stroke="{THEME["GRID"]}" stroke-width="0.5" opacity="0.4"/>')
        parts.append(text(xx, H - margin["bottom"] + 20, date_label(day),
                          "middle", 11, THEME["MUT"]))

    # ── 今日线（假设今天是 11-10，即 day=40） ──
    today = 40
    if x_min <= today <= x_max:
        today_x = x(today)
        parts.append(f'<line x1="{fmt(today_x)}" y1="{fmt(margin["top"] - 10)}" '
                     f'x2="{fmt(today_x)}" y2="{fmt(H - margin["bottom"])}" '
                     f'stroke="{THEME["HERO"]}" stroke-width="1.5" stroke-dasharray="4,4" opacity="0.6"/>')
        parts.append(text(today_x, margin["top"] - 16, "今日",
                          "middle", 11, THEME["HERO"], weight=600))

    # ── 任务条形 ──
    bar_h = min(inner_h / n * 0.5, 32)  # 条形高度
    band_h = inner_h / n

    # 按开始时间排序（最早的在顶部）
    sorted_data = sorted(enumerate(data), key=lambda x: parse_date(x[1]["start"]))

    for rank, (i, d) in enumerate(sorted_data):
        cy = margin["top"] + band_h * rank + band_h / 2
        by = cy - bar_h / 2

        start_day = parse_date(d["start"])
        end_day = parse_date(d["end"])
        bx = x(start_day)
        bw = x(end_day) - bx

        # 颜色：用 RAMP 明度梯（最早开始的用最深色）
        color_idx = int((rank / (n - 1)) * (len(THEME["RAMP"]) - 1)) if n > 1 else 0
        color = THEME["RAMP"][color_idx]

        # 背景条（总时长，浅色）
        parts.append(f'<rect x="{fmt(bx)}" y="{fmt(by)}" width="{fmt(bw)}" height="{fmt(bar_h)}" '
                     f'rx="4" fill="{color}" opacity="0.2" '
                     f'data-tip="{d["task"]}: {d["start"]} ~ {d["end"]}"/>')

        # 进度条（已完成部分，实心）
        if d["progress"] > 0:
            progress_w = bw * (d["progress"] / 100)
            parts.append(f'<rect x="{fmt(bx)}" y="{fmt(by)}" width="{fmt(progress_w)}" height="{fmt(bar_h)}" '
                         f'rx="4" fill="{color}" opacity="0.85" '
                         f'data-tip="{d["task"]}: {d["progress"]}% 完成"/>')

        # 任务名称（左侧）
        parts.append(text(margin["left"] - 12, cy + 4, d["task"],
                          "end", 13, THEME["TXT"], weight=600))

        # 时间段标签（条形右侧）
        time_label = f'{d["start"]} ~ {d["end"]}'
        label_x = bx + bw + 8
        # 如果右侧空间不够，放在条形内部
        if label_x + estimate_text_width(time_label, 11) > W - margin["right"]:
            label_x = bx + bw - 8
            anchor = "end"
            label_color = THEME["BG"]
        else:
            anchor = "start"
            label_color = THEME["MUT"]

        parts.append(text(label_x, cy + 4, time_label,
                          anchor, 11, label_color))

        # 进度百分比（如果未完成，显示在条形右端）
        if 0 < d["progress"] < 100:
            progress_x = bx + bw * (d["progress"] / 100)
            parts.append(text(progress_x + 6, cy + 4, f'{d["progress"]}%',
                              "start", 11, THEME["TXT"], weight=600))

    return "\n    ".join(parts)


# ===== C8 漏斗图 =====
# 数据：用户转化漏斗
C8_DATA = [
    {"stage": "访问首页", "value": 12000},
    {"stage": "注册账号", "value": 6800},
    {"stage": "完善资料", "value": 4200},
    {"stage": "首次下单", "value": 2100},
    {"stage": "复购", "value": 890},
]
C8_TITLE = "用户转化漏斗：注册转化率 57%"
C8_SUBTITLE = "单位：人次 | 2025 年 Q3"
C8_FOOTER = "数据来源：产品分析平台 | 口径：去重用户"


def build_c8_svg():
    data = [d for d in C8_DATA if is_number(d.get("value")) and d["value"] > 0]
    if not data:
        return no_data_svg()
    n = len(data)

    margin = {"top": 60, "right": 60, "bottom": 50, "left": 60}
    inner_w = W - margin["left"] - margin["right"]
    inner_h = H - margin["top"] - margin["bottom"]

    max_v = max(d["value"] for d in data)

    # 漏斗参数
    band_h = inner_h / n
    bar_h = band_h * 0.7
    center_x = W / 2

    parts = []

    # ── 漏斗层 ──
    for i, d in enumerate(data):
        cy = margin["top"] + band_h * i + band_h / 2
        by = cy - bar_h / 2

        # 宽度 ∝ 数值
        width = (d["value"] / max_v) * inner_w * 0.85
        bx = center_x - width / 2

        # 颜色：RAMP 明度梯（从上到下，由深到浅）
        # 前 4 层各占一个色阶，第 5+ 层用最浅色
        color_idx = min(i, len(THEME["RAMP"]) - 1)
        color = THEME["RAMP"][color_idx]

        # 漏斗层（梯形，用 path 绘制）
        # 上一层宽度
        if i > 0:
            prev_width = (data[i-1]["value"] / max_v) * inner_w * 0.85
            prev_bx = center_x - prev_width / 2
            prev_by = margin["top"] + band_h * (i-1) + band_h / 2 + bar_h / 2

            # 连接梯形的四个角
            path_d = (
                f"M {fmt(prev_bx)} {fmt(prev_by)} "
                f"L {fmt(prev_bx + prev_width)} {fmt(prev_by)} "
                f"L {fmt(bx + width)} {fmt(by)} "
                f"L {fmt(bx)} {fmt(by)} "
                f"Z"
            )
            parts.append(f'<path d="{path_d}" fill="{color}" opacity="0.3" stroke="none"/>')

        # 当前层矩形
        parts.append(f'<rect x="{fmt(bx)}" y="{fmt(by)}" width="{fmt(width)}" height="{fmt(bar_h)}" '
                     f'rx="4" fill="{color}" opacity="0.85" '
                     f'data-tip="{d["stage"]}: {format_num(d["value"])}"/>')

        # 阶段名称（中心）
        parts.append(text(center_x, cy - 4, d["stage"],
                          "middle", 14, THEME["BG"], weight=700))

        # 数值（中心，阶段名下方）
        parts.append(text(center_x, cy + 14, format_num(d["value"]),
                          "middle", 13, THEME["BG"], weight=600))

        # 转化率（级间，右侧）
        if i > 0:
            conv_rate = (d["value"] / data[i-1]["value"]) * 100
            conv_x = W - margin["right"] + 20
            conv_y = margin["top"] + band_h * i - band_h / 2
            parts.append(text(conv_x, conv_y + 4, f"↓ {conv_rate:.1f}%",
                              "start", 12, THEME["MUT"], weight=600))

    return "\n    ".join(parts)


# ===== C9 指标卡 =====
# 数据：单 KPI
C9_DATA = {
    "value": 12847,
    "unit": "万元",
    "label": "Q3 营收",
    "yoy": 23.5,  # 同比增长率
    "mom": 8.2,   # 环比增长率
}
C9_TITLE = "Q3 营收 1.28 亿元"
C9_SUBTITLE = "同比 +23.5% | 环比 +8.2%"
C9_FOOTER = "数据来源：财务系统 | 口径：含税收入"


def build_c9_svg():
    d = C9_DATA
    if not is_number(d.get("value")):
        return no_data_svg()

    # 指标卡不需要 SVG 图表，用纯文本排版
    # 但为了保持一致性，还是用 SVG 实现
    parts = []

    center_x = W / 2
    center_y = H / 2

    # ── 超大数字（主角） ──
    value_text = format_num(d["value"])
    parts.append(text(center_x, center_y - 40, value_text,
                      "middle", 96, THEME["DATA"], weight=700))

    # ── 单位 ──
    parts.append(text(center_x, center_y + 20, d["unit"],
                      "middle", 24, THEME["MUT"]))

    # ── 标签 ──
    parts.append(text(center_x, center_y + 60, d["label"],
                      "middle", 16, THEME["TXT"], weight=600))

    # ── 同比/环比（左下/右下） ──
    yoy = d.get("yoy")
    mom = d.get("mom")
    yoy_text = f"同比 {'+' if yoy > 0 else ''}{yoy:.1f}%" if is_number(yoy) else "同比 —"
    mom_text = f"环比 {'+' if mom > 0 else ''}{mom:.1f}%" if is_number(mom) else "环比 —"

    # 同比（左下）
    yoy_color = THEME["DATA"] if is_number(yoy) and yoy > 0 else THEME["HERO"]
    parts.append(text(center_x - 200, H - 120, yoy_text,
                      "middle", 18, yoy_color, weight=600))

    # 环比（右下）
    mom_color = THEME["DATA"] if is_number(mom) and mom > 0 else THEME["HERO"]
    parts.append(text(center_x + 200, H - 120, mom_text,
                      "middle", 18, mom_color, weight=600))

    return "\n    ".join(parts)


# ===== C10 对比卡 =====
# 数据：2-4 个 KPI 并列
C10_DATA = [
    {"label": "华北地区", "value": 12847, "unit": "万元", "yoy": 23.5, "mom": 8.2},
    {"label": "华东地区", "value": 15234, "unit": "万元", "yoy": 18.7, "mom": 12.4},
    {"label": "华南地区", "value": 9856, "unit": "万元", "yoy": -5.2, "mom": 3.1},
    {"label": "西南地区", "value": 7421, "unit": "万元", "yoy": 31.8, "mom": -2.5},
]
C10_TITLE = "华东营收领先，华南同比下滑"
C10_SUBTITLE = "单位：万元 | 2025 年 Q3"
C10_FOOTER = "数据来源：财务系统 | 口径：含税收入"


def build_c10_svg():
    parts = []
    data = [d for d in C10_DATA if is_number(d.get("value"))]
    if not data:
        return no_data_svg()
    n = len(data)

    # 每列宽度
    col_w = W / n

    for i, d in enumerate(data):
        cx = col_w * i + col_w / 2  # 列中心 x

        # ── 标签（顶部） ──
        parts.append(text(cx, 120, d["label"],
                          "middle", 18, THEME["TXT"], weight=600))

        # ── 数值（主角） ──
        value_text = format_num(d["value"])
        parts.append(text(cx, 260, value_text,
                          "middle", 64, THEME["DATA"], weight=700))

        # ── 单位 ──
        parts.append(text(cx, 300, d["unit"],
                          "middle", 16, THEME["MUT"]))

        # ── 同比/环比（底部） ──
        yoy = d.get("yoy")
        mom = d.get("mom")
        yoy_text = f"同比 {'↑' if yoy > 0 else '↓'} {abs(yoy):.1f}%" if is_number(yoy) else "同比 —"
        mom_text = f"环比 {'↑' if mom > 0 else '↓'} {abs(mom):.1f}%" if is_number(mom) else "环比 —"

        yoy_color = THEME["DATA"] if is_number(yoy) and yoy > 0 else THEME["HERO"]
        mom_color = THEME["DATA"] if is_number(mom) and mom > 0 else THEME["HERO"]

        parts.append(text(cx, 560, yoy_text,
                          "middle", 14, yoy_color, weight=600))
        parts.append(text(cx, 590, mom_text,
                          "middle", 14, mom_color, weight=600))

        # ── 分隔线（除了最后一列） ──
        if i < n - 1:
            sep_x = col_w * (i + 1)
            parts.append(line(sep_x, 100, sep_x, 620, THEME["GRID"], 1))

    return "\n    ".join(parts)


# ===== HTML 骨架 =====
def html_shell(kind_desc, rules, title, subtitle, footer, data, svg_body):
    t = THEME
    data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    rules_html = "\n".join(f"  - {r}" for r in rules)
    return f"""<!DOCTYPE html>
<!--
  {kind_desc}
{rules_html}
  本文件由 scripts/build_templates.py 生成，SVG 坐标已全部静态写死；
  如需改动请修改脚本后重新生成，勿手改坐标。
-->
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    /* __CSS_THEME_START__ */
    --c-bg: {t["BG"]};
    --c-txt: {t["TXT"]};
    --c-mut: {t["MUT"]};
    --c-grid: {t["GRID"]};
    --c-radius: {t["RADIUS"]}px;
    --c-font: {t["FONT"]};
    /* __CSS_THEME_END__ */
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1280px; height: 720px;
    background: var(--c-bg);
    font-family: var(--c-font);
    display: flex; justify-content: center; align-items: center;
    overflow: hidden;
  }}
  .chart-container {{
    width: 1280px; height: 720px;
    padding: 40px 48px 32px 48px;
    display: flex; flex-direction: column;
    position: relative;
  }}
  .chart-header {{ margin-bottom: 8px; flex-shrink: 0; }}
  .chart-title {{
    font-size: 24px; font-weight: 700; color: var(--c-txt);
    line-height: 1.3; letter-spacing: 0.5px;
  }}
  .chart-subtitle {{
    font-size: 14px; color: var(--c-mut); margin-top: 4px; line-height: 1.4;
  }}
  .chart-body {{
    flex: 1; min-height: 0; display: flex; justify-content: center; align-items: center;
  }}
  .chart-footer {{
    font-size: 11px; color: var(--c-mut); flex-shrink: 0;
    margin-top: 8px; line-height: 1.4;
  }}
  svg {{ display: block; width: 100%; height: 100%; }}
  .tooltip {{
    position: absolute; pointer-events: none; opacity: 0;
    background: var(--c-txt); color: var(--c-bg);
    font-size: 12px; padding: 6px 10px; border-radius: var(--c-radius);
    white-space: nowrap; transition: opacity 0.15s;
    z-index: 10;
  }}
</style>
</head>
<body>
<div class="chart-container">
  <div class="chart-header">
    <div class="chart-title">{title}</div>
    <div class="chart-subtitle">{subtitle}</div>
  </div>
  <div class="chart-body">
    <svg id="chart" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet">
    {svg_body}
    </svg>
  </div>
  <div class="chart-footer">{footer}</div>
  <div class="tooltip" id="tooltip"></div>
</div>

<script>
// ===== 主题 token（静态 SVG 模式下仅为元数据，供 gallery.html 替换引擎识别） =====
// __JS_THEME_START__
// BG: {t["BG"]}, TXT: {t["TXT"]}, MUT: {t["MUT"]}, GRID: {t["GRID"]}
// DATA: {t["DATA"]}
// RAMP: {json.dumps(t["RAMP"])}
// CAT: {json.dumps(t["CAT"])}
// HERO: {t["HERO"]}
// FONT: {t["FONT"]}
// LINE_WIDTH: {t["LINE_WIDTH"]}, RADIUS: {t["RADIUS"]}, DARK: {str(t["DARK"]).lower()}
// __JS_THEME_END__

// ===== 数据（同上，仅为元数据） =====
// __DATA_START__
// {data_js}
// __DATA_END__

// hover tooltip 增强（删除此 script 图表仍完整）
(function(){{
  var tip = document.getElementById('tooltip');
  document.querySelectorAll('[data-tip]').forEach(function(el){{
    el.addEventListener('mouseenter', function(){{
      tip.textContent = el.getAttribute('data-tip');
      tip.style.opacity = 1;
      var r = el.getBoundingClientRect();
      var c = document.querySelector('.chart-container').getBoundingClientRect();
      tip.style.left = (r.left - c.left + r.width/2 - tip.offsetWidth/2) + 'px';
      tip.style.top = (r.top - c.top - 36) + 'px';
    }});
    el.addEventListener('mouseleave', function(){{ tip.style.opacity = 0; }});
  }});
}})();
</script>
</body>
</html>
"""


def main():
    c1_rules = [
        "C1 柱状图 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：单序列 ≤10 类目；>10 类请改 C2 条形图",
        "Y 轴必须从 0 开始，禁止截断；负值按柱状长度向下延伸（仍保持 ∝ 数值）",
        "超长中文类目名：先尝试旋转 -25°，仍重叠则降级 C2",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c2_rules = [
        "C2 条形图 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：单序列，长类目名 / 排名场景；第一名在顶，按数值降序",
        "X 轴从 0 开始，禁止截断；负值向左延伸（仍保持 ∝ 数值）",
        "类目名不设字数上限（这是 C2 存在的意义）；超 20 类建议分页或降级 C1",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c3_rules = [
        "C3 折线图 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：时间趋势，≤4 条序列；>4 序列请拆图或合并",
        "Y 轴必须从 0 开始，禁止截断",
        "面积模式开关：fill_area=True 时填充半透明面积（强调量级感）",
        "X 轴标签自动抽稀（最多 ~8 个），避免拥挤",
        "数据标签只标注关键点（首/末/最大/最小），其余靠 hover 读数",
        "RAMP 按重要性分配：序列 1 = DATA（主角），其余按 RAMP 递浅",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c4_rules = [
        "C4 环形图 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：占比构成，≤6 扇区硬规则；>6 合并长尾为'其他'，仍超→降级 C2",
        "≤4 类用 CAT 色，>4 类降级 RAMP 明度梯",
        "主角（最大值）用 HERO 色，全图唯一",
        "中心显示总计数值，标签显示类目名+百分比",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c5_rules = [
        "C5 堆叠柱 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：构成 × 比较，堆叠层数 ≤4；>4 层请合并或拆图",
        "Y 轴必须从 0 开始，禁止截断",
        "堆叠层用 CAT 色（≤4 类），从底部开始按 series 顺序堆叠",
        "每段显示数值标签（空间足够时），柱顶显示总计",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c6_rules = [
        "C6 瀑布图 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：增减分解（起点→终点），财务汇报刚需",
        "Y 轴必须从 0 开始，禁止截断",
        "起点/终点柱用 DATA 色，正增长用 DATA 色，负增长用 HERO 色",
        "柱之间用虚线连接，显示累计值",
        "增减柱显示 +/- 前缀，起点终点显示绝对值",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c7_rules = [
        "C7 甘特图 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：项目排期，≤10 个任务；>10 任务请分组或拆图",
        "时间轴从最早开始日期到最晚结束日期",
        "任务按开始时间排序（最早在顶部）",
        "颜色用 RAMP 明度梯（最早开始的用最深色）",
        "背景条显示总时长（浅色），进度条显示已完成部分（实心）",
        "今日线用 HERO 色虚线标记",
        "时间段标签放条形右侧，空间不够时放内部",
    ]
    c8_rules = [
        "C8 漏斗图 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：阶段转化，3–6 级；<3 级用 C9 指标卡，>6 级请合并",
        "每层宽度 ∝ 数值，禁止截断或压缩比例",
        "颜色用 RAMP 明度梯（从上到下，由深到浅）",
        "层间用梯形连接（半透明），显示流失",
        "转化率显示在级间右侧（↓ XX%）",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c9_rules = [
        "C9 指标卡 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：单 KPI；>1 个 KPI 用 C10 对比卡",
        "超大数字是主角（96px），单位和标签是配角",
        "同比/环比显示在底部左右两侧，正增长用 DATA 色，负增长用 HERO 色",
        "极简设计，无图表元素，纯排版",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]
    c10_rules = [
        "C10 对比卡 · 局部规则（全局规则见 SKILL.md，此处不重复）",
        "数据契约：2-4 个 KPI 并列；<2 用 C9 指标卡，>4 请拆图",
        "每个 KPI 包含：标签、数值、单位、同比、环比",
        "数值用 DATA 色突出（64px），标签用 TXT 色（18px）",
        "同比/环比用箭头符号（↑/↓），正增长用 DATA 色，负增长用 HERO 色",
        "列之间用细分隔线，保持视觉呼吸感",
        "数值格式化：≥1e8 → X.XX亿；≥1e4 → X.X万；其余千分位",
    ]

    c1_html = html_shell(
        "C1 柱状图", c1_rules[1:], C1_TITLE, C1_SUBTITLE, C1_FOOTER,
        C1_DATA, build_c1_svg())
    c2_html = html_shell(
        "C2 条形图", c2_rules[1:], C2_TITLE, C2_SUBTITLE, C2_FOOTER,
        sorted(C2_DATA, key=lambda d: -d["value"]), build_c2_svg())
    c3_html = html_shell(
        "C3 折线图", c3_rules[1:], C3_TITLE, C3_SUBTITLE, C3_FOOTER,
        C3_DATA, build_c3_svg(fill_area=C3_FILL_AREA))
    c4_html = html_shell(
        "C4 环形图", c4_rules[1:], C4_TITLE, C4_SUBTITLE, C4_FOOTER,
        C4_DATA, build_c4_svg())
    c5_html = html_shell(
        "C5 堆叠柱", c5_rules[1:], C5_TITLE, C5_SUBTITLE, C5_FOOTER,
        C5_DATA, build_c5_svg())
    c6_html = html_shell(
        "C6 瀑布图", c6_rules[1:], C6_TITLE, C6_SUBTITLE, C6_FOOTER,
        C6_DATA, build_c6_svg())
    c7_html = html_shell(
        "C7 甘特图", c7_rules[1:], C7_TITLE, C7_SUBTITLE, C7_FOOTER,
        C7_DATA, build_c7_svg())
    c8_html = html_shell(
        "C8 漏斗图", c8_rules[1:], C8_TITLE, C8_SUBTITLE, C8_FOOTER,
        C8_DATA, build_c8_svg())
    c9_html = html_shell(
        "C9 指标卡", c9_rules[1:], C9_TITLE, C9_SUBTITLE, C9_FOOTER,
        C9_DATA, build_c9_svg())
    c10_html = html_shell(
        "C10 对比卡", c10_rules[1:], C10_TITLE, C10_SUBTITLE, C10_FOOTER,
        C10_DATA, build_c10_svg())

    for name, content in [("c01-bar.html", c1_html), ("c02-hbar.html", c2_html),
                           ("c03-line.html", c3_html), ("c04-donut.html", c4_html),
                           ("c05-stacked.html", c5_html), ("c06-waterfall.html", c6_html),
                           ("c07-gantt.html", c7_html), ("c08-funnel.html", c8_html),
                           ("c09-kpi.html", c9_html), ("c10-compare.html", c10_html)]:
        path = os.path.join(TPL_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print(f"已生成 {os.path.normpath(path)}（{len(content)} 字节）")


if __name__ == "__main__":
    main()
