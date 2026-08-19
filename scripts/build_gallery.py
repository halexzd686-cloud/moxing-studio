#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_gallery.py — 生成 templates/gallery.html（验收画廊）

读取 templates/ 下的图表模板（paper 主题），为每个图型 × 每个主题
预生成一张卡片，内联到单个 gallery.html 中。

特性：
  - 双击即用，零 iframe / 零 XHR / 零外部请求
  - 默认显示 paper 主题，JS 切换显示/隐藏主题卡片组
  - 每张卡片有 960x540 缩放按钮
  - 无 JS 时至少显示 paper 主题的所有图型

运行：python scripts/build_gallery.py
"""

import os
import re
import html as html_mod

# ────────────────────────── 主题数据 ──────────────────────────

THEMES = {
    "paper": {
        "DARK": False,
        "BG": "#FAFAF7", "TXT": "#23262B", "MUT": "#8A8F98", "GRID": "#E4E3DE",
        "DATA": "#2F6B4F",
        "RAMP": ["#2F6B4F", "#5E9478", "#93BCA4", "#C5DBCF"],
        "CAT": ["#2F6B4F", "#C46A4A", "#4A6FA5", "#D9A441"],
        "HERO": "#C46A4A",
        "FONT": "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
        "LINE_WIDTH": 2, "RADIUS": 12
    },
    "ink": {
        "DARK": False,
        "BG": "#F4F1EA", "TXT": "#1F1D1A", "MUT": "#7D786C", "GRID": "#E0DCD2",
        "DATA": "#1F1D1A",
        "RAMP": ["#1F1D1A", "#4A463E", "#7D786C", "#B5B0A4"],
        "CAT": ["#1F1D1A", "#9A3B2E", "#6B7F5E", "#B08A3E"],
        "HERO": "#9A3B2E",
        "FONT": "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
        "LINE_WIDTH": 2, "RADIUS": 4
    },
    "boardroom": {
        "DARK": False,
        "BG": "#FBFAF7", "TXT": "#1B2331", "MUT": "#7A8291", "GRID": "#E5E4DF",
        "DATA": "#1E3A5F",
        "RAMP": ["#1E3A5F", "#3D5D85", "#6E89AC", "#A8BACF"],
        "CAT": ["#1E3A5F", "#B08D3E", "#7C93A8", "#8C5A4A"],
        "HERO": "#B08D3E",
        "FONT": "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
        "LINE_WIDTH": 2, "RADIUS": 8
    },
    "tech": {
        "DARK": True,
        "BG": "#16181D", "TXT": "#E8EAF0", "MUT": "#8B91A0", "GRID": "#2A2E38",
        "DATA": "#5B8DEF",
        "RAMP": ["#5B8DEF", "#7FA5F2", "#A3BDF6", "#C7D6FA"],
        "CAT": ["#5B8DEF", "#4ECBA8", "#F0A35E", "#E07A8B"],
        "HERO": "#F0A35E",
        "FONT": "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
        "LINE_WIDTH": 3, "RADIUS": 12
    },
    "mori": {
        "DARK": False,
        "BG": "#F5F4EF", "TXT": "#3A3D38", "MUT": "#8F8C82", "GRID": "#E4E2D8",
        "DATA": "#7D8F69",
        "RAMP": ["#7D8F69", "#9BAE8A", "#BAC7AD", "#D7DFCE"],
        "CAT": ["#7D8F69", "#C4A484", "#A67B7B", "#8A9BA8"],
        "HERO": "#B5724A",
        "FONT": "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
        "LINE_WIDTH": 2, "RADIUS": 12
    },
    "dawn": {
        "DARK": True,
        "BG": "#1C1B22", "TXT": "#F0EDEA", "MUT": "#98949E", "GRID": "#2E2C36",
        "DATA": "#D4A24E",
        "RAMP": ["#D4A24E", "#DFB876", "#EACD9E", "#F3E2C6"],
        "CAT": ["#D4A24E", "#8FA3BF", "#B0708C", "#7BA88F"],
        "HERO": "#E8E4DE",
        "FONT": "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
        "LINE_WIDTH": 3, "RADIUS": 12
    }
}

THEME_ORDER = ["paper", "ink", "boardroom", "tech", "mori", "dawn"]

THEME_LABELS = {
    "paper":     "paper（白纸 · 默认）",
    "ink":       "ink（墨）",
    "boardroom": "boardroom（董事会）",
    "tech":      "tech（深色科技）",
    "mori":      "mori（山野）",
    "dawn":      "dawn（破晓）",
}

# ────────────────────────── 图表元信息 ──────────────────────────

CHARTS = [
    {
        "id": "c01",
        "name": "C1 柱状图",
        "file": "c01-bar.html",
        "title": "Q3 华东区贡献了近半增长",
        "subtitle": "单位：万元 | 2025 年 Q3",
        "source": "数据来源：内部 CRM 系统 | 口径：含税收入"
    },
    {
        "id": "c02",
        "name": "C2 条形图",
        "file": "c02-hbar.html",
        "title": "客服响应时长排名：华东区最优",
        "subtitle": "单位：分钟 | 2025 年 Q3",
        "source": "数据来源：客服工单系统 | 口径：首次响应平均时长"
    },
    {
        "id": "c03",
        "name": "C3 折线图",
        "file": "c03-line.html",
        "title": "下半年用户增长提速，11 月创新高",
        "subtitle": "单位：万人 | 2024–2025 年月度活跃用户",
        "source": "数据来源：产品分析平台 | 口径：月活跃去重用户"
    },
    {
        "id": "c04",
        "name": "C4 环形图",
        "file": "c04-donut.html",
        "title": "华东区贡献近半营收",
        "subtitle": "单位：万元 | 2025 年 Q3 营收构成",
        "source": "数据来源：内部 CRM 系统 | 口径：含税收入"
    },
    {
        "id": "c05",
        "name": "C5 堆叠柱",
        "file": "c05-stacked.html",
        "title": "产品 A 仍是各区域营收主力",
        "subtitle": "单位：万元 | 2025 年 Q3 各区域产品营收构成",
        "source": "数据来源：内部 CRM 系统 | 口径：含税收入"
    },
    {
        "id": "c06",
        "name": "C6 瀑布图",
        "file": "c06-waterfall.html",
        "title": "全年现金净流入 250 万",
        "subtitle": "单位：万元 | 2025 年度现金流分解",
        "source": "数据来源：财务系统 | 口径：经营活动现金流"
    },
    {
        "id": "c07",
        "name": "C7 甘特图",
        "file": "c07-gantt.html",
        "title": "Q4 产品迭代排期：11 月底发布",
        "subtitle": "时间：2025 年 Q4 | 进度：截至 11 月 10 日",
        "source": "数据来源：项目管理工具 | 负责人：产品团队"
    },
    {
        "id": "c08",
        "name": "C8 漏斗图",
        "file": "c08-funnel.html",
        "title": "用户转化漏斗：注册转化率 57%",
        "subtitle": "单位：人次 | 2025 年 Q3",
        "source": "数据来源：产品分析平台 | 口径：去重用户"
    },
    {
        "id": "c09",
        "name": "C9 指标卡",
        "file": "c09-kpi.html",
        "title": "Q3 营收 1.28 亿元",
        "subtitle": "同比 +23.5% | 环比 +8.2%",
        "source": "数据来源：财务系统 | 口径：含税收入"
    },
    {
        "id": "c10",
        "name": "C10 对比卡",
        "file": "c10-compare.html",
        "title": "Q3 各区域营收对比",
        "subtitle": "单位：万元 | 2025 年 Q3",
        "source": "数据来源：财务系统 | 口径：含税收入"
    }
]

# ────────────────────────── 路径 ──────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_FILE = os.path.join(TEMPLATES_DIR, "gallery.html")

# ────────────────────────── 工具函数 ──────────────────────────


def build_color_map(source_theme, target_theme):
    """构建 source → target 的色值映射表（覆盖所有角色）。"""
    m = {}
    for role in ("BG", "TXT", "MUT", "GRID", "DATA", "HERO"):
        m[source_theme[role]] = target_theme[role]
    for i, c in enumerate(source_theme["RAMP"]):
        m[c] = target_theme["RAMP"][i]
    for i, c in enumerate(source_theme["CAT"]):
        m[c] = target_theme["CAT"][i]
    return m


def replace_svg_colors(svg_html, color_map):
    """替换 SVG 属性中的 fill/stroke 色值。按 key 长度降序替换避免前缀冲突。"""
    # 按 key 长度降序排列，确保较长的 hex 先被替换（避免 "#232" 替换掉 "#23262B" 的前缀）
    # 实际上 hex 色值都是 7 字符，但保险起见还是排序
    sorted_keys = sorted(color_map.keys(), key=len, reverse=True)
    for old_color in sorted_keys:
        new_color = color_map[old_color]
        # 只替换出现在 fill="..." 或 stroke="..." 属性值中的色值
        svg_html = svg_html.replace(f'fill="{old_color}"', f'fill="{new_color}"')
        svg_html = svg_html.replace(f'stroke="{old_color}"', f'stroke="{new_color}"')
    return svg_html


def extract_chart_html(template_path):
    """从模板 HTML 中提取 .chart-container 的完整 HTML。"""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取 <div class="chart-container"> ... </div>（含 tooltip）
    # 模板中 chart-container 后面跟着 <script>，我们到 </div>\n\n<script 为止
    # 用正则找到 chart-container 开始位置
    match = re.search(
        r'(<div\s+class="chart-container">.*?)\s*<script>',
        content,
        re.DOTALL
    )
    if not match:
        raise ValueError(f"无法在 {template_path} 中找到 .chart-container")

    chart_html = match.group(1).rstrip()

    # 移除 chart-container 内部的 tooltip div（gallery 自己管理 tooltip）
    chart_html = re.sub(
        r'\s*<div\s+class="tooltip"[^>]*></div>\s*',
        '\n',
        chart_html
    )

    return chart_html


def theme_css_vars(theme):
    """生成一组 CSS 变量声明字符串。"""
    return (
        f"--c-bg: {theme['BG']}; "
        f"--c-txt: {theme['TXT']}; "
        f"--c-mut: {theme['MUT']}; "
        f"--c-grid: {theme['GRID']}; "
        f"--c-radius: {theme['RADIUS']}px; "
        f"--c-font: {theme['FONT']};"
    )


# ────────────────────────── 主逻辑 ──────────────────────────

def build():
    # 1. 读取所有模板的 chart-container HTML
    chart_bodies = {}
    for chart in CHARTS:
        path = os.path.join(TEMPLATES_DIR, chart["file"])
        chart_bodies[chart["id"]] = extract_chart_html(path)
        print(f"  [ok] 读取 {chart['file']}")

    # 2. 生成所有卡片
    #    每个图型 × 每个主题 = 一张卡片
    cards_html = []
    paper = THEMES["paper"]

    for chart in CHARTS:
        raw_html = chart_bodies[chart["id"]]

        for theme_key in THEME_ORDER:
            theme = THEMES[theme_key]

            # 替换 SVG 中的色值
            color_map = build_color_map(paper, theme)
            themed_html = replace_svg_colors(raw_html, color_map)

            # 卡片的可见性：paper 默认显示
            visible = "true" if theme_key == "paper" else "false"
            display = "" if theme_key == "paper" else ' style="display:none"'

            # 缩放状态标记（JS 切换）
            card_id = f"card-{chart['id']}-{theme_key}"

            card = f'''
    <div class="card" data-theme="{theme_key}" data-chart="{chart["id"]}"{display}>
      <div class="card-header">
        <span class="card-badge">{chart["name"]}</span>
        <span class="card-theme-label">{html_mod.escape(THEME_LABELS[theme_key])}</span>
        <button class="scale-btn" data-card="{card_id}" title="切换 960×540 缩放">960×540</button>
      </div>
      <div class="card-body" id="{card_id}">
        <div class="chart-frame" data-theme-vars="{theme_key}">
          <div class="chart-viewport" style="{theme_css_vars(theme)}">
{themed_html}
          </div>
        </div>
      </div>
    </div>'''
            cards_html.append(card)

        print(f"  [ok] 生成 {chart['name']} x {len(THEME_ORDER)} 主题")

    all_cards = "\n".join(cards_html)

    # 3. 生成主题选择器选项
    theme_options = "\n      ".join(
        f'<option value="{k}"{" selected" if k == "paper" else ""}>{html_mod.escape(THEME_LABELS[k])}</option>'
        for k in THEME_ORDER
    )

    # 4. 生成主题 JS 数据（供 tooltip 和背景色使用）
    theme_js_data = "{\n"
    for k in THEME_ORDER:
        t = THEMES[k]
        theme_js_data += f'      "{k}": {{ BG: "{t["BG"]}", TXT: "{t["TXT"]}", MUT: "{t["MUT"]}", GRID: "{t["GRID"]}", DARK: {str(t["DARK"]).lower()} }},\n'
    theme_js_data = theme_js_data.rstrip(",\n") + "\n    }"

    # 5. 组装 gallery.html
    gallery = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Moxing Studio — 验收画廊</title>
<style>
  /* ── gallery 全局 ── */
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #1a1a2e;
    color: #eee;
    font-family: 'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif;
    min-height: 100vh;
    padding: 24px;
  }}
  h1 {{
    text-align: center;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 16px;
    letter-spacing: 1px;
  }}
  .controls {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }}
  .controls label {{
    font-size: 14px;
    color: #aaa;
  }}
  .controls select {{
    background: #2a2a4a;
    color: #eee;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 14px;
    cursor: pointer;
    font-family: inherit;
  }}
  .controls select:focus {{
    outline: none;
    border-color: #888;
  }}

  /* ── 网格布局 ── */
  .grid {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 32px;
    max-width: 1400px;
    margin: 0 auto;
  }}

  /* ── 卡片 ── */
  .card {{
    background: #16213e;
    border: 1px solid #333;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  }}
  .card-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    background: #1a2744;
    border-bottom: 1px solid #333;
  }}
  .card-badge {{
    background: #4a6fa5;
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 4px;
  }}
  .card-theme-label {{
    color: #aaa;
    font-size: 13px;
  }}
  .scale-btn {{
    margin-left: auto;
    background: #2a2a4a;
    color: #ccc;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    cursor: pointer;
    font-family: inherit;
  }}
  .scale-btn:hover {{
    background: #3a3a5a;
    border-color: #888;
  }}
  .scale-btn.active {{
    background: #4a6fa5;
    color: #fff;
    border-color: #4a6fa5;
  }}

  /* ── 图表视口（1280×720，通过 transform 缩放） ── */
  .card-body {{
    overflow: hidden;
    /* 默认尺寸：1280×720 缩放到容器宽度 */
    width: 100%;
    display: flex;
    justify-content: center;
  }}
  .chart-frame {{
    width: 1280px;
    height: 720px;
    overflow: hidden;
    flex-shrink: 0;
    transform-origin: top center;
  }}
  /* 960×540 缩放模式 */
  .chart-frame.scaled {{
    transform: scale(0.75);
    margin-bottom: -180px; /* 720 * 0.25，补偿缩放后的空白 */
  }}
  .chart-viewport {{
    width: 1280px;
    height: 720px;
    overflow: hidden;
  }}

  /* ── 图表模板样式（从模板中提取的公共样式，用 CSS 变量驱动） ── */
  .chart-viewport .chart-container {{
    width: 1280px; height: 720px;
    padding: 40px 48px 32px 48px;
    display: flex; flex-direction: column;
    position: relative;
    background: var(--c-bg);
    font-family: var(--c-font);
  }}
  .chart-viewport .chart-header {{
    margin-bottom: 8px; flex-shrink: 0;
  }}
  .chart-viewport .chart-title {{
    font-size: 24px; font-weight: 700; color: var(--c-txt);
    line-height: 1.3; letter-spacing: 0.5px;
  }}
  .chart-viewport .chart-subtitle {{
    font-size: 14px; color: var(--c-mut); margin-top: 4px; line-height: 1.4;
  }}
  .chart-viewport .chart-body {{
    flex: 1; min-height: 0; display: flex; justify-content: center; align-items: center;
  }}
  .chart-viewport .chart-footer {{
    font-size: 11px; color: var(--c-mut); flex-shrink: 0;
    margin-top: 8px; line-height: 1.4;
  }}
  .chart-viewport svg {{
    display: block; width: 100%; height: 100%;
  }}

  /* ── tooltip（每个 chart-frame 内只有一个） ── */
  .chart-viewport .tooltip {{
    position: absolute; pointer-events: none; opacity: 0;
    background: var(--c-txt); color: var(--c-bg);
    font-size: 12px; padding: 6px 10px; border-radius: var(--c-radius);
    white-space: nowrap; transition: opacity 0.15s;
    z-index: 10;
  }}
</style>
</head>
<body>

<h1>Moxing Studio — 验收画廊</h1>

<div class="controls">
  <label for="themeSelect">主题：</label>
  <select id="themeSelect">
      {theme_options}
  </select>
</div>

<div class="grid" id="grid">
{all_cards}
</div>

<script>
(function() {{

  // ── 主题切换 ──

  var themeSelect = document.getElementById('themeSelect');
  var grid = document.getElementById('grid');

  function switchTheme(themeKey) {{
    // 显示/隐藏对应主题的卡片
    var cards = grid.querySelectorAll('.card');
    for (var i = 0; i < cards.length; i++) {{
      var card = cards[i];
      if (card.getAttribute('data-theme') === themeKey) {{
        card.style.display = '';
      }} else {{
        card.style.display = 'none';
      }}
    }}
  }}

  themeSelect.addEventListener('change', function() {{
    switchTheme(this.value);
  }});

  // ── 960×540 缩放切换 ──

  var scaleBtns = grid.querySelectorAll('.scale-btn');
  for (var i = 0; i < scaleBtns.length; i++) {{
    scaleBtns[i].addEventListener('click', function() {{
      var cardId = this.getAttribute('data-card');
      var frame = document.getElementById(cardId);
      if (!frame) return;
      var viewport = frame.querySelector('.chart-frame');
      if (!viewport) return;

      if (viewport.classList.contains('scaled')) {{
        viewport.classList.remove('scaled');
        this.classList.remove('active');
        this.textContent = '960×540';
      }} else {{
        viewport.classList.add('scaled');
        this.classList.add('active');
        this.textContent = '1280×720';
      }}
    }});
  }}

  // ── tooltip（事件委托到每个 chart-viewport） ──

  var viewports = grid.querySelectorAll('.chart-viewport');
  for (var i = 0; i < viewports.length; i++) {{
    (function(vp) {{
      var tip = null;
      // 确保 tooltip 元素存在
      var container = vp.querySelector('.chart-container');
      if (!container) return;
      tip = container.querySelector('.tooltip');
      if (!tip) {{
        tip = document.createElement('div');
        tip.className = 'tooltip';
        container.appendChild(tip);
      }}

      var bars = vp.querySelectorAll('[data-tip]');
      for (var j = 0; j < bars.length; j++) {{
        (function(el, tipEl, vpEl) {{
          el.addEventListener('mouseenter', function() {{
            tipEl.textContent = el.getAttribute('data-tip');
            tipEl.style.opacity = 1;
            var r = el.getBoundingClientRect();
            var c = vpEl.querySelector('.chart-container').getBoundingClientRect();
            tipEl.style.left = (r.left - c.left + r.width/2 - tipEl.offsetWidth/2) + 'px';
            tipEl.style.top = (r.top - c.top - 36) + 'px';
          }});
          el.addEventListener('mouseleave', function() {{
            tipEl.style.opacity = 0;
          }});
        }})(bars[j], tip, vp);
      }}
    }})(viewports[i]);
  }}

}})();
</script>

</body>
</html>
'''

    # 6. 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(gallery)

    # 统计
    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    card_count = len(CHARTS) * len(THEME_ORDER)
    print(f"\n[done] 生成 {OUTPUT_FILE}")
    print(f"   {len(CHARTS)} 图型 x {len(THEME_ORDER)} 主题 = {card_count} 张卡片")
    print(f"   文件大小：{size_kb:.1f} KB")


if __name__ == "__main__":
    print("build_gallery.py — 生成验收画廊")
    print()
    build()
