from __future__ import annotations

import base64
import html
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "tokens" / "system.json").read_text(encoding="utf-8"))
PRESENTATION_CONTRACT = json.loads((ROOT / "tokens" / "presentation-modes.json").read_text(encoding="utf-8"))
PRESENTATION_TARGETS = {
    item["id"]: {"A": "direct", "B": "embedded", "C": "interface"}[item["mode"]]
    for item in PRESENTATION_CONTRACT["charts"]
}
PRESENTATION_LOCK_MODES = {
    item["id"]: item.get("lockMode", "explicit")
    for item in PRESENTATION_CONTRACT["charts"]
}
PRESENTATION_LINE_TRACES = {
    item["id"]: bool(item.get("lineTrace", False))
    for item in PRESENTATION_CONTRACT["charts"]
}
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


def motion(
    kind: str,
    delay: int,
    *,
    dx: int = 0,
    dy: int = 0,
    duration: int | None = None,
    brief: int | None = None,
    story: int | None = None,
    duration_brief: int | None = None,
    duration_story: int | None = None,
    choreo: str | None = None,
) -> str:
    style = [f"--delay:{delay}ms", f"--dx:{dx}px", f"--dy:{dy}px"]
    if duration is not None:
        style.append(f"--duration:{duration}ms")
    if brief is not None:
        style.append(f"--delay-brief:{brief}ms")
    if story is not None:
        style.append(f"--delay-story:{story}ms")
    if duration_brief is not None:
        style.append(f"--duration-brief:{duration_brief}ms")
    if duration_story is not None:
        style.append(f"--duration-story:{duration_story}ms")
    choreography = f' data-choreo="{esc(choreo)}"' if choreo else ""
    return f'data-motion="{kind}"{choreography} style="{";".join(style)}"'


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
    brief: int | None = None,
    story: int | None = None,
    choreo: str | None = None,
) -> str:
    children = [
        path(cut_rect_path(x, y, width, 94, 8), cls="panel-stroke"),
        text(x + 14, y + 21, index, cls="index muted", size=12),
        text(x + width - 14, y + 21, state.upper(), cls="index signal-text", anchor="end", size=12),
        text(x + 14, y + 55, value, cls="value", size=28, weight=650),
        text(x + 14, y + 77, note, cls="muted", size=13),
    ]
    return group(
        children,
        cls="evidence-plate",
        extra=motion("lock", delay, dx=-8, brief=brief, story=story, choreo=choreo),
    )


def no_data(message: str = "暂无可用数据") -> str:
    return group(
        [
            line(W / 2 - 90, H / 2, W / 2 + 90, H / 2, cls="rail", extra=motion("align", 80)),
            text(W / 2, H / 2 - 18, "NO DATA", cls="index signal-text", anchor="middle", size=14, extra=motion("lock", 280)),
            text(W / 2, H / 2 + 34, message, cls="muted", anchor="middle", size=18),
        ],
        cls="empty-state",
    )


@dataclass(frozen=True)
class DirectCanvas:
    """Full-width chart carrier with no detached evidence container."""

    foreground_svg: str = ""
    plot_svg: str = ""
    lock_delay: int = 980
    lock_delay_brief: int | None = None
    lock_delay_story: int | None = None
    compiled_motion: bool = False
    mode: str = field(init=False, default="direct")


@dataclass(frozen=True)
class EmbeddedEvidence:
    """Full-width chart carrier with evidence anchored in natural whitespace."""

    evidence_id: str
    evidence_svg: str
    foreground_svg: str
    lock_delay: int = 980
    plot_svg: str = ""
    evidence_delay: int = 760
    evidence_delay_brief: int | None = None
    evidence_delay_story: int | None = None
    lock_delay_brief: int | None = None
    lock_delay_story: int | None = None
    compiled_motion: bool = False
    mode: str = field(init=False, default="embedded")


@dataclass(frozen=True)
class EvidenceInterface:
    """Split chart carrier with a reserved evidence bay and terminal."""

    evidence_id: str
    evidence_viewbox: str
    plot_x: float
    lock_delay: int
    evidence_svg: str
    foreground_svg: str
    plot_right: float = W
    mode: str = field(init=False, default="interface")


# Backward-compatible builder name. New work should use EvidenceInterface.
PrecisionInterface = EvidenceInterface
PresentationCarrier = DirectCanvas | EmbeddedEvidence | EvidenceInterface


@dataclass
class ChartArtwork:
    """Chart geometry plus an explicit presentation carrier."""

    svg: str
    presentation: PresentationCarrier | None = None
    precision: EvidenceInterface | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.presentation is not None and self.precision is not None:
            raise ValueError("use presentation or legacy precision, not both")
        if self.presentation is None:
            self.presentation = self.precision or DirectCanvas()


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
    family: str = "STRUCT"
    data_signature: str = "—"
    interface_state: str = "READY"
    total_ms: int = 1800
    profile_totals: dict[str, int] = field(default_factory=dict)
    choreography: str = "structural"
    surface: str = "light"
    mode: str = "editorial"
    presentation: PresentationCarrier = field(default_factory=DirectCanvas)
    presentation_target: str = "direct"
    lock_mode: str = "explicit"
    line_trace: bool = False


