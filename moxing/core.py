from __future__ import annotations

import base64
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "tokens" / "system.json").read_text(encoding="utf-8"))
W, H = TOKENS["geometry"]["viewbox"]


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def fmt(value: float) -> str:
    rounded = round(float(value), 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def format_num(value: float) -> str:
    if not is_number(value):
        return "—"
    absolute = abs(value)
    if absolute >= 100_000_000:
        result = f"{value / 100_000_000:.2f}".rstrip("0").rstrip(".")
        return f"{result}亿"
    if absolute >= 10_000:
        result = f"{value / 10_000:.1f}".rstrip("0").rstrip(".")
        return f"{result}万"
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.1f}".rstrip("0").rstrip(".")


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def nice_ceil(value: float) -> float:
    if value <= 0:
        return 1
    exponent = math.floor(math.log10(value))
    base = 10**exponent
    normalized = value / base
    for step in (1, 2, 2.5, 5, 10):
        if normalized <= step:
            return step * base
    return 10 * base


def nice_floor(value: float) -> float:
    return 0 if value >= 0 else -nice_ceil(-value)


def attrs(**values: Any) -> str:
    rendered = []
    for key, value in values.items():
        if value is None:
            continue
        name = key[:-1] if key.endswith("_") else key.replace("_", "-")
        rendered.append(f'{name}="{esc(value)}"')
    return " ".join(rendered)


def motion(kind: str, delay: int, *, dx: int = 0, dy: int = 0, duration: int | None = None) -> str:
    style = [f"--delay:{delay}ms", f"--dx:{dx}px", f"--dy:{dy}px"]
    if duration is not None:
        style.append(f"--duration:{duration}ms")
    return f'data-motion="{kind}" style="{";".join(style)}"'


def text(
    x: float,
    y: float,
    value: Any,
    *,
    cls: str = "label",
    anchor: str = "start",
    size: int | float | None = None,
    weight: int | None = None,
    extra: str = "",
) -> str:
    options = {
        "x": fmt(x),
        "y": fmt(y),
        "class": cls,
        "text_anchor": anchor,
        "font_size": size,
        "font_weight": weight,
    }
    return f'<text {attrs(**options)} {extra}>{esc(value)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, *, cls: str = "grid", extra: str = "") -> str:
    return f'<line {attrs(x1=fmt(x1), y1=fmt(y1), x2=fmt(x2), y2=fmt(y2), class_=cls)} {extra}/>'


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    cls: str = "data-fill",
    rx: float = 0,
    extra: str = "",
) -> str:
    return f'<rect {attrs(x=fmt(x), y=fmt(y), width=fmt(max(0, width)), height=fmt(max(0, height)), rx=fmt(rx), class_=cls)} {extra}/>'


def circle(cx: float, cy: float, radius: float, *, cls: str = "data-fill", extra: str = "") -> str:
    return f'<circle {attrs(cx=fmt(cx), cy=fmt(cy), r=fmt(max(0, radius)), class_=cls)} {extra}/>'


def path(d: str, *, cls: str = "data-stroke", extra: str = "") -> str:
    return f'<path d="{esc(d)}" class="{esc(cls)}" {extra}/>'


def polygon(points: Iterable[tuple[float, float]], *, cls: str = "data-fill", extra: str = "") -> str:
    encoded = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
    return f'<polygon points="{encoded}" class="{esc(cls)}" {extra}/>'


def group(children: Iterable[str], *, cls: str = "", extra: str = "") -> str:
    return f'<g class="{esc(cls)}" {extra}>\n' + "\n".join(children) + "\n</g>"


def cut_rect_path(x: float, y: float, width: float, height: float, cut: float = 8) -> str:
    width = max(0, width)
    height = max(0, height)
    c = min(cut, width / 2, height / 2)
    return (
        f"M {fmt(x)} {fmt(y)} H {fmt(x + width - c)} "
        f"L {fmt(x + width)} {fmt(y + c)} V {fmt(y + height)} "
        f"H {fmt(x + c)} L {fmt(x)} {fmt(y + height - c)} Z"
    )


