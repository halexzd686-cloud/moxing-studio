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
        domain = "foundation" if number <= 10 else "commerce" if number <= 16 else "finance" if number <= 20 else "analysis"
        filename = f"c{number:02d}-{meta['slug']}.html"
        cards.append(
            f"""<article class="card" data-chart="{chart_id}" data-domain="{domain}">
  <div class="card-head"><span>{chart_id} / {meta['name']}</span><button type="button" data-replay>REPLAY</button></div>
  <div class="frame"><iframe title="{meta['name']}" loading="lazy" src="{filename}?motion=brief&autoplay=off&build=macro-v2.1.1"></iframe></div>
</article>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-surface="light">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Moxing v2 Motion Gallery</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#E8EAE4;color:#171916;font-family:system-ui,'Microsoft YaHei',sans-serif}}
header{{position:sticky;top:0;z-index:2;background:rgba(232,234,228,.94);backdrop-filter:blur(10px);padding:22px 4vw 16px;border-bottom:1px solid #BEC3B9;display:grid;grid-template-columns:minmax(300px,1fr) auto;gap:20px;align-items:end}}
h1{{font-family:Georgia,'Songti SC',serif;margin:0;font-size:34px}} .sub{{color:#6F746C;margin-top:6px}}
.toolbar,.filters{{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}} .filters{{grid-column:1/-1;justify-content:flex-start}} button,select{{border:1px solid #9DA39A;background:#F2F3EF;color:#171916;padding:8px 12px;font:600 11px ui-monospace,monospace;letter-spacing:.08em;cursor:pointer}} button[aria-pressed="true"]{{background:#171916;color:#F2F3EF;border-color:#171916}}
main{{width:min(1480px,94vw);margin:30px auto 70px;display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.card{{background:#F2F3EF;border:1px solid #C8CCC3}} .card[hidden]{{display:none}} .card-head{{height:44px;padding:0 14px;display:flex;align-items:center;justify-content:space-between;font:600 11px ui-monospace,monospace;letter-spacing:.08em;border-bottom:1px solid #D8DBD4}}
.card-head button{{padding:5px 8px}} .frame{{aspect-ratio:16/9;overflow:hidden;position:relative}} iframe{{border:0;width:1280px;height:720px;transform-origin:0 0;position:absolute;inset:0}}
@media(max-width:900px){{main{{grid-template-columns:1fr}}}}
</style></head>
<body><header><div><h1>Moxing v2 / Structural Interface</h1><div class="sub">24 个行业契约 · 9 个共享图形家族 · 定位 / 装配 / 接通 / 锁定</div></div><div class="toolbar"><select id="motion"><option value="brief">BRIEF</option><option value="standard">STANDARD</option><option value="story">STORY</option><option value="off">MOTION OFF</option></select><button id="surface">DARK</button></div><nav class="filters" aria-label="图表领域"><button type="button" data-filter="all" aria-pressed="true">ALL / 24</button><button type="button" data-filter="foundation" aria-pressed="false">FOUNDATION / 10</button><button type="button" data-filter="commerce" aria-pressed="false">COMMERCE / 06</button><button type="button" data-filter="finance" aria-pressed="false">FINANCE / 04</button><button type="button" data-filter="analysis" aria-pressed="false">ANALYSIS / 04</button></nav></header>
<main>{''.join(cards)}</main>
<script>
const frames=[...document.querySelectorAll('iframe')];const motion=document.getElementById('motion');let dark=false;
function fit(){{document.querySelectorAll('.frame').forEach(box=>{{const frame=box.querySelector('iframe');frame.style.transform=`scale(${{box.clientWidth/1280}})`}})}}
function update(frame){{frame.dataset.played='';frame.src=frame.src.split('?')[0]+`?motion=${{motion.value}}&theme=${{dark?'dark':'light'}}&autoplay=off&build=macro-v2.1.1`}}
function getApi(frame){{try{{return frame.contentWindow?.Moxing}}catch{{return null}}}}
function replay(frame){{const api=getApi(frame);if(api)api.replay();else update(frame)}}
motion.addEventListener('change',()=>frames.forEach(update));document.getElementById('surface').addEventListener('click',e=>{{dark=!dark;e.target.textContent=dark?'LIGHT':'DARK';frames.forEach(update)}});
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{{document.querySelectorAll('[data-filter]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));document.querySelectorAll('.card').forEach(card=>card.hidden=button.dataset.filter!=='all'&&card.dataset.domain!==button.dataset.filter);fit()}}));
document.querySelectorAll('[data-replay]').forEach(button=>button.addEventListener('click',()=>replay(button.closest('.card').querySelector('iframe'))));
const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{{const frame=entry.target.querySelector('iframe'),api=getApi(frame);if(entry.isIntersecting&&!frame.dataset.played){{frame.dataset.played='1';if(api)replay(frame);else frame.addEventListener('load',()=>replay(frame),{{once:true}})}}else if(!entry.isIntersecting)api?.settle()}}),{{threshold:.28}});
document.querySelectorAll('.card').forEach(card=>observer.observe(card));addEventListener('resize',fit);fit();
</script></body></html>"""
    target = ROOT / "templates" / "gallery.html"
    target.write_text(html, encoding="utf-8")
    print(f"built {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