def _surface_css(name: str, values: dict[str, Any]) -> str:
    cats = values["cat"]
    return f"""
  [data-surface=\"{name}\"] {{
    --bg:{values['bg']}; --ink:{values['ink']}; --muted:{values['muted']};
    --matrix-strong:{values['matrixStrong']}; --matrix-quiet:{values['matrixQuiet']};
    --faint:{values['faint']}; --grid:{values['grid']}; --rail:{values['rail']};
    --secondary:{values['secondary']}; --signal:{values['signal']}; --on-signal:{values['onSignal']}; --panel:{values['panel']};
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
    interface_tokens = TOKENS["interface"]
    motion_tokens = TOKENS["motion"]
    precision_motion = motion_tokens["precision"]
    font_css = _font_face_css(embed_fonts)
    display_code = f"C{int(page.chart_id[1:]):02d}" if page.chart_id[1:].isdigit() else page.chart_id
    header_ticks = "<i></i>" * 16
    presentation = page.presentation
    carrier_name = presentation.mode
    lock_mode = page.lock_mode if page.lock_mode in {"implicit", "micro", "explicit"} else "explicit"
    foreground_svg = "" if lock_mode == "implicit" else presentation.foreground_svg
    interface = presentation if isinstance(presentation, EvidenceInterface) else None
    embedded = presentation if isinstance(presentation, EmbeddedEvidence) else None
    direct = presentation if isinstance(presentation, DirectCanvas) else None
    compiled_direct = bool(direct and direct.compiled_motion)
    compiled_embedded = bool(embedded and embedded.compiled_motion)
    motion_system = "presentation-v2.1" if compiled_direct or compiled_embedded else ("precision-v2.1" if interface else "legacy")
    motion_revision = "motion-v2" if motion_system != "legacy" else "legacy"
    motion_strategy = (
        "trace-overlay"
        if page.line_trace
        else "evidence-interface"
        if interface
        else "data-reveal"
    )
    html_interface = ' data-interface="precision-v2.1"' if interface else ""
    root_interface = ' data-interface="precision-v2.1"' if interface else ""
    if interface:
        plot_width = interface.plot_right - interface.plot_x
        body_markup = f'''<section class="chart-body pi-split-body">
    <aside class="pi-evidence-bay" aria-label="{esc(interface.evidence_id)} evidence bay" style="--pi-evidence-delay:{precision_motion['evidence']['delay']}ms;--pi-terminal-delay:{max(0, interface.lock_delay - 120)}ms">
      <span class="pi-evidence-bay__label">EVIDENCE / BAY</span>
      <svg class="pi-evidence-svg" viewBox="{esc(interface.evidence_viewbox)}" aria-hidden="true">{interface.evidence_svg}</svg>
      <div class="pi-bay-terminal"><span>{esc(interface.evidence_id)}</span><i></i><b></b></div>
    </aside>
    <svg class="pi-data-field" viewBox="{fmt(interface.plot_x)} 0 {fmt(plot_width)} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{esc(page.title)}" style="--pi-lock-delay:{interface.lock_delay}ms">{page.svg}<g class="pi-overlay pi-overlay--foreground pi-target-lock">{foreground_svg}</g></svg>
  </section>'''
    elif embedded:
        plot_layer = f'<g class="pm-plot-layer">{embedded.plot_svg}</g>' if embedded.plot_svg else ""
        evidence_brief = embedded.evidence_delay_brief if embedded.evidence_delay_brief is not None else round(embedded.evidence_delay * .62)
        evidence_story = embedded.evidence_delay_story if embedded.evidence_delay_story is not None else round(embedded.evidence_delay * 1.8)
        lock_brief = embedded.lock_delay_brief if embedded.lock_delay_brief is not None else round(embedded.lock_delay * .62)
        lock_story = embedded.lock_delay_story if embedded.lock_delay_story is not None else round(embedded.lock_delay * 1.8)
        target_layer = f'<g class="pm-target-lock">{foreground_svg}</g>' if foreground_svg else ""
        body_markup = f'''<section class="chart-body pm-embedded-body">
    <svg class="pm-data-field pm-embedded-field" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(page.title)}" style="--pm-evidence-delay:{embedded.evidence_delay}ms;--pm-evidence-delay-brief:{evidence_brief}ms;--pm-evidence-delay-story:{evidence_story}ms;--pm-lock-delay:{embedded.lock_delay}ms;--pm-lock-delay-brief:{lock_brief}ms;--pm-lock-delay-story:{lock_story}ms"><g class="pm-data-field-layer">{page.svg}</g>{plot_layer}<g class="pm-local-evidence" aria-label="{esc(embedded.evidence_id)} local evidence">{embedded.evidence_svg}</g>{target_layer}</svg>
  </section>'''
    else:
        foreground = f'<g class="pm-target-lock">{foreground_svg}</g>' if foreground_svg else ""
        plot_layer = f'<g class="pm-plot-layer">{presentation.plot_svg}</g>' if direct and direct.plot_svg else ""
        direct_style = ""
        if direct:
            brief_delay = direct.lock_delay_brief if direct.lock_delay_brief is not None else round(direct.lock_delay * .62)
            story_delay = direct.lock_delay_story if direct.lock_delay_story is not None else round(direct.lock_delay * 1.8)
            direct_style = f' style="--pm-lock-delay:{direct.lock_delay}ms;--pm-lock-delay-brief:{brief_delay}ms;--pm-lock-delay-story:{story_delay}ms"'
        body_markup = f'<section class="chart-body pm-direct-body"><svg class="pm-direct-field" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(page.title)}"{direct_style}><g class="pm-data-field-layer">{page.svg}</g>{plot_layer}{foreground}</svg></section>'
    return f"""<!DOCTYPE html>
