#!/usr/bin/env python3
"""Build the responsive desktop/mobile v2 motion gallery."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moxing import CHARTS  # noqa: E402


GALLERY_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN" data-surface="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#E8EAE4">
<title>Moxing v2 Motion Gallery</title>
<style>
:root{--page:#E8EAE4;--panel:#F2F3EF;--ink:#171916;--muted:#6F746C;--line:#BEC3B9;--soft:#D8DBD4;--signal:#D95636;color-scheme:light}
[data-surface="dark"]{--page:#111310;--panel:#191C18;--ink:#F0F1EC;--muted:#A7ACA3;--line:#444A42;--soft:#30352F;--signal:#EA6544;color-scheme:dark}
*{box-sizing:border-box}html{background:var(--page)}body{margin:0;background:var(--page);color:var(--ink);font-family:-apple-system,"SF Pro Text","PingFang SC","Noto Sans SC",sans-serif;transition:background-color .2s,color .2s}
button,select{min-height:40px;border:1px solid var(--line);border-radius:0;background:var(--panel);color:var(--ink);padding:8px 12px;font:700 11px ui-monospace,"Cascadia Mono",monospace;letter-spacing:.08em;cursor:pointer}
button:focus-visible,select:focus-visible{outline:2px solid var(--signal);outline-offset:2px}button[aria-pressed="true"]{background:var(--ink);color:var(--panel);border-color:var(--ink)}
.site-head{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--page) 94%,transparent);backdrop-filter:blur(10px);padding:22px 4vw 16px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:minmax(300px,1fr) auto;gap:20px;align-items:end}
h1{font-family:Georgia,"Songti SC","Noto Serif SC",serif;margin:0;font-size:34px;line-height:1.05}.sub{color:var(--muted);margin-top:7px;font-size:14px}.toolbar,.filters,.card-actions,.viewer-actions{display:flex;align-items:center;gap:8px}.toolbar{justify-content:flex-end}.filters{grid-column:1/-1;justify-content:flex-start;flex-wrap:wrap}
.gallery{width:min(1480px,94vw);margin:30px auto 70px;display:grid;grid-template-columns:1fr 1fr;gap:24px}
.card{min-width:0;background:var(--panel);border:1px solid var(--line)}.card[hidden]{display:none}.card-head{height:48px;padding:0 10px 0 14px;display:flex;align-items:center;justify-content:space-between;gap:12px;border-bottom:1px solid var(--soft);font:700 11px ui-monospace,"Cascadia Mono",monospace;letter-spacing:.08em}.card-head>span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.card-actions button{min-height:32px;padding:5px 8px}
.frame{aspect-ratio:16/9;overflow:hidden;position:relative;background:var(--panel)}.frame-placeholder{position:absolute;inset:0;display:grid;place-content:center;gap:8px;text-align:center;color:var(--muted);font:700 11px ui-monospace,"Cascadia Mono",monospace;letter-spacing:.09em;transition:opacity .18s}.frame-placeholder b{color:var(--signal);font-size:18px}.frame.is-loaded .frame-placeholder{opacity:0;pointer-events:none}.card-frame{border:0;width:1280px;height:720px;transform-origin:0 0;position:absolute;inset:0;background:var(--panel)}
.viewer{width:100vw;max-width:none;height:100dvh;max-height:none;margin:0;padding:0;border:0;background:#0C0E0C;color:#F0F1EC}.viewer::backdrop{background:#0C0E0C}.viewer-shell{height:100%;display:grid;grid-template-rows:auto minmax(0,1fr);padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}.viewer-bar{min-height:56px;padding:6px 10px 6px 14px;border-bottom:1px solid #343934;display:flex;align-items:center;justify-content:space-between;gap:10px}.viewer-title{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font:700 11px ui-monospace,"Cascadia Mono",monospace;letter-spacing:.08em}.viewer-actions button{min-width:48px;min-height:44px;border-color:#555C54;background:#151815;color:#F0F1EC}.viewer-stage{position:relative;min-width:0;min-height:0;overflow:hidden;display:grid;place-items:center}.viewer-stage.is-pan{display:flex;align-items:center;justify-content:flex-start;overflow-x:auto;overflow-y:hidden;overscroll-behavior-x:contain;touch-action:pan-x}.viewer-canvas{position:relative;overflow:hidden;background:#F2F3EF;flex:0 0 auto}.viewer-frame{position:absolute;inset:0;width:1280px;height:720px;border:0;transform-origin:0 0}.orientation-hint{display:none;position:fixed;left:50%;bottom:max(14px,env(safe-area-inset-bottom));z-index:2;transform:translateX(-50%);margin:0;padding:8px 12px;border:1px solid #555C54;background:rgba(12,14,12,.9);color:#F0F1EC;font:700 10px ui-monospace,"Cascadia Mono",monospace;letter-spacing:.08em;white-space:nowrap;pointer-events:none}
body.viewer-open{overflow:hidden}
@media(max-width:900px){
  button,select{min-height:44px}.site-head{position:relative;padding:18px 12px 12px;display:flex;flex-direction:column;align-items:stretch;gap:12px}h1{font-size:25px}.sub{font-size:12px;line-height:1.65}.toolbar{justify-content:flex-start}.toolbar select{flex:1;min-width:0}.filters{order:3;flex-wrap:nowrap;overflow-x:auto;overscroll-behavior-inline:contain;padding-bottom:2px;scrollbar-width:none}.filters::-webkit-scrollbar{display:none}.filters button{flex:0 0 auto}.gallery{width:auto;margin:14px 12px 44px;grid-template-columns:1fr;gap:14px}.card-head{height:52px}.card-actions button{min-height:44px}.card [data-replay]{display:none}.frame{cursor:pointer}.card-frame{pointer-events:none}.orientation-hint{display:block}
}
@media(max-width:430px){.sub{max-width:34em}.card-head{padding-left:12px}.viewer-title{max-width:34vw}.viewer-actions{gap:6px}.viewer-actions button{padding-inline:9px}}
@media(max-width:900px) and (orientation:landscape){.orientation-hint,[data-viewer-fit]{display:none}.viewer-bar{min-height:48px}.viewer-actions button{min-height:40px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style>
</head>
<body>
<header class="site-head">
  <div><h1>Moxing v2 / Structural Interface</h1><div class="sub">24 个行业契约 · 9 个共享图形家族 · 桌面浏览 / 移动聚焦</div></div>
  <div class="toolbar"><select id="motion" aria-label="动画速度"><option value="brief">BRIEF</option><option value="standard">STANDARD</option><option value="story">STORY</option><option value="off">MOTION OFF</option></select><button id="surface" type="button">DARK</button></div>
  <nav class="filters" aria-label="图表领域"><button type="button" data-filter="all" aria-pressed="true">ALL / 24</button><button type="button" data-filter="foundation" aria-pressed="false">FOUNDATION / 10</button><button type="button" data-filter="commerce" aria-pressed="false">COMMERCE / 06</button><button type="button" data-filter="finance" aria-pressed="false">FINANCE / 04</button><button type="button" data-filter="analysis" aria-pressed="false">ANALYSIS / 04</button></nav>
</header>
<main class="gallery">__CARDS__</main>
<dialog class="viewer" id="viewer" aria-labelledby="viewer-title">
  <div class="viewer-shell">
    <header class="viewer-bar"><span class="viewer-title" id="viewer-title">CHART VIEWER</span><div class="viewer-actions"><button type="button" data-viewer-fit>FIT</button><button type="button" data-viewer-replay>REPLAY</button><button type="button" data-viewer-close>CLOSE</button></div></header>
    <div class="viewer-stage"><div class="viewer-canvas"><iframe class="viewer-frame" title="图表全屏预览"></iframe></div><p class="orientation-hint" data-orientation-hint>SWIPE / 左右滑动 · 横屏最佳</p></div>
  </div>
</dialog>
<script>
const CANVAS={width:1280,height:720};
const cards=[...document.querySelectorAll('.card')];
const frames=cards.map(card=>card.querySelector('.card-frame'));
const motion=document.getElementById('motion');
const surface=document.getElementById('surface');
const viewer=document.getElementById('viewer');
const viewerFrame=viewer.querySelector('.viewer-frame');
const viewerCanvas=viewer.querySelector('.viewer-canvas');
const viewerTitle=document.getElementById('viewer-title');
const viewerFit=viewer.querySelector('[data-viewer-fit]');
const viewerHint=viewer.querySelector('[data-orientation-hint]');
const mobile=matchMedia('(max-width:900px)');
let dark=false;
let activeViewerSource='';

function configuredSource(raw){const path=raw.split('?')[0];return `${path}?motion=${motion.value}&theme=${dark?'dark':'light'}&autoplay=off&build=motion-v2`}
function getApi(frame){try{return frame.contentWindow?.Moxing}catch{return null}}
function settle(frame){getApi(frame)?.settle()}
function pause(frame){getApi(frame)?.pause?.()}
function frameVisible(frame){const card=frame.closest('.card');if(!card)return true;const box=card.getBoundingClientRect();return box.bottom>0&&box.top<innerHeight}
function mount(frame){if(frame.dataset.mounted==='true')return;frame.dataset.mounted='true';frame.dataset.ready='false';frame.src=configuredSource(frame.dataset.src);frame.closest('.frame')?.classList.remove('is-loaded')}
function unmount(frame){if(frame.dataset.mounted!=='true')return;settle(frame);frame.src='about:blank';delete frame.dataset.mounted;delete frame.dataset.ready;frame.closest('.frame')?.classList.remove('is-loaded')}
function fitCard(frame){const box=frame.closest('.frame');const scale=box.clientWidth/CANVAS.width;frame.style.transform=`scale(${scale})`}
function fitCards(){frames.forEach(fitCard)}
function trimMobilePool(keep){if(!mobile.matches)return;const mounted=frames.filter(frame=>frame.dataset.mounted==='true');const removable=mounted.filter(frame=>frame!==keep&&!frameVisible(frame));while(mounted.length>4&&removable.length){const frame=removable.shift();mounted.splice(mounted.indexOf(frame),1);unmount(frame)}}
function updateMounted(){frames.filter(frame=>frame.dataset.mounted==='true').forEach(frame=>{frame.dataset.ready='false';frame.src=configuredSource(frame.dataset.src);frame.closest('.frame')?.classList.remove('is-loaded')});if(activeViewerSource){viewerFrame.dataset.ready='false';viewerFrame.src=configuredSource(activeViewerSource)}}
async function waitForApi(frame){for(let attempt=0;attempt<75;attempt+=1){const api=getApi(frame);if(api){if(api.ready)try{await api.ready}catch{}return api}await new Promise(resolve=>setTimeout(resolve,40))}return null}
async function replay(frame,{resetOthers=true}={}){if(resetOthers)frames.forEach(item=>{if(item!==frame)settle(item)});if(frame!==viewerFrame)mount(frame);const api=await waitForApi(frame);api?.replay?.()}

const observer=new IntersectionObserver(entries=>{for(const entry of entries){const frame=entry.target.querySelector('.card-frame');if(entry.isIntersecting){mount(frame);trimMobilePool(frame)}else{pause(frame)}}},{rootMargin:'30% 0px'});
function reconcileMode(){if(mobile.matches){cards.forEach(card=>observer.observe(card));trimMobilePool()}else{cards.forEach(card=>observer.unobserve(card));frames.forEach(mount)}fitCards()}

frames.forEach(frame=>frame.addEventListener('load',()=>{if(frame.src==='about:blank')return;frame.closest('.frame').classList.add('is-loaded');frame.dataset.ready='true';settle(frame);fitCard(frame)}));
document.querySelectorAll('[data-replay]').forEach(button=>button.addEventListener('click',()=>replay(button.closest('.card').querySelector('.card-frame'))));
document.querySelectorAll('[data-open]').forEach(button=>button.addEventListener('click',()=>openViewer(button.closest('.card'))));
document.querySelectorAll('.frame').forEach(frame=>frame.addEventListener('click',()=>{if(mobile.matches)openViewer(frame.closest('.card'))}));

function fitViewer(){if(!viewer.open)return;const stage=viewer.querySelector('.viewer-stage');const portrait=mobile.matches&&innerHeight>innerWidth;const detail=portrait&&viewer.dataset.detail==='true';const fitScale=Math.min(stage.clientWidth/CANVAS.width,stage.clientHeight/CANVAS.height);const scale=detail?Math.max(fitScale,Math.min(.58,stage.clientHeight/CANVAS.height)):fitScale;stage.classList.toggle('is-pan',detail);viewerCanvas.style.width=`${CANVAS.width*scale}px`;viewerCanvas.style.height=`${CANVAS.height*scale}px`;viewerFrame.style.transform=`scale(${scale})`;viewerFit.textContent=detail?'FIT':'DETAIL';viewerHint.textContent=detail?'SWIPE / 左右滑动 · 横屏最佳':'ROTATE DEVICE / 横屏查看细节';if(!detail)stage.scrollLeft=0}
function openViewer(card){activeViewerSource=card.querySelector('.card-frame').dataset.src;viewer.dataset.detail=String(mobile.matches&&innerHeight>innerWidth);viewerTitle.textContent=`${card.dataset.chart} / ${card.dataset.name}`;viewerFrame.dataset.ready='false';viewerFrame.src=configuredSource(activeViewerSource);document.body.classList.add('viewer-open');if(typeof viewer.showModal==='function')viewer.showModal();else viewer.setAttribute('open','');requestAnimationFrame(fitViewer)}
function closeViewer(){settle(viewerFrame);viewerFrame.src='about:blank';delete viewerFrame.dataset.ready;activeViewerSource='';document.body.classList.remove('viewer-open');if(typeof viewer.close==='function')viewer.close();else viewer.removeAttribute('open')}
viewerFrame.addEventListener('load',()=>{if(viewerFrame.src!=='about:blank'){viewerFrame.dataset.ready='true';settle(viewerFrame)}});
viewerFit.addEventListener('click',()=>{viewer.dataset.detail=String(viewer.dataset.detail!=='true');fitViewer()});
viewer.querySelector('[data-viewer-replay]').addEventListener('click',()=>replay(viewerFrame,{resetOthers:false}));
viewer.querySelector('[data-viewer-close]').addEventListener('click',closeViewer);
viewer.addEventListener('cancel',event=>{event.preventDefault();closeViewer()});

motion.addEventListener('change',updateMounted);
surface.addEventListener('click',()=>{dark=!dark;document.documentElement.dataset.surface=dark?'dark':'light';surface.textContent=dark?'LIGHT':'DARK';document.querySelector('meta[name="theme-color"]').content=dark?'#111310':'#E8EAE4';updateMounted()});
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));cards.forEach(card=>{card.hidden=button.dataset.filter!=='all'&&card.dataset.domain!==button.dataset.filter});requestAnimationFrame(()=>{fitCards();if(mobile.matches)trimMobilePool()})}));
mobile.addEventListener('change',reconcileMode);addEventListener('resize',()=>{fitCards();fitViewer()},{passive:true});addEventListener('orientationchange',()=>requestAnimationFrame(fitViewer));
reconcileMode();
</script>
</body>
</html>
"""


def main() -> None:
    cards = []
    for chart_id, meta in CHARTS.items():
        number = int(chart_id[1:])
        domain = "foundation" if number <= 10 else "commerce" if number <= 16 else "finance" if number <= 20 else "analysis"
        filename = f"c{number:02d}-{meta['slug']}.html"
        cards.append(
            f"""<article class="card" data-chart="{chart_id}" data-name="{meta['name']}" data-domain="{domain}">
  <div class="card-head"><span>{chart_id} / {meta['name']}</span><div class="card-actions"><button type="button" data-replay>REPLAY</button><button type="button" data-open>OPEN</button></div></div>
  <div class="frame"><div class="frame-placeholder"><b>{chart_id}</b><span>LOCKED PREVIEW</span></div><iframe class="card-frame" title="{meta['name']}" loading="lazy" data-src="{filename}?motion=brief&amp;autoplay=off&amp;build=motion-v2"></iframe></div>
</article>"""
        )
    target = ROOT / "templates" / "gallery.html"
    target.write_text(GALLERY_TEMPLATE.replace("__CARDS__", "".join(cards)), encoding="utf-8")
    print(f"built {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
