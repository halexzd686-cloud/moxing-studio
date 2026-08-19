#!/usr/bin/env python3
"""Build the compact v2 motion gallery."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moxing import CHARTS  # noqa: E402


def main() -> None:
    cards = []
    for chart_id, meta in CHARTS.items():
        number = int(chart_id[1:])
        filename = f"c{number:02d}-{meta['slug']}.html"
        cards.append(
            f"""<article class="card" data-chart="{chart_id}">
  <div class="card-head"><span>{chart_id} / {meta['name']}</span><button type="button" data-replay>REPLAY</button></div>
  <div class="frame"><iframe title="{meta['name']}" loading="lazy" src="{filename}?motion=brief"></iframe></div>
</article>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-surface="light">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Moxing v2 Motion Gallery</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#E8EAE4;color:#171916;font-family:system-ui,'Microsoft YaHei',sans-serif}}
header{{position:sticky;top:0;z-index:2;background:rgba(232,234,228,.94);backdrop-filter:blur(10px);padding:24px 4vw 18px;border-bottom:1px solid #BEC3B9;display:flex;justify-content:space-between;align-items:end}}
h1{{font-family:Georgia,'Songti SC',serif;margin:0;font-size:34px}} .sub{{color:#6F746C;margin-top:6px}}
.toolbar{{display:flex;gap:8px}} button,select{{border:1px solid #9DA39A;background:#F2F3EF;color:#171916;padding:8px 12px;font:600 11px ui-monospace,monospace;letter-spacing:.08em;cursor:pointer}}
main{{width:min(1480px,94vw);margin:30px auto 70px;display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.card{{background:#F2F3EF;border:1px solid #C8CCC3}} .card-head{{height:44px;padding:0 14px;display:flex;align-items:center;justify-content:space-between;font:600 11px ui-monospace,monospace;letter-spacing:.08em;border-bottom:1px solid #D8DBD4}}
.card-head button{{padding:5px 8px}} .frame{{aspect-ratio:16/9;overflow:hidden;position:relative}} iframe{{border:0;width:1280px;height:720px;transform-origin:0 0;position:absolute;inset:0}}
@media(max-width:900px){{main{{grid-template-columns:1fr}}}}
</style></head>
<body><header><div><h1>Moxing v2 / Structural Interface</h1><div class="sub">定位 · 装配 · 接通 · 锁定</div></div><div class="toolbar"><select id="motion"><option value="brief">BRIEF</option><option value="standard">STANDARD</option><option value="story">STORY</option><option value="off">MOTION OFF</option></select><button id="surface">DARK</button></div></header>
<main>{''.join(cards)}</main>
<script>
const frames=[...document.querySelectorAll('iframe')];const motion=document.getElementById('motion');let dark=false;
function fit(){{document.querySelectorAll('.frame').forEach(box=>{{const frame=box.querySelector('iframe');frame.style.transform=`scale(${{box.clientWidth/1280}})`}})}}
function update(frame){{frame.src=frame.src.split('?')[0]+`?motion=${{motion.value}}&theme=${{dark?'dark':'light'}}`}}
motion.addEventListener('change',()=>frames.forEach(update));document.getElementById('surface').addEventListener('click',e=>{{dark=!dark;e.target.textContent=dark?'LIGHT':'DARK';frames.forEach(update)}});
document.querySelectorAll('[data-replay]').forEach(button=>button.addEventListener('click',()=>update(button.closest('.card').querySelector('iframe'))));addEventListener('resize',fit);fit();
</script></body></html>"""
    target = ROOT / "templates" / "gallery.html"
    target.write_text(html, encoding="utf-8")
    print(f"built {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