<html lang=\"zh-CN\" data-surface=\"{esc(page.surface)}\"{html_interface}>
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
  .chart-container {{ width:1280px; height:720px; padding:38px 54px 28px; display:grid; grid-template-rows:{interface_tokens['headerHeight']}px 1fr 28px; position:relative; background:var(--bg); }}
  .chart-header {{ display:grid; grid-template-columns:{interface_tokens['codeWidth']}px minmax(0,1fr); column-gap:{interface_tokens['headerGap']}px; align-items:start; border-top:1.5px solid var(--ink); padding:10px 122px 0 0; position:relative; }}
  .chart-code {{ align-self:start; font-family:{index_font}; font-variation-settings:'ROND' 0,'wght' 650; letter-spacing:.055em; color:var(--matrix-strong); }}
  .mx-code {{ height:84px; display:grid; grid-template-rows:20px 1fr 18px; border-left:2px solid var(--ink); padding-left:12px; position:relative; }}
  .mx-code::after {{ content:""; position:absolute; left:-2px; bottom:0; width:18px; height:2px; background:var(--signal); }}
  .mx-code__top,.mx-code__state {{ display:flex; justify-content:space-between; align-items:center; gap:8px; font-size:11px; color:var(--matrix-strong); font-weight:700; }}
  .mx-code__top strong {{ font-size:14px; color:var(--matrix-strong); font-weight:720; }}
  .mx-code__name {{ align-self:center; max-width:138px; font-size:12px; line-height:1.2; color:var(--matrix-strong); }}
  .mx-code__state {{ justify-content:flex-start; color:var(--signal); }}
  .mx-dots {{ display:grid; grid-template-columns:repeat(3,3px); grid-auto-rows:3px; gap:2px; margin-right:3px; }}
  .mx-dots i {{ display:block; width:3px; height:3px; background:var(--matrix-quiet); }}
  .mx-dots i:last-child {{ background:var(--signal); }}
  .chart-title {{ margin:0; font-family:{title_font}; font-size:34px; line-height:1.18; font-weight:700; letter-spacing:.01em; }}
  .chart-subtitle {{ margin-top:8px; color:var(--muted); font-size:14px; }}
  .mx-meta {{ margin-top:7px; display:flex; align-items:center; gap:{interface_tokens['metaGap']}px; font-family:{index_font}; font-size:11px; font-weight:700; font-variation-settings:'ROND' 0,'wght' 700; letter-spacing:.075em; color:var(--matrix-strong); }}
  .mx-meta span {{ display:flex; align-items:center; gap:6px; white-space:nowrap; }}
  .mx-meta span::before {{ content:""; display:block; width:5px; height:5px; border:1px solid currentColor; }}
  .mx-meta span[data-state]::before {{ background:var(--signal); border-color:var(--signal); }}
  .mx-header-ticks {{ position:absolute; right:123px; top:-1px; height:7px; display:flex; align-items:start; gap:5px; }}
  .mx-header-ticks i {{ display:block; width:1px; height:4px; background:var(--rail); }}
  .mx-header-ticks i:nth-child(4n) {{ height:7px; background:var(--signal); }}
  .chart-body {{ min-height:0; }}
  svg {{ display:block; width:100%; height:100%; overflow:visible; }}
  svg text {{ font-family:{text_font}; fill:var(--ink); }}
  svg .title-font {{ font-family:{title_font}; }}
  svg .index {{ font-family:{index_font}; font-weight:650; font-variation-settings:'ROND' 0,'wght' 650; letter-spacing:.055em; fill:var(--matrix-strong); }}
  svg .muted {{ fill:var(--muted); }}
  svg .faint {{ fill:var(--faint); }}
  svg .index.muted {{ fill:var(--matrix-quiet); font-weight:560; font-variation-settings:'ROND' 0,'wght' 560; letter-spacing:.04em; }}
  svg .signal-text {{ fill:var(--signal); }}
  svg .index.signal-text {{ fill:var(--signal); font-weight:700; font-variation-settings:'ROND' 0,'wght' 700; }}
  svg .value {{ fill:var(--ink); font-variant-numeric:tabular-nums; }}
  svg .on-fill {{ fill:var(--bg); font-weight:700; }}
  svg .on-signal {{ fill:var(--on-signal); font-weight:700; }}
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
  .chart-footer .mark {{ font-family:{index_font}; color:var(--matrix-quiet); font-weight:600; font-variation-settings:'ROND' 0,'wght' 600; letter-spacing:.07em; }}
  [data-mode=\"brief\"] .evidence-plate {{ display:none; }}
  [data-mode=\"brief\"] svg .grid {{ opacity:.62; }}
  .motion-controls {{ position:absolute; right:54px; top:48px; display:grid; grid-template-columns:repeat(3,{interface_tokens['controlCell']}px); gap:0; z-index:5; border:1px solid var(--rail); clip-path:polygon(0 0,calc(100% - 7px) 0,100% 7px,100% 100%,7px 100%,0 calc(100% - 7px)); background:var(--bg); }}
  .motion-controls::before {{ content:"CTRL / 03"; position:absolute; right:0; top:-16px; font-family:{index_font}; font-size:9px; letter-spacing:.08em; color:var(--matrix-quiet); }}
  .motion-controls button {{ width:{interface_tokens['controlCell']}px; height:36px; border:0; border-left:1px solid var(--rail); background:var(--bg); color:var(--ink); font-family:{index_font}; cursor:pointer; padding:0; position:relative; }}
  .motion-controls button:first-child {{ border-left:0; }}
  .motion-controls button::after {{ content:attr(data-code); position:absolute; right:3px; bottom:1px; font-size:7px; color:var(--matrix-quiet); letter-spacing:.04em; }}
  .motion-controls button:hover {{ border-color:var(--signal); color:var(--signal); }}
  [data-motion] {{ transform-box:fill-box; transform-origin:center; }}
  @keyframes mx-align {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
  @keyframes mx-dock {{ from {{ opacity:0; transform:translate(var(--dx),var(--dy)); }} to {{ opacity:1; transform:translate(0,0); }} }}
  @keyframes mx-route {{ from {{ opacity:0; stroke-dashoffset:1; }} to {{ opacity:1; stroke-dashoffset:0; }} }}
  @keyframes mx-lock {{ 0% {{ opacity:0; transform:scale(.92); }} 68% {{ opacity:1; transform:scale(1.025); }} 100% {{ opacity:1; transform:scale(1); }} }}
  @keyframes mx-rail-rise {{ from {{ opacity:0; transform:translateY(var(--dy)) scaleY(.16); }} to {{ opacity:1; transform:translateY(0) scaleY(1); }} }}
  @keyframes mx-rail-slide {{ from {{ opacity:0; transform:translateX(var(--dx)) scaleX(.18); }} to {{ opacity:1; transform:translateX(0) scaleX(1); }} }}
  @keyframes mx-field-seat {{ from {{ opacity:0; transform:translateY(var(--dy)) scale(.72); }} to {{ opacity:1; transform:translateY(0) scale(1); }} }}
  @keyframes mx-band-fill {{ from {{ opacity:0; transform:scaleX(.06); }} to {{ opacity:1; transform:scaleX(1); }} }}
  @keyframes mx-pin {{ from {{ opacity:0; transform:translateY(var(--dy)) scale(.35); }} to {{ opacity:1; transform:translateY(0) scale(1); }} }}
  @keyframes mx-interlock {{ from {{ opacity:0; transform:translateX(var(--dx)) scaleX(.82); }} to {{ opacity:1; transform:translateX(0) scaleX(1); }} }}
  @keyframes mx-readout {{ from {{ opacity:0; clip-path:inset(0 100% 0 0); transform:translateY(6px); }} to {{ opacity:1; clip-path:inset(0 0 0 0); transform:translateY(0); }} }}
  @keyframes mx-alarm {{ from {{ opacity:0; transform:translateX(-8px); }} to {{ opacity:1; transform:translateX(0); }} }}
  .motion-enabled.is-playing [data-motion=\"align\"] {{ animation:mx-align var(--active-duration,var(--duration,{motion_tokens['align']}ms)) linear var(--active-delay,var(--delay,0ms)) both; }}
  .motion-enabled.is-playing [data-motion=\"dock\"] {{ animation:mx-dock var(--active-duration,var(--duration,{motion_tokens['dock']}ms)) {motion_tokens['ease']} var(--active-delay,var(--delay,0ms)) both; }}
  .motion-enabled.is-playing [data-motion=\"route\"] {{ animation:mx-route var(--active-duration,var(--duration,{motion_tokens['route']}ms)) {motion_tokens['ease']} var(--active-delay,var(--delay,0ms)) both; }}
  .motion-enabled.is-playing [data-motion=\"route\"]:not([data-choreo=\"band-fill\"]) {{ stroke-dasharray:1; will-change:stroke-dashoffset,opacity; }}
  .motion-enabled.is-playing [data-motion=\"lock\"] {{ animation:mx-lock var(--active-duration,var(--duration,{motion_tokens['lock']}ms)) {motion_tokens['ease']} var(--active-delay,var(--delay,0ms)) both; }}
  .motion-enabled.is-playing [data-choreo=\"rail-rise\"] {{ animation-name:mx-rail-rise; transform-origin:center bottom; }}
  .motion-enabled.is-playing [data-choreo=\"rail-slide\"] {{ animation-name:mx-rail-slide; transform-origin:left center; }}
  .motion-enabled.is-playing [data-choreo=\"field-seat\"] {{ animation-name:mx-field-seat; }}
  .motion-enabled.is-playing [data-choreo=\"band-fill\"] {{ animation-name:mx-band-fill; transform-origin:left center; }}
  .motion-enabled.is-playing [data-choreo=\"trace\"] {{ animation-timing-function:linear; }}
  .motion-enabled.is-playing [data-choreo=\"pin\"] {{ animation-name:mx-pin; }}
  .motion-enabled.is-playing [data-choreo=\"interlock\"] {{ animation-name:mx-interlock; }}
  .motion-enabled.is-playing [data-choreo=\"readout\"] {{ animation-name:mx-readout; transform-origin:left center; }}
  .motion-enabled.is-playing [data-choreo=\"alarm\"] {{ animation-name:mx-alarm; }}
  .motion-enabled.is-paused [data-motion] {{ animation-play-state:paused!important; }}
  @media (prefers-reduced-motion:reduce) {{ .motion-enabled.is-playing [data-motion] {{ animation:none!important; }} }}
  .pi-split-body {{ display:grid; grid-template-columns:{interface_tokens['evidenceBay']['width']}px minmax(0,1fr); column-gap:{interface_tokens['evidenceBay']['gap']}px; align-items:stretch; min-width:0; }}
  .pi-evidence-bay {{ position:relative; min-width:0; padding:0 22px 0 4px; border-right:1px solid var(--grid); display:grid; grid-template-rows:18px auto 18px; align-content:center; gap:9px; }}
  .pi-evidence-bay::after {{ content:""; position:absolute; right:-3px; top:50%; width:5px; height:5px; margin-top:-2px; background:var(--signal); }}
  .pi-evidence-bay__label {{ font-family:{index_font}; font-size:9px; font-weight:700; font-variation-settings:'ROND' 0,'wght' 700; letter-spacing:.08em; color:var(--matrix-quiet); align-self:end; }}
  .pi-evidence-svg {{ display:block; width:100%!important; height:auto!important; overflow:visible; }}
  .pi-bay-terminal {{ height:18px; display:grid; grid-template-columns:auto minmax(20px,1fr) 7px; align-items:center; gap:7px; font-family:{index_font}; font-size:9px; font-weight:750; font-variation-settings:'ROND' 0,'wght' 750; letter-spacing:.06em; color:var(--signal); }}
  .pi-bay-terminal i {{ height:1px; background:var(--rail); }}
  .pi-bay-terminal b {{ display:block; width:7px; height:7px; border:1.5px solid var(--signal); background:var(--bg); }}
  .pi-data-field {{ display:block; width:100%!important; height:100%!important; min-width:0; overflow:hidden; contain:layout paint; isolation:isolate; }}
  .pi-evidence-bay .evidence-plate .panel-stroke {{ stroke:var(--ink); stroke-width:1.2; }}
  svg .pi-socket {{ fill:var(--bg); stroke:var(--ink); stroke-width:1.5; vector-effect:non-scaling-stroke; }}
  svg .pi-socket-signal {{ fill:var(--signal); stroke:var(--on-signal); stroke-width:1; vector-effect:non-scaling-stroke; }}
  svg .pi-lock-ring {{ fill:none; stroke:var(--signal); stroke-width:2; vector-effect:non-scaling-stroke; }}
  svg .pi-lock-cross {{ fill:none; stroke:var(--signal); stroke-width:1; vector-effect:non-scaling-stroke; }}
  svg .pi-address {{ font-family:{index_font}; fill:var(--matrix-strong); font-weight:700; font-variation-settings:'ROND' 0,'wght' 700; letter-spacing:.06em; }}
  svg .pi-address-signal {{ fill:var(--signal); }}
  svg .pi-focus-corner {{ fill:none; stroke:var(--signal); stroke-width:2; vector-effect:non-scaling-stroke; }}
  svg .pm-socket {{ fill:var(--bg); stroke:var(--ink); stroke-width:1.5; vector-effect:non-scaling-stroke; }}
  svg .pm-socket-signal {{ fill:var(--signal); stroke:var(--on-signal); stroke-width:1; vector-effect:non-scaling-stroke; }}
  svg .pm-lock-ring {{ fill:none; stroke:var(--signal); stroke-width:2; vector-effect:non-scaling-stroke; }}
  svg .pm-lock-cross {{ fill:none; stroke:var(--signal); stroke-width:1; vector-effect:non-scaling-stroke; }}
  svg .pm-address {{ font-family:{index_font}; fill:var(--matrix-strong); font-weight:700; font-variation-settings:'ROND' 0,'wght' 700; letter-spacing:.06em; }}
  svg .pm-address-signal {{ fill:var(--signal); }}
  svg .pm-focus-corner {{ fill:none; stroke:var(--signal); stroke-width:2; vector-effect:non-scaling-stroke; }}
  svg .pm-micro-bracket {{ fill:none; stroke:var(--signal); stroke-width:1; vector-effect:non-scaling-stroke; }}
  [data-lock-mode="micro"] .pm-target-lock .pm-focus-corner,
  [data-lock-mode="micro"] .pm-target-lock .pm-lock-ring,
  [data-lock-mode="micro"] .pm-target-lock .pm-lock-cross,
  [data-lock-mode="micro"] .pi-overlay .pi-focus-corner,
  [data-lock-mode="micro"] .pi-overlay .pi-lock-cross {{ display:none; }}
  [data-lock-mode="micro"] .pm-target-lock .pm-socket-signal {{ transform-box:fill-box; transform-origin:center; transform:scale(.56); }}
  [data-lock-mode="micro"] .pi-overlay .pi-lock-ring {{ r:4px; fill:var(--signal); stroke:none; }}
  [data-lock-mode="micro"] .pm-address-signal,
  [data-lock-mode="micro"] .pi-address-signal {{ opacity:.82; }}
  @keyframes pm-lock-settle {{ from {{ opacity:0; transform:scale(.96); }} to {{ opacity:1; transform:scale(1); }} }}
  @keyframes pm-evidence-enter {{ from {{ opacity:0; transform:translateY(5px); }} to {{ opacity:1; transform:translateY(0); }} }}
  @keyframes pi-evidence-enter {{ from {{ opacity:0; transform:translateX(-8px); }} to {{ opacity:1; transform:translateX(0); }} }}
  @keyframes pi-terminal-handshake {{ from {{ opacity:.2; }} to {{ opacity:1; }} }}
  @keyframes pi-lock-settle {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
  .pm-data-field-layer,.pm-plot-layer,.pm-local-evidence,.pm-target-lock,.pi-target-lock {{ transform-box:fill-box; transform-origin:center; }}
  [data-motion-revision="motion-v2"] .pm-data-field-layer,
  [data-motion-revision="motion-v2"] .pm-plot-layer {{ opacity:1; animation:none; will-change:auto; }}
  [data-motion-revision="motion-v2"].is-resetting [data-motion] {{ animation:none!important; opacity:0; }}
  [data-motion-revision="motion-v2"].is-resetting [data-motion="route"],
  [data-motion-revision="motion-v2"].is-resetting [data-choreo="trace"] {{ stroke-dasharray:1; stroke-dashoffset:1; }}
  [data-motion-revision="motion-v2"].is-resetting .pm-local-evidence,
  [data-motion-revision="motion-v2"].is-resetting .pm-target-lock,
  [data-motion-revision="motion-v2"].is-resetting .pi-target-lock {{ opacity:0; }}
  [data-motion-revision="motion-v2"] [data-choreo="trace"] {{ stroke-dasharray:1; }}
  [data-motion-revision="motion-v2"]:not(.is-playing):not(.is-resetting) [data-choreo="trace"] {{ stroke-dashoffset:0; opacity:1; }}
  .motion-enabled.is-playing[data-motion-revision="motion-v2"] .pm-local-evidence {{ animation:pm-evidence-enter var(--pm-evidence-duration,360ms) {precision_motion['ease']} var(--pm-active-evidence-delay,var(--pm-evidence-delay,0ms)) both; will-change:opacity,transform; }}
  .motion-enabled.is-playing[data-motion-revision="motion-v2"][data-presentation-carrier="direct"] .pm-target-lock,
  .motion-enabled.is-playing[data-motion-revision="motion-v2"][data-presentation-carrier="embedded"] .pm-target-lock {{ animation:pm-lock-settle var(--pm-lock-duration,280ms) linear var(--pm-active-lock-delay,var(--pm-lock-delay,0ms)) both; will-change:opacity,transform; }}
  .motion-enabled.is-paused[data-motion-revision="motion-v2"] [data-motion],
  .motion-enabled.is-paused[data-motion-revision="motion-v2"] .pm-local-evidence,
  .motion-enabled.is-paused[data-motion-revision="motion-v2"] .pm-target-lock {{ animation-play-state:paused!important; }}
  [data-motion-revision="motion-v2"] .pi-data-field {{ opacity:1; animation:none; }}
  [data-motion-revision="motion-v2"] .pi-evidence-bay {{ opacity:1; transform:translateX(0); animation:none; will-change:auto; }}
  [data-motion-revision="motion-v2"].is-resetting .pi-evidence-bay {{ opacity:0; transform:translateX(-8px); }}
  [data-motion-revision="motion-v2"].is-resetting .pi-bay-terminal {{ opacity:.2; }}
  .motion-enabled.is-playing[data-motion-revision="motion-v2"][data-motion-strategy="evidence-interface"] .pi-evidence-bay {{ animation:pi-evidence-enter {precision_motion['evidence']['duration']}ms {precision_motion['ease']} var(--pi-active-evidence-delay,var(--pi-evidence-delay,0ms)) both; will-change:opacity,transform; }}
  .motion-enabled.is-playing[data-motion-revision="motion-v2"][data-motion-strategy="evidence-interface"] .pi-bay-terminal {{ animation:pi-terminal-handshake {precision_motion['terminal']['duration']}ms linear var(--pi-active-terminal-delay,var(--pi-terminal-delay,860ms)) both; will-change:opacity; }}
  .motion-enabled.is-playing[data-motion-revision="motion-v2"][data-motion-strategy="evidence-interface"] .pi-target-lock {{ animation:pi-lock-settle {precision_motion['lock']['duration']}ms linear var(--pi-active-lock-delay,var(--pi-lock-delay,980ms)) both; will-change:opacity; }}
  .motion-enabled.is-paused[data-motion-revision="motion-v2"] .pi-evidence-bay,
  .motion-enabled.is-paused[data-motion-revision="motion-v2"] .pi-bay-terminal,
  .motion-enabled.is-paused[data-motion-revision="motion-v2"] .pi-target-lock {{ animation-play-state:paused!important; }}
  .is-complete[data-motion-revision="motion-v2"] .pm-data-field-layer,
  .is-complete[data-motion-revision="motion-v2"] .pm-plot-layer,
  .is-complete[data-motion-revision="motion-v2"] .pm-local-evidence,
  .is-complete[data-motion-revision="motion-v2"] .pm-target-lock,
  .is-complete[data-motion-revision="motion-v2"] .pi-target-lock,
  .is-complete[data-motion-revision="motion-v2"] .pi-evidence-bay {{ will-change:auto; }}
  @media (prefers-reduced-motion:reduce) {{
    [data-motion-revision="motion-v2"] .pm-data-field-layer,
    [data-motion-revision="motion-v2"] .pm-plot-layer,
    [data-motion-revision="motion-v2"] .pm-local-evidence,
    [data-motion-revision="motion-v2"] .pm-target-lock,
    [data-motion-revision="motion-v2"] [data-motion],
    [data-motion-revision="motion-v2"] .pi-evidence-bay,
    [data-motion-revision="motion-v2"] .pi-bay-terminal,
    [data-motion-revision="motion-v2"] .pi-target-lock,
    [data-motion-revision="motion-v2"] .pi-lock-ring,
    [data-motion-revision="motion-v2"] .pi-focus-corner {{ animation:none!important; opacity:1!important; transform:none; }}
    [data-motion-revision="motion-v2"] [data-choreo="trace"] {{ stroke-dasharray:1; stroke-dashoffset:0; }}
  }}
</style>
</head>
<body>
<main class=\"chart-container\" id=\"moxing-chart\" data-total=\"{page.total_ms}\" data-total-brief=\"{page.profile_totals.get('brief', round(page.total_ms * .68))}\" data-total-standard=\"{page.profile_totals.get('standard', page.total_ms)}\" data-total-story=\"{page.profile_totals.get('story', round(page.total_ms * 1.8))}\" data-mode=\"{esc(page.mode)}\" data-choreography=\"{esc(page.choreography)}\" data-motion-system=\"{esc(motion_system)}\" data-motion-revision=\"{esc(motion_revision)}\" data-motion-strategy=\"{esc(motion_strategy)}\" data-presentation-carrier=\"{esc(carrier_name)}\" data-presentation-target=\"{esc(page.presentation_target)}\" data-lock-mode=\"{esc(lock_mode)}\" data-line-trace=\"{'true' if page.line_trace else 'false'}\"{root_interface}>
  <header class=\"chart-header\">
    <div class=\"chart-code\"><div class=\"mx-code\"><div class=\"mx-code__top\"><strong>{esc(display_code)}</strong><span>SYS / 21</span></div><div class=\"mx-code__name\">{esc(page.public_name.upper())}</div><div class=\"mx-code__state\"><span class=\"mx-dots\" aria-hidden=\"true\"><i></i><i></i><i></i><i></i><i></i><i></i></span>{esc(page.interface_state)}</div></div></div>
    <div><h1 class=\"chart-title\">{esc(page.title)}</h1><div class=\"chart-subtitle\">{esc(page.subtitle)}</div><div class=\"mx-meta\"><span>FAMILY / {esc(page.family)}</span><span>DATA / {esc(page.data_signature)}</span><span data-state>STATE / READY</span></div></div>
    <span class=\"mx-header-ticks\" aria-hidden=\"true\">{header_ticks}</span>
  </header>
  {body_markup}
  <footer class=\"chart-footer\"><span>{esc(page.footer)}</span><span class=\"mark\">MOXING / STRUCTURAL INTERFACE</span></footer>
  <nav class=\"motion-controls\" aria-label=\"动画控制\"><button type=\"button\" data-action=\"replay\" data-code=\"R\" title=\"重播\">↻</button><button type=\"button\" data-action=\"pause\" data-code=\"H\" title=\"暂停或继续\">Ⅱ</button><button type=\"button\" data-action=\"surface\" data-code=\"S\" title=\"切换明暗\">◐</button></nav>
</main>
<script type=\"application/json\" id=\"moxing-data\">{data_json.replace('</', '<\\/')}</script>
<script>
(() => {{
  const root=document.getElementById('moxing-chart');
  const params=new URLSearchParams(location.search);
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches||params.get('motion')==='off';
  const requestedProfile=params.get('motion')||'standard';
  const profile=['brief','standard','story'].includes(requestedProfile)?requestedProfile:'standard';
  const scales={{brief:{motion_tokens['profiles']['brief']['fallbackScale']},standard:{motion_tokens['profiles']['standard']['fallbackScale']},story:{motion_tokens['profiles']['story']['fallbackScale']}}};
  const scale=scales[profile]||1;
  const terminalProfiles={{brief:{{lockDuration:220,evidenceDuration:280}},standard:{{lockDuration:260,evidenceDuration:360}},story:{{lockDuration:320,evidenceDuration:440}}}};
  const terminal=terminalProfiles[profile]||terminalProfiles.standard;
  root.style.setProperty('--pm-lock-duration',terminal.lockDuration+'ms');
  root.style.setProperty('--pm-evidence-duration',terminal.evidenceDuration+'ms');
  const activeMs=(node,name,fallback)=>{{
    if(!node)return Math.max(0,Math.round(fallback*scale));
    const profileValue=parseFloat(node.style.getPropertyValue(name+'-'+profile));
    if(Number.isFinite(profileValue))return Math.max(0,Math.round(profileValue));
    const baseValue=parseFloat(node.style.getPropertyValue(name));
    return Math.max(0,Math.round((Number.isFinite(baseValue)?baseValue:fallback)*scale));
  }};
  const directField=root.querySelector('.pm-direct-field');
  const embeddedField=root.querySelector('.pm-embedded-field');
  const interfaceField=root.querySelector('.pi-data-field');
  const evidenceBay=root.querySelector('.pi-evidence-bay');
  const directLockDelay=activeMs(directField,'--pm-lock-delay',980);
  const embeddedEvidenceDelay=activeMs(embeddedField,'--pm-evidence-delay',760);
  const embeddedLockDelay=activeMs(embeddedField,'--pm-lock-delay',1080);
  const interfaceEvidenceDelay=activeMs(evidenceBay,'--pi-evidence-delay',{precision_motion['evidence']['delay']});
  const interfaceTerminalDelay=activeMs(evidenceBay,'--pi-terminal-delay',860);
  const interfaceLockDelay=activeMs(interfaceField,'--pi-lock-delay',980);
  root.style.setProperty('--pm-active-lock-delay',directLockDelay+'ms');
  root.style.setProperty('--pm-active-evidence-delay',embeddedEvidenceDelay+'ms');
  root.style.setProperty('--pm-active-embedded-lock-delay',embeddedLockDelay+'ms');
  root.style.setProperty('--pi-active-evidence-delay',interfaceEvidenceDelay+'ms');
  root.style.setProperty('--pi-active-terminal-delay',interfaceTerminalDelay+'ms');
  root.style.setProperty('--pi-active-lock-delay',interfaceLockDelay+'ms');
  const profileKey='total'+profile[0].toUpperCase()+profile.slice(1);
  const dataTotal=Number(root.dataset[profileKey]||root.dataset.total||1800);
  const baseDuration={{align:{motion_tokens['align']},dock:{motion_tokens['dock']},route:{motion_tokens['route']},lock:{motion_tokens['lock']}}};
  root.querySelectorAll('[data-motion]').forEach(el=>{{
    const rawDelay=parseFloat(el.style.getPropertyValue('--delay'))||0;
    const rawDuration=parseFloat(el.style.getPropertyValue('--duration'))||baseDuration[el.dataset.motion]||300;
    const profileDelay=parseFloat(el.style.getPropertyValue('--delay-'+profile));
    const profileDuration=parseFloat(el.style.getPropertyValue('--duration-'+profile));
    el.style.setProperty('--active-delay',Math.round(Number.isFinite(profileDelay)?profileDelay:rawDelay*scale)+'ms');
    el.style.setProperty('--active-duration',Math.round(Number.isFinite(profileDuration)?profileDuration:rawDuration*scale)+'ms');
  }});
  const timelineEnds=[...root.querySelectorAll('[data-motion]')].map(el=>Number.parseFloat(el.style.getPropertyValue('--active-delay'))+Number.parseFloat(el.style.getPropertyValue('--active-duration'))).filter(Number.isFinite);
  const terminalEnds=[embeddedField?embeddedEvidenceDelay+terminal.evidenceDuration:0,embeddedField?embeddedLockDelay+terminal.lockDuration:0,directField?directLockDelay+terminal.lockDuration:0,evidenceBay?interfaceEvidenceDelay+{precision_motion['evidence']['duration']}:0,evidenceBay?interfaceTerminalDelay+{precision_motion['terminal']['duration']}:0,interfaceField?interfaceLockDelay+{precision_motion['lock']['duration']}:0];
  const total=Math.max(dataTotal,...timelineEnds,...terminalEnds);
  let timer=0,frame=0,replayToken=0;
  const settle=()=>{{
    replayToken+=1;
    clearTimeout(timer); cancelAnimationFrame(frame);
    root.classList.remove('motion-enabled','is-playing','is-paused','is-resetting');
    root.classList.add('is-complete');
    const b=root.querySelector('[data-action=pause]'); if(b)b.textContent='Ⅱ';
  }};
  const replay=()=>{{
    const token=++replayToken;
    clearTimeout(timer); cancelAnimationFrame(frame);
    root.classList.remove('is-playing','is-complete','is-paused');
    if(reduce){{settle();return;}}
    root.style.setProperty('--motion-scale',scale);
    root.classList.add('motion-enabled','is-resetting');
    void root.offsetWidth;
    frame=requestAnimationFrame(()=>{{
      if(token!==replayToken)return;
      root.classList.remove('is-resetting');
      root.classList.add('is-playing');
      timer=setTimeout(settle,total+90);
    }});
  }};
  const pause=()=>{{
    if(!root.classList.contains('is-playing')&&!root.classList.contains('is-paused'))return;
    root.classList.toggle('is-paused');
    const b=root.querySelector('[data-action=pause]'); b.textContent=root.classList.contains('is-paused')?'▶':'Ⅱ';
  }};
  root.querySelector('[data-action=replay]').addEventListener('click',replay);
  root.querySelector('[data-action=pause]').addEventListener('click',pause);
  root.querySelector('[data-action=surface]').addEventListener('click',()=>{{ const html=document.documentElement; html.dataset.surface=html.dataset.surface==='dark'?'light':'dark'; }});
  if(params.get('theme')==='dark') document.documentElement.dataset.surface='dark';
  window.Moxing={{replay,settle,setSurface:(v)=>document.documentElement.dataset.surface=v,profile,duration:total,ready:Promise.resolve()}};
  if(reduce||params.get('autoplay')==='off') settle();
  else if('IntersectionObserver'in window){{ const io=new IntersectionObserver(e=>{{if(e[0].isIntersecting){{io.disconnect();replay();}}}},{{threshold:.35}});io.observe(root); }}
  else replay();
}})();
</script>
</body>
</html>
"""