def evidence_plate(
    x: float,
    y: float,
    index: str,
    state: str,
    value: str,
    note: str,
    *,
    delay: int = 1250,
    width: float = 220,
) -> str:
    children = [
        path(cut_rect_path(x, y, width, 94, 8), cls="panel-stroke"),
        text(x + 14, y + 21, index, cls="index muted", size=12),
        text(x + width - 14, y + 21, state.upper(), cls="index signal-text", anchor="end", size=12),
        text(x + 14, y + 55, value, cls="value", size=28, weight=650),
        text(x + 14, y + 77, note, cls="muted", size=13),
    ]
    return group(children, cls="evidence-plate", extra=motion("lock", delay, dx=-8))


def no_data(message: str = "暂无可用数据") -> str:
    return group(
        [
            line(W / 2 - 90, H / 2, W / 2 + 90, H / 2, cls="rail", extra=motion("align", 80)),
            text(W / 2, H / 2 - 18, "NO DATA", cls="index signal-text", anchor="middle", size=14, extra=motion("lock", 280)),
            text(W / 2, H / 2 + 34, message, cls="muted", anchor="middle", size=18),
        ],
        cls="empty-state",
    )


@dataclass
class ChartPage:
    chart_id: str
    slug: str
    public_name: str
    title: str
    subtitle: str
    footer: str
    svg: str
    data: Any
    total_ms: int = 1800
    surface: str = "light"
    mode: str = "editorial"


def _surface_css(name: str, values: dict[str, Any]) -> str:
    cats = values["cat"]
    return f"""
  [data-surface=\"{name}\"] {{
    --bg:{values['bg']}; --ink:{values['ink']}; --muted:{values['muted']};
    --faint:{values['faint']}; --grid:{values['grid']}; --rail:{values['rail']};
    --secondary:{values['secondary']}; --signal:{values['signal']}; --panel:{values['panel']};
    --cat-1:{cats[0]}; --cat-2:{cats[1]}; --cat-3:{cats[2]}; --cat-4:{cats[3]};
  }}"""


def _font_face_css(embed_fonts: bool) -> str:
    font_dir = ROOT / "assets" / "fonts"
    files = [
        ("Noto Sans SC", "NotoSansSC-Variable.woff2", "100 900"),
        ("Noto Serif SC", "NotoSerifSC-Variable.woff2", "100 900"),
        ("Doto", "Doto-Variable.woff2", "100 900"),
    ]
    rules = []
    for family, filename, weight in files:
        if embed_fonts:
            encoded = base64.b64encode((font_dir / filename).read_bytes()).decode("ascii")
            source = f"data:font/woff2;base64,{encoded}"
        else:
            source = f"../assets/fonts/{filename}"
        rules.append(
            f"@font-face{{font-family:'{family}';src:url('{source}') format('woff2');"
            f"font-weight:{weight};font-display:swap}}"
        )
    return "\n".join(rules)


def html_page(page: ChartPage, *, embed_fonts: bool = False) -> str:
    surfaces = "\n".join(_surface_css(name, values) for name, values in TOKENS["surfaces"].items())
    data_json = json.dumps(json_safe(page.data), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    title_font = TOKENS["typography"]["title"]
    text_font = TOKENS["typography"]["text"]
    index_font = TOKENS["typography"]["index"]
    motion_tokens = TOKENS["motion"]
    font_css = _font_face_css(embed_fonts)
    return f"""<!DOCTYPE html>
<html lang=\"zh-CN\" data-surface=\"{esc(page.surface)}\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{esc(page.title)}</title>
<style>
  {font_css}
{surfaces}
  * {{ box-sizing:border-box; }}
  html,body {{ width:1280px; height:720px; margin:0; overflow:hidden; background:var(--bg); color:var(--ink); }}
  body {{ font-family:{text_font}; -webkit-font-smoothing:antialiased; }}
  .chart-container {{ width:1280px; height:720px; padding:38px 54px 28px; display:grid; grid-template-rows:124px 1fr 28px; position:relative; background:var(--bg); }}
  .chart-header {{ display:grid; grid-template-columns:170px minmax(0,1fr); align-items:start; border-top:1.5px solid var(--ink); padding:12px 122px 0 0; }}
  .chart-code {{ font-family:{index_font}; font-size:14px; letter-spacing:.08em; color:var(--muted); }}
  .chart-title {{ margin:0; font-family:{title_font}; font-size:34px; line-height:1.18; font-weight:700; letter-spacing:.01em; }}
  .chart-subtitle {{ margin-top:8px; color:var(--muted); font-size:14px; }}
  .chart-body {{ min-height:0; }}
  svg {{ display:block; width:100%; height:100%; overflow:visible; }}
  svg text {{ font-family:{text_font}; fill:var(--ink); }}
  svg .title-font {{ font-family:{title_font}; }}
  svg .index {{ font-family:{index_font}; letter-spacing:.08em; }}
  svg .muted {{ fill:var(--muted); }}
  svg .faint {{ fill:var(--faint); }}
  svg .signal-text {{ fill:var(--signal); }}
  svg .value {{ fill:var(--ink); font-variant-numeric:tabular-nums; }}
  svg .grid {{ stroke:var(--grid); stroke-width:1; fill:none; vector-effect:non-scaling-stroke; }}
  svg .rail {{ stroke:var(--rail); stroke-width:1.5; fill:none; vector-effect:non-scaling-stroke; }}
  svg .rail-strong {{ stroke:var(--ink); stroke-width:2.25; fill:none; vector-effect:non-scaling-stroke; }}
  svg .data-stroke {{ stroke:var(--ink); stroke-width:2.25; fill:none; vector-effect:non-scaling-stroke; }}
  svg .secondary-stroke {{ stroke:var(--secondary); stroke-width:1.5; fill:none; vector-effect:non-scaling-stroke; }}
  svg .signal-stroke {{ stroke:var(--signal); stroke-width:2.5; fill:none; vector-effect:non-scaling-stroke; }}
  svg .data-fill {{ fill:var(--ink); }}
  svg .secondary-fill {{ fill:var(--secondary); }}
  svg .panel-fill {{ fill:var(--panel); }}
  svg .panel-stroke {{ fill:var(--panel); stroke:var(--rail); stroke-width:1; vector-effect:non-scaling-stroke; }}
  svg .signal-fill {{ fill:var(--signal); }}
  svg .hollow {{ fill:var(--bg); stroke:var(--ink); stroke-width:1.5; vector-effect:non-scaling-stroke; }}
  svg .cat-1 {{ fill:var(--cat-1); }} svg .cat-2 {{ fill:var(--cat-2); }}
  svg .cat-3 {{ fill:var(--cat-3); }} svg .cat-4 {{ fill:var(--cat-4); }}
  .chart-footer {{ display:flex; justify-content:space-between; align-items:end; color:var(--muted); font-size:12px; letter-spacing:.02em; border-bottom:1px solid var(--grid); padding-bottom:7px; }}
  .chart-footer .mark {{ font-family:{index_font}; letter-spacing:.1em; }}
  [data-mode=\"brief\"] .evidence-plate {{ display:none; }}
  [data-mode=\"brief\"] svg .grid {{ opacity:.62; }}
  .motion-controls {{ position:absolute; right:54px; top:48px; display:flex; gap:6px; z-index:5; }}
  .motion-controls button {{ width:30px; height:30px; border:1px solid var(--rail); background:var(--bg); color:var(--ink); font-family:{index_font}; cursor:pointer; padding:0; }}
  .motion-controls button:hover {{ border-color:var(--signal); color:var(--signal); }}
  [data-motion] {{ transform-box:fill-box; transform-origin:center; }}
  @keyframes mx-align {{ from {{ opacity:0; stroke-dashoffset:1; }} to {{ opacity:1; stroke-dashoffset:0; }} }}
  @keyframes mx-dock {{ from {{ opacity:0; transform:translate(var(--dx),var(--dy)); }} to {{ opacity:1; transform:translate(0,0); }} }}
  @keyframes mx-route {{ from {{ opacity:.25; stroke-dashoffset:1; }} to {{ opacity:1; stroke-dashoffset:0; }} }}
  @keyframes mx-lock {{ 0% {{ opacity:0; transform:scale(.92); }} 68% {{ opacity:1; transform:scale(1.025); }} 100% {{ opacity:1; transform:scale(1); }} }}
  .motion-enabled.is-playing [data-motion=\"align\"] {{ stroke-dasharray:1; animation:mx-align var(--duration,{motion_tokens['align']}ms) linear var(--delay,0ms) both; }}
  .motion-enabled.is-playing [data-motion=\"dock\"] {{ animation:mx-dock var(--duration,{motion_tokens['dock']}ms) {motion_tokens['ease']} var(--delay,0ms) both; }}
  .motion-enabled.is-playing [data-motion=\"route\"] {{ stroke-dasharray:1; animation:mx-route var(--duration,{motion_tokens['route']}ms) {motion_tokens['ease']} var(--delay,0ms) both; }}
  .motion-enabled.is-playing [data-motion=\"lock\"] {{ animation:mx-lock var(--duration,{motion_tokens['lock']}ms) {motion_tokens['ease']} var(--delay,0ms) both; }}
  .motion-enabled.is-paused [data-motion] {{ animation-play-state:paused!important; }}
  @media (prefers-reduced-motion:reduce) {{ .motion-enabled.is-playing [data-motion] {{ animation:none!important; }} }}
</style>
</head>
<body>
<main class=\"chart-container\" id=\"moxing-chart\" data-total=\"{page.total_ms}\" data-mode=\"{esc(page.mode)}\">
  <header class=\"chart-header\">
    <div class=\"chart-code\">{esc(page.chart_id)} / {esc(page.public_name.upper())}</div>
    <div><h1 class=\"chart-title\">{esc(page.title)}</h1><div class=\"chart-subtitle\">{esc(page.subtitle)}</div></div>
  </header>
  <section class=\"chart-body\"><svg viewBox=\"0 0 {W} {H}\" role=\"img\" aria-label=\"{esc(page.title)}\">{page.svg}</svg></section>
  <footer class=\"chart-footer\"><span>{esc(page.footer)}</span><span class=\"mark\">MOXING / STRUCTURAL INTERFACE</span></footer>
  <nav class=\"motion-controls\" aria-label=\"动画控制\"><button type=\"button\" data-action=\"replay\" title=\"重播\">↻</button><button type=\"button\" data-action=\"pause\" title=\"暂停或继续\">Ⅱ</button><button type=\"button\" data-action=\"surface\" title=\"切换明暗\">◐</button></nav>
</main>
<script type=\"application/json\" id=\"moxing-data\">{data_json.replace('</', '<\\/')}</script>
<script>
(() => {{
  const root=document.getElementById('moxing-chart');
  const params=new URLSearchParams(location.search);
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches||params.get('motion')==='off';
  const profile=params.get('motion')||'standard';
  const scales={{brief:.72,standard:1,story:1.8}};
  const scale=scales[profile]||1;
  const total=Math.round(Number(root.dataset.total||1800)*scale);
  const baseDuration={{align:{motion_tokens['align']},dock:{motion_tokens['dock']},route:{motion_tokens['route']},lock:{motion_tokens['lock']}}};
  root.querySelectorAll('[data-motion]').forEach(el=>{{
    const rawDelay=parseFloat(el.style.getPropertyValue('--delay'))||0;
    const rawDuration=parseFloat(el.style.getPropertyValue('--duration'))||baseDuration[el.dataset.motion]||300;
    el.style.setProperty('--delay',Math.round(rawDelay*scale)+'ms');
    el.style.setProperty('--duration',Math.round(rawDuration*scale)+'ms');
  }});
  let timer=0;
  const settle=()=>{{ clearTimeout(timer); root.classList.remove('is-playing','is-paused'); root.classList.add('is-complete'); }};
  const replay=()=>{{
    clearTimeout(timer); root.classList.remove('is-playing','is-complete','is-paused'); void root.offsetWidth;
    if(reduce){{settle();return;}}
    root.style.setProperty('--motion-scale',scale); root.classList.add('motion-enabled','is-playing');
    timer=setTimeout(settle,total+120);
  }};
  const pause=()=>{{ root.classList.toggle('is-paused'); const b=root.querySelector('[data-action=pause]'); b.textContent=root.classList.contains('is-paused')?'▶':'Ⅱ'; }};
  root.querySelector('[data-action=replay]').addEventListener('click',replay);
  root.querySelector('[data-action=pause]').addEventListener('click',pause);
  root.querySelector('[data-action=surface]').addEventListener('click',()=>{{ const html=document.documentElement; html.dataset.surface=html.dataset.surface==='dark'?'light':'dark'; }});
  if(params.get('theme')==='dark') document.documentElement.dataset.surface='dark';
  window.Moxing={{replay,settle,setSurface:(v)=>document.documentElement.dataset.surface=v,ready:Promise.resolve()}};
  if(reduce) settle();
  else if('IntersectionObserver'in window){{ const io=new IntersectionObserver(e=>{{if(e[0].isIntersecting){{io.disconnect();replay();}}}},{{threshold:.35}});io.observe(root); }}
  else replay();
}})();
</script>
</body>
</html>
"""
