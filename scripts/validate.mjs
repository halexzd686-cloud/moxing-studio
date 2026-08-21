#!/usr/bin/env node
/** Moxing Studio v2 structural, motion, fallback, and visual validation. */
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(process.argv[2] || ".");
const templatesDir = path.join(root, "templates");
const previewDir = path.join(root, "docs", "previews");
const chartFiles = fs.readdirSync(templatesDir).filter((file) => /^c\d{2}-.*\.html$/.test(file)).sort();
const precisionSpecs = {
  "c03-signal-trend.html": { evidence: "E03", plotX: 248 },
  "c06-ledger-steps.html": { evidence: "E06", plotX: 260 },
  "c08-stage-channel.html": { evidence: "E08", plotX: 280 },
  "c15-commerce-flow.html": { evidence: "E15", plotX: 250 },
  "c22-correlation-matrix.html": { evidence: "E22", plotX: 255 },
};
const directA = new Set([
  "c01-structural-rank.html", "c02-ranked-rail.html", "c04-composition-field.html",
  "c05-composition-bands.html", "c07-milestone-lanes.html", "c09-metric-lockup.html",
  "c10-decision-interface.html", "c11-sector-lock.html", "c12-metric-small-multiples.html",
  "c20-sensitivity-matrix.html",
]);
const embeddedB = new Set([
  "c13-pareto-contribution.html", "c14-cohort-matrix.html", "c16-decision-bubble-matrix.html",
  "c17-market-candles.html", "c18-performance-drawdown.html", "c19-yield-curve.html",
  "c21-distribution-profile.html", "c23-forecast-fan.html", "c24-control-chart.html",
]);
const exemplars = {
  "c01-structural-rank.html": { family: "rail-rise", cue: "rail-rise", animation: "mx-rail-rise", direct: true, directLayers: 3 },
  "c02-ranked-rail.html": { family: "ranked-rail", cue: "rail-slide", animation: "mx-rail-slide", direct: true, directLayers: 3 },
  "c03-signal-trend.html": { family: "path-trace", cue: "trace", animation: "mx-route", precision: true },
  "c04-composition-field.html": { family: "field-aggregation", cue: "field-seat", animation: "mx-field-seat", direct: true, directLayers: 2 },
  "c05-composition-bands.html": { family: "band-routing", cue: "band-fill", animation: "mx-band-fill", direct: true, directLayers: 2 },
  "c06-ledger-steps.html": { family: "ledger-interlock", cue: "field-seat", animation: "mx-field-seat", precision: true },
  "c07-milestone-lanes.html": { family: "milestone-routing", cue: "interlock", animation: "mx-interlock", direct: true, directLayers: 2 },
  "c08-stage-channel.html": { family: "stage-interlock", cue: "interlock", animation: "mx-interlock", precision: true },
  "c09-metric-lockup.html": { family: "metric-readout", cue: "readout", animation: "mx-readout", direct: true, directLayers: 2 },
  "c10-decision-interface.html": { family: "decision-readout", cue: "readout", animation: "mx-readout", direct: true, directLayers: 3 },
  "c11-sector-lock.html": { family: "sector-lock", cue: "field-seat", animation: "mx-field-seat", direct: true, directLayers: 2 },
  "c12-metric-small-multiples.html": { family: "metric-pulse", cue: "trace", animation: "mx-route", direct: true, directLayers: 2 },
  "c13-pareto-contribution.html": { family: "pareto-routing", cue: "rail-rise", animation: "mx-rail-rise", embedded: true, embeddedLayers: 4 },
  "c14-cohort-matrix.html": { family: "cohort-seating", cue: "field-seat", animation: "mx-field-seat", embedded: true, embeddedLayers: 4 },
  "c15-commerce-flow.html": { family: "flow-routing", cue: "trace", animation: "mx-route", precision: true },
  "c16-decision-bubble-matrix.html": { family: "quadrant-lock", cue: "pin", animation: "mx-pin", embedded: true, embeddedLayers: 3 },
  "c17-market-candles.html": { family: "market-build", cue: "field-seat", animation: "mx-field-seat", embedded: true, embeddedLayers: 4 },
  "c18-performance-drawdown.html": { family: "drawdown-routing", cue: "trace", animation: "mx-route", embedded: true, embeddedLayers: 4 },
  "c19-yield-curve.html": { family: "curve-routing", cue: "trace", animation: "mx-route", embedded: true, embeddedLayers: 4 },
  "c20-sensitivity-matrix.html": { family: "matrix-seating", cue: "field-seat", animation: "mx-field-seat", direct: true, directLayers: 2 },
  "c21-distribution-profile.html": { family: "distribution-build", cue: "rail-rise", animation: "mx-rail-rise", embedded: true, embeddedLayers: 4 },
  "c22-correlation-matrix.html": { family: "matrix-seating", cue: "field-seat", animation: "mx-field-seat", precision: true },
  "c23-forecast-fan.html": { family: "forecast-routing", cue: "trace", animation: "mx-route", embedded: true, embeddedLayers: 4 },
  "c24-control-chart.html": { family: "control-lock", cue: "trace", animation: "mx-route", embedded: true, embeddedLayers: 4 },
};
const failures = [];
const checks = [];
const fail = (scope, message) => failures.push({ scope, message });
const pass = (scope, message) => checks.push({ scope, message });
fs.mkdirSync(previewDir, { recursive: true });

function luminance(hex) {
  const rgb = hex.slice(1).match(/../g).map((value) => Number.parseInt(value, 16) / 255)
    .map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
}
function contrast(a, b) {
  const [high, low] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (high + 0.05) / (low + 0.05);
}

const tokens = JSON.parse(fs.readFileSync(path.join(root, "tokens", "system.json"), "utf8"));
for (const [name, surface] of Object.entries(tokens.surfaces)) {
  const textRatio = contrast(surface.ink, surface.bg);
  const signalRatio = contrast(surface.signal, surface.bg);
  const matrixStrongRatio = contrast(surface.matrixStrong, surface.bg);
  const matrixQuietRatio = contrast(surface.matrixQuiet, surface.bg);
  const onSignalRatio = contrast(surface.onSignal, surface.signal);
  if (textRatio < 7) fail(`tokens:${name}`, `ink/bg contrast ${textRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `ink/bg contrast ${textRatio.toFixed(2)}`);
  if (signalRatio < 3) fail(`tokens:${name}`, `signal/bg contrast ${signalRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `signal/bg contrast ${signalRatio.toFixed(2)}`);
  if (matrixStrongRatio < 5) fail(`tokens:${name}`, `matrixStrong/bg contrast ${matrixStrongRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `matrixStrong/bg contrast ${matrixStrongRatio.toFixed(2)}`);
  if (matrixQuietRatio < 3.5) fail(`tokens:${name}`, `matrixQuiet/bg contrast ${matrixQuietRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `matrixQuiet/bg contrast ${matrixQuietRatio.toFixed(2)}`);
  if (onSignalRatio < 4.5) fail(`tokens:${name}`, `onSignal/signal contrast ${onSignalRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `onSignal/signal contrast ${onSignalRatio.toFixed(2)}`);
  for (const [index, category] of surface.cat.entries()) {
    const ratio = contrast(surface.bg, category);
    if (ratio < 4.5) fail(`tokens:${name}`, `bg/cat-${index + 1} contrast ${ratio.toFixed(2)}`);
    else pass(`tokens:${name}`, `bg/cat-${index + 1} contrast ${ratio.toFixed(2)}`);
  }
}

for (const file of chartFiles) {
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  const scope = `static:${file}`;
  if (!source.includes('viewBox="0 0 1172 500"') && !/class="pi-data-field" viewBox="\d+(?:\.\d+)? 0 \d+(?:\.\d+)? 500"/.test(source)) fail(scope, "missing v2 or precision-cropped viewBox");
  if (!source.includes("--matrix-strong:") || !source.includes("--matrix-quiet:") || !source.includes("--on-signal:")) fail(scope, "missing contrast tokens");
  if (/class="[^"]*index[^"]*"[^>]*font-size="11"/.test(source)) fail(scope, "dot-matrix text below 12px");
  if (!source.includes('data-motion="align"') || !source.includes('data-motion="dock"') || !source.includes('data-motion="lock"')) fail(scope, "missing motion primitives");
  if (!source.includes('data-total-brief="') || !source.includes('data-total-standard="') || !source.includes('data-total-story="')) fail(scope, "missing profile totals");
  if (!/data-lock-mode="(?:implicit|micro|explicit)"/.test(source) || !/data-line-trace="(?:true|false)"/.test(source)) fail(scope, "missing lock or line-trace contract");
  if (!source.includes("prefers-reduced-motion") || !source.includes("window.Moxing")) fail(scope, "missing motion accessibility/runtime API");
  if (!source.includes('@keyframes mx-route { from { opacity:0; stroke-dashoffset:1; } to { opacity:1; stroke-dashoffset:0; } }')) fail(scope, "route trace exposes a pre-draw ghost state");
  if (!source.includes('@keyframes mx-align { from { opacity:0; } to { opacity:1; } }')) fail(scope, "structural lines still use dash drawing");
  if (!source.includes('.motion-enabled.is-playing [data-motion="route"] { animation:mx-route')) fail(scope, "route timeline base is missing");
  if (!source.includes('.motion-enabled.is-playing [data-motion="route"]:not([data-choreo="band-fill"])')) fail(scope, "route animation is not isolated from fill bands");
  if (source.includes('mx-compiled-trace')) fail(scope, "legacy duplicate trace keyframe remains");
  if (!source.includes('[data-motion-revision="motion-v2"]:not(.is-playing):not(.is-resetting) [data-choreo="trace"]')) fail(scope, "trace final state is not gated by motion state");
  if (/<canvas\b/i.test(source)) fail(scope, "canvas is not allowed");
  if (/(?:src|href)\s*=\s*["']https?:\/\//i.test(source) || /url\(\s*["']?https?:\/\//i.test(source)) fail(scope, "external runtime URL");
  if (/paper|boardroom|mori|dawn/i.test(source)) fail(scope, "legacy theme residue");
  if (!/<h1\b[^>]*class="chart-title"[^>]*>[^<]+<\/h1>/i.test(source)) fail(scope, "missing conclusion title");
  if (!source.includes('class="mx-code"') || !source.includes('class="mx-meta"') || !source.includes('class="mx-header-ticks"')) fail(scope, "missing precision interface shell");
  if (!/class="mx-code__top"><strong>C\d{2}<\/strong>/.test(source)) fail(scope, "chart identifier is not zero-padded");
  if ((source.match(/data-code="[RHS]"/g) || []).length !== 3) fail(scope, "control dock codes incomplete");
  if (!failures.some((item) => item.scope === scope)) pass(scope, "v2 static contract");
}

for (const [file, expected] of Object.entries(exemplars)) {
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  const scope = `choreography:${file}`;
  if (!source.includes(`data-choreography="${expected.family}"`)) fail(scope, `missing ${expected.family} family`);
  if (!source.includes(`data-choreo="${expected.cue}"`)) fail(scope, `missing ${expected.cue} cue`);
  if (expected.precision && (!source.includes('data-motion-system="precision-v2.1"') || !source.includes('class="chart-body pi-split-body"') || !source.includes('class="pi-evidence-bay"') || !source.includes('class="pi-data-field"') || !source.includes('class="pi-bay-terminal"') || !source.includes('pi-overlay--foreground'))) fail(scope, "approved precision-interface contract incomplete");
  if (expected.direct && (!source.includes('data-motion-system="presentation-v2.1"') || !source.includes('data-presentation-carrier="direct"') || !source.includes('class="pm-data-field-layer"') || !source.includes('class="pm-plot-layer"') || source.includes('class="pi-evidence-bay"'))) fail(scope, "approved direct-canvas contract incomplete");
  if (expected.embedded && (!source.includes('data-motion-system="presentation-v2.1"') || !source.includes('data-presentation-carrier="embedded"') || !source.includes('class="pm-data-field-layer"') || !source.includes('class="pm-plot-layer"') || !source.includes('class="pm-local-evidence"') || source.includes('class="pi-evidence-bay"'))) fail(scope, "approved embedded-evidence contract incomplete");
  const explicit = source.match(new RegExp(`data-choreo="${expected.cue}"[^>]*style="([^"]+)"`))?.[1] || "";
  if (!explicit.includes("--delay-brief:") || !explicit.includes("--delay-story:")) fail(scope, "cue lacks independent profile timing");
  if (!failures.some((item) => item.scope === scope)) pass(scope, `${expected.family} with independent profile timing`);
}

for (const file of directA) {
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  const scope = `direct:${file}`;
  if (!source.includes('data-presentation-carrier="direct"') || !source.includes('data-presentation-target="direct"')) fail(scope, "direct carrier/target mismatch");
  const lockMode = source.match(/<main[^>]+data-lock-mode="([a-z]+)"/)?.[1];
  if (lockMode === "implicit" && source.includes('class="pm-target-lock"')) fail(scope, "implicit target rendered an extra lock ornament");
  if (lockMode !== "implicit" && (!source.includes('class="pm-target-lock"') || !source.includes('pm-address-signal'))) fail(scope, "visible target lock missing");
  if (source.includes("evidence bay") || source.includes('class="evidence-plate"') || source.includes('class="pm-local-evidence"')) fail(scope, "detached evidence remains");
  if (!failures.some((item) => item.scope === scope)) pass(scope, `full-width field with ${lockMode} target`);
}

for (const file of embeddedB) {
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  const scope = `embedded:${file}`;
  if (!source.includes('data-presentation-carrier="embedded"') || !source.includes('data-presentation-target="embedded"')) fail(scope, "embedded carrier/target mismatch");
  const lockMode = source.match(/<main[^>]+data-lock-mode="([a-z]+)"/)?.[1];
  if (!source.includes('class="pm-local-evidence"')) fail(scope, "local evidence missing");
  if (lockMode === "implicit" && source.includes('class="pm-target-lock"')) fail(scope, "implicit target rendered an extra lock ornament");
  if (lockMode !== "implicit" && (!source.includes('class="pm-target-lock"') || !source.includes('pm-address-signal'))) fail(scope, "visible target lock missing");
  if (source.includes('class="pi-evidence-bay"') || source.includes('class="evidence-plate"')) fail(scope, "detached evidence container remains");
  if (!failures.some((item) => item.scope === scope)) pass(scope, `full-width field with embedded evidence and ${lockMode} target`);
}

for (const [file, expected] of Object.entries(precisionSpecs)) {
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  const scope = `precision:${file}`;
  if (!source.includes(`aria-label="${expected.evidence} evidence bay"`)) fail(scope, `missing ${expected.evidence} side bay`);
  if (!source.includes(`class="pi-data-field" viewBox="${expected.plotX} 0 `)) fail(scope, `plot crop origin is not ${expected.plotX}`);
  if (!source.includes("pi-overlay--foreground") || !source.includes("pi-lock-ring") && !source.includes("pi-focus-corner")) fail(scope, "missing data-bound target lock");
  if (!failures.some((item) => item.scope === scope)) pass(scope, `${expected.evidence} production parity contract`);
}

let playwright;
try {
  playwright = await import("playwright");
} catch (error) {
  const dependencyPath = process.env.MOXING_PLAYWRIGHT_PATH;
  if (!dependencyPath) throw new Error("playwright missing; set MOXING_PLAYWRIGHT_PATH", { cause: error });
  playwright = await import(pathToFileURL(path.join(dependencyPath, "index.mjs")));
}
const launchOptions = { headless: true, args: ["--disable-gpu", "--disable-dev-shm-usage", "--no-first-run"] };
if (process.env.MOXING_BROWSER_EXECUTABLE) launchOptions.executablePath = process.env.MOXING_BROWSER_EXECUTABLE;
const browser = await playwright.chromium.launch(launchOptions);

async function inspect(file, javaScriptEnabled) {
  const mode = javaScriptEnabled ? "js" : "no-js";
  const scope = `${file}:${mode}`;
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, javaScriptEnabled, reducedMotion: "no-preference" });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const external = [];
  page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => { if (!request.url().startsWith("file:") && !request.url().startsWith("data:")) external.push(request.url()); });
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
  if (javaScriptEnabled) {
    await page.evaluate(() => document.fonts?.ready || Promise.resolve());
    await page.evaluate(() => window.Moxing?.settle());
  }
  const state = await page.evaluate(() => {
    const container = document.querySelector(".chart-container")?.getBoundingClientRect();
    return {
      width: container?.width, height: container?.height,
      svg: document.querySelectorAll("svg").length,
      text: document.querySelectorAll("svg text").length,
      shapes: document.querySelectorAll("svg path,svg rect,svg circle,svg line,svg polygon").length,
      api: Boolean(window.Moxing),
      surface: document.documentElement.dataset.surface,
      precisionShell: {
        code: document.querySelectorAll(".mx-code").length,
        meta: document.querySelectorAll(".mx-meta span").length,
        ticks: document.querySelectorAll(".mx-header-ticks i").length,
        controls: document.querySelectorAll(".motion-controls button[data-code]").length,
      },
      headerGap: (() => { const code = document.querySelector(".chart-code"); const title = document.querySelector(".chart-title"); if (!code || !title) return -1; const range = document.createRange(); range.selectNodeContents(code); return title.getBoundingClientRect().left - range.getBoundingClientRect().right; })(),
      titleOverflow: (() => { const title = document.querySelector(".chart-title"); const header = document.querySelector(".chart-header"); if (!title || !header) return true; const range = document.createRange(); range.selectNodeContents(title); const textBox = range.getBoundingClientRect(); const titleBox = title.getBoundingClientRect(); const headerBox = header.getBoundingClientRect(); return textBox.right > titleBox.right + .5 || textBox.bottom > headerBox.bottom + .5; })(),
      overflow: document.body.scrollWidth > 1280 || document.body.scrollHeight > 720,
    };
  });
  if (state.width !== 1280 || state.height !== 720) fail(scope, `container ${state.width}x${state.height}`);
  const expectedSvg = precisionSpecs[file] ? 2 : 1;
  if (state.svg !== expectedSvg || state.text === 0 || state.shapes === 0) fail(scope, `svg=${state.svg} text=${state.text} shapes=${state.shapes}`);
  if (state.overflow) fail(scope, "page overflow");
  if (state.titleOverflow) fail(scope, "conclusion title overflow");
  if (state.headerGap < 24) fail(scope, `header gap ${state.headerGap.toFixed(1)}px`);
  if (state.precisionShell.code !== 1 || state.precisionShell.meta !== 3 || state.precisionShell.ticks !== 16 || state.precisionShell.controls !== 3) fail(scope, `precision shell ${JSON.stringify(state.precisionShell)}`);
  if (javaScriptEnabled && !state.api) fail(scope, "runtime API missing");
  if (consoleErrors.length || pageErrors.length || external.length) fail(scope, [...consoleErrors, ...pageErrors, ...external].join(" | "));
  if (!failures.some((item) => item.scope === scope)) pass(scope, javaScriptEnabled ? "runtime and locked frame" : "static fallback");
  await context.close();
}

for (const file of chartFiles) {
  await inspect(file, true);
  await inspect(file, false);
}

const motionContext = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: "no-preference" });
const motionPage = await motionContext.newPage();
await motionPage.goto(pathToFileURL(path.join(templatesDir, "c03-signal-trend.html")).href, { waitUntil: "load" });
await motionPage.evaluate(() => window.Moxing.replay());
await motionPage.waitForTimeout(100);
const activeMotion = await motionPage.evaluate(() => {
  const running = document.getAnimations().filter((item) => item.playState === "running");
  const macroSelector = ".pi-evidence-bay,.pi-bay-terminal,.pi-lock-ring,.pi-focus-corner";
  const activeMarks = [...document.querySelectorAll("[data-motion]")].filter((item) => getComputedStyle(item).animationName !== "none");
  const root = document.querySelector(".chart-container");
  const field = document.querySelector(".pi-data-field");
  const trace = document.querySelector('[data-choreo="trace"]');
  return {
    macroRunning: running.filter((item) => item.effect?.target?.matches?.(macroSelector)).length,
    layers: document.querySelectorAll(macroSelector).length,
    traceMarks: activeMarks.filter((item) => ["trace", "pin"].includes(item.dataset.choreo)).length,
    unexpectedMarks: activeMarks.filter((item) => !["trace", "pin"].includes(item.dataset.choreo)).length,
    revision: root?.dataset.motionRevision,
    fieldOpacity: Number.parseFloat(field ? getComputedStyle(field).opacity : "0"),
    traceOffset: Number.parseFloat(trace ? getComputedStyle(trace).strokeDashoffset : "0"),
  };
});
if (activeMotion.revision !== "motion-v2" || activeMotion.layers < 3 || activeMotion.layers > 4 || !activeMotion.traceMarks || activeMotion.fieldOpacity < .99 || activeMotion.macroRunning > 4) fail("motion", JSON.stringify(activeMotion));
else pass("motion", `${activeMotion.traceMarks} element animations with a single forward trace`);
await motionPage.evaluate(() => window.Moxing.setSurface("dark"));
const darkSurface = await motionPage.evaluate(() => document.documentElement.dataset.surface);
if (darkSurface !== "dark") fail("motion", "dark surface toggle failed");
else pass("motion", "dark surface toggle");
const replayContinuity = await motionPage.evaluate(() => new Promise((resolve) => {
  window.Moxing.settle();
  const root = document.querySelector('.chart-container');
  const field = document.querySelector('.pi-data-field');
  const trace = document.querySelector('[data-choreo="trace"]');
  const read = () => ({
    resetting: root.classList.contains('is-resetting'),
    playing: root.classList.contains('is-playing'),
    complete: root.classList.contains('is-complete'),
    fieldOpacity: Number.parseFloat(getComputedStyle(field).opacity),
    fieldTransform: getComputedStyle(field).transform,
    traceOffset: Number.parseFloat(getComputedStyle(trace).strokeDashoffset),
    traceOpacity: Number.parseFloat(getComputedStyle(trace).opacity),
  });
  window.Moxing.replay();
  const immediate = read();
  requestAnimationFrame(() => {
    const firstFrame = read();
    requestAnimationFrame(() => resolve({ immediate, firstFrame }));
  });
}));
if (replayContinuity.immediate.complete || !replayContinuity.immediate.resetting || replayContinuity.immediate.playing || replayContinuity.immediate.fieldOpacity < .99 || replayContinuity.immediate.traceOffset < 0 || replayContinuity.immediate.traceOffset > 1 || replayContinuity.firstFrame.complete || !replayContinuity.firstFrame.playing || replayContinuity.firstFrame.fieldOpacity < .99 || replayContinuity.firstFrame.fieldTransform !== "none" || replayContinuity.firstFrame.traceOpacity > .02) fail("motion-continuity", JSON.stringify(replayContinuity));
else pass("motion-continuity", "replay uses an instant reset followed by one forward timeline");
await motionContext.close();

for (const file of Object.keys(precisionSpecs)) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: "no-preference" });
  const page = await context.newPage();
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=brief&autoplay=off`, { waitUntil: "load" });
  const frameState = await page.evaluate(() => new Promise((resolve) => {
    window.Moxing.replay();
    const gaps = [];
    let previous = performance.now();
    const sample = (now) => {
      gaps.push(now - previous);
      previous = now;
      if (gaps.length < 50) { requestAnimationFrame(sample); return; }
      const ordered = [...gaps].sort((a, b) => a - b);
      const field = document.querySelector('.pi-data-field');
      const running = document.getAnimations().filter((item) => item.playState === "running");
      const macroSelector = '.pi-data-field,.pi-evidence-bay,.pi-bay-terminal,.pi-lock-ring,.pi-focus-corner';
      const activeMarks = [...document.querySelectorAll('[data-motion]')].filter((item) => getComputedStyle(item).animationName !== "none");
      resolve({
        carrier: field?.tagName,
        p95: ordered[Math.floor(ordered.length * .95)],
        over28: gaps.filter((gap) => gap > 28).length,
        macroRunning: running.filter((item) => item.effect?.target?.matches?.(macroSelector)).length,
        unexpectedMarks: activeMarks.filter((item) => document.querySelector('.chart-container')?.dataset.lineTrace !== 'true' || !['trace','pin'].includes(item.dataset.choreo)).length,
      });
    };
    requestAnimationFrame(sample);
  }));
  const scope = `precision-performance:${file}`;
  if (frameState.carrier !== "svg" && frameState.carrier !== "SVG" || frameState.p95 > 28 || frameState.over28 > 3 || frameState.macroRunning > 4) fail(scope, JSON.stringify(frameState));
  else pass(scope, `precision carrier p95 ${frameState.p95.toFixed(1)}ms; ${frameState.macroRunning} terminal layers`);
  await context.close();
}

for (const file of embeddedB) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: "no-preference" });
  const page = await context.newPage();
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=brief&autoplay=off`, { waitUntil: "load" });
  const frameState = await page.evaluate(() => new Promise((resolve) => {
    window.Moxing.replay();
    const gaps = [];
    let previous = performance.now();
    const sample = (now) => {
      gaps.push(now - previous);
      previous = now;
      if (gaps.length < 50) { requestAnimationFrame(sample); return; }
      const ordered = [...gaps].sort((a, b) => a - b);
      const running = document.getAnimations().filter((item) => item.playState === "running");
      const macroSelector = '.pm-data-field-layer,.pm-plot-layer,.pm-local-evidence,.pm-target-lock';
      const activeMarks = [...document.querySelectorAll('[data-motion]')].filter((item) => getComputedStyle(item).animationName !== "none");
      resolve({
        carrier: document.querySelector('.pm-embedded-field')?.tagName,
        p95: ordered[Math.floor(ordered.length * .95)],
        over28: gaps.filter((gap) => gap > 28).length,
        macroRunning: running.filter((item) => item.effect?.target?.matches?.(macroSelector)).length,
        layers: document.querySelectorAll('.pm-data-field-layer,.pm-plot-layer,.pm-local-evidence,.pm-target-lock').length,
        unexpectedMarks: activeMarks.filter((item) => document.querySelector('.chart-container')?.dataset.lineTrace !== 'true' || !['trace','pin'].includes(item.dataset.choreo)).length,
      });
    };
    requestAnimationFrame(sample);
  }));
  const scope = `embedded-performance:${file}`;
  const expectedLayers = file === "c16-decision-bubble-matrix.html" ? 3 : 4;
  if (frameState.carrier !== "svg" && frameState.carrier !== "SVG" || frameState.p95 > 28 || frameState.over28 > 3 || frameState.layers !== expectedLayers) fail(scope, JSON.stringify(frameState));
  else pass(scope, `embedded carrier p95 ${frameState.p95.toFixed(1)}ms; ${frameState.layers} static layers`);
  await context.close();
}

for (const file of directA) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: "no-preference" });
  const page = await context.newPage();
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=brief&autoplay=off`, { waitUntil: "load" });
  const frameState = await page.evaluate(() => new Promise((resolve) => {
    window.Moxing.replay();
    const gaps = [];
    let previous = performance.now();
    const sample = (now) => {
      gaps.push(now - previous);
      previous = now;
      if (gaps.length < 50) { requestAnimationFrame(sample); return; }
      const ordered = [...gaps].sort((a, b) => a - b);
      const running = document.getAnimations().filter((item) => item.playState === "running");
      const macroSelector = '.pm-data-field-layer,.pm-plot-layer,.pm-target-lock';
      const activeMarks = [...document.querySelectorAll('[data-motion]')].filter((item) => getComputedStyle(item).animationName !== "none");
      resolve({
        carrier: document.querySelector('.pm-direct-field')?.tagName,
        p95: ordered[Math.floor(ordered.length * .95)],
        over28: gaps.filter((gap) => gap > 28).length,
        macroRunning: running.filter((item) => item.effect?.target?.matches?.(macroSelector)).length,
        layers: document.querySelectorAll('.pm-data-field-layer,.pm-plot-layer,.pm-target-lock').length,
        unexpectedMarks: activeMarks.filter((item) => document.querySelector('.chart-container')?.dataset.lineTrace !== 'true' || !['trace','pin'].includes(item.dataset.choreo)).length,
      });
    };
    requestAnimationFrame(sample);
  }));
  const scope = `direct-performance:${file}`;
  const expectedLayers = ["c04-composition-field.html","c05-composition-bands.html","c07-milestone-lanes.html","c09-metric-lockup.html","c11-sector-lock.html","c12-metric-small-multiples.html","c20-sensitivity-matrix.html"].includes(file) ? 2 : 3;
  if (frameState.carrier !== "svg" && frameState.carrier !== "SVG" || frameState.p95 > 28 || frameState.over28 > 3 || frameState.layers !== expectedLayers) fail(scope, JSON.stringify(frameState));
  else pass(scope, `direct carrier p95 ${frameState.p95.toFixed(1)}ms; ${frameState.layers} static layers`);
  await context.close();
}

const profileRanges = {
  brief: [900, 1300],
  standard: [1400, 2200],
  story: [2500, 5000],
};
for (const [file, expected] of Object.entries(exemplars)) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: "no-preference" });
  const page = await context.newPage();
  const observed = {};
  for (const profile of ["brief", "standard", "story"]) {
    await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=${profile}`, { waitUntil: "load" });
    await page.evaluate(() => window.Moxing.replay());
    await page.waitForTimeout(50);
    observed[profile] = await page.evaluate(({ cue, precision, direct, embedded }) => {
      const element = document.querySelector(`[data-choreo="${cue}"]`);
      const lock = document.querySelector(precision ? '.pi-lock-ring,.pi-focus-corner' : direct || embedded ? '.pm-target-lock' : '[data-choreo="alarm"]');
      const style = element ? getComputedStyle(element) : null;
      const lockStyle = lock ? getComputedStyle(lock) : null;
      const macroSelector = direct ? ".pm-data-field-layer,.pm-plot-layer,.pm-target-lock" : embedded ? ".pm-data-field-layer,.pm-plot-layer,.pm-local-evidence,.pm-target-lock" : ".pi-data-field,.pi-evidence-bay,.pi-bay-terminal,.pi-lock-ring,.pi-focus-corner";
      const running = document.getAnimations().filter((item) => item.playState === "running");
      const activeMarks = [...document.querySelectorAll("[data-motion]")].filter((item) => getComputedStyle(item).animationName !== "none");
      return {
        profile: window.Moxing?.profile,
        duration: window.Moxing?.duration,
        delay: element ? Number.parseFloat(element.style.getPropertyValue("--active-delay")) : null,
        lockDelay: lock ? Number.parseFloat(lockStyle.animationDelay) * 1000 : null,
        animation: style?.animationName,
        macroRunning: running.filter((item) => item.effect?.target?.matches?.(macroSelector)).length,
        layers: document.querySelectorAll(macroSelector).length,
        unexpectedMarks: activeMarks.filter((item) => document.querySelector('.chart-container')?.dataset.lineTrace !== 'true' || !['trace','pin'].includes(item.dataset.choreo)).length,
      };
    }, { cue: expected.cue, precision: Boolean(expected.precision), direct: Boolean(expected.direct), embedded: Boolean(expected.embedded) });
    await page.evaluate(() => window.Moxing.settle());
  }
  const scope = `profiles:${file}`;
  for (const [profile, state] of Object.entries(observed)) {
    const [minimum, maximum] = profileRanges[profile];
    if (state.profile !== profile) fail(scope, `${profile} runtime reported ${state.profile}`);
    if (state.duration < minimum || state.duration > maximum) fail(scope, `${profile} duration ${state.duration}`);
    if (state.animation !== expected.animation) fail(scope, `${profile} animation ${state.animation}`);
    const directLayers = expected.directLayers || 2;
    if (expected.direct && state.layers !== directLayers) fail(scope, `${profile} direct layers ${state.layers}/${directLayers}`);
    const embeddedLayers = expected.embeddedLayers || 4;
    if (expected.embedded && state.layers !== embeddedLayers) fail(scope, `${profile} embedded layers ${state.layers}/${embeddedLayers}`);
    if (expected.precision && (state.macroRunning > 4 || state.layers !== 4)) fail(scope, `${profile} precision layers ${state.macroRunning}/${state.layers}`);
  }
  const briefRatio = observed.brief.delay / observed.standard.delay;
  const storyRatio = observed.story.delay / observed.standard.delay;
  if (Math.abs(briefRatio - 0.72) < 0.01 && Math.abs(storyRatio - 1.8) < 0.01) fail(scope, "profiles are uniform speed multipliers");
  if (observed.standard.lockDelay > 0 && !(observed.standard.delay < observed.standard.lockDelay)) fail(scope, `primary cue ${observed.standard.delay} does not precede lock ${observed.standard.lockDelay}`);
  if (!failures.some((item) => item.scope === scope)) pass(scope, `${expected.family} brief/standard/story choreography`);
  await context.close();
}

for (const [file, headingSelector] of Object.entries({
  "c02-ranked-rail.html": ".rank-heading text",
  "c07-milestone-lanes.html": ".milestone-heading text",
})) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
  const overlap = await page.evaluate((selector) => {
    const plate = document.querySelector(".evidence-plate")?.getBoundingClientRect();
    if (!plate) return false;
    return [...document.querySelectorAll(selector)].some((element) => {
      const box = element.getBoundingClientRect();
      return plate.left < box.right && plate.right > box.left && plate.top < box.bottom && plate.bottom > box.top;
    });
  }, headingSelector);
  if (overlap) fail(`layout:${file}`, "supporting evidence overlaps row heading");
  else pass(`layout:${file}`, "supporting evidence clears row headings");
  await context.close();
}

const collisionContext = await browser.newContext({ viewport: { width: 1280, height: 720 } });
const collisionPage = await collisionContext.newPage();
for (const file of chartFiles) {
  await collisionPage.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
  const collisions = await collisionPage.evaluate(() => {
    const plates = [...document.querySelectorAll(".evidence-plate,.pm-local-evidence")];
    const geometry = [...document.querySelectorAll([
      "line.rail-strong",
      "path.data-stroke", "path.signal-stroke", "path.secondary-stroke",
      "rect.data-fill", "rect.signal-fill", "rect.secondary-fill", "rect.cat-1",
      "circle.data-fill", "circle.signal-fill", "circle.secondary-fill", "circle.cat-1",
      "polygon.data-fill", "polygon.signal-fill", "polygon.secondary-fill", "polygon.cat-1",
    ].join(","))].filter((element) => !element.closest(".evidence-plate,.pm-local-evidence"));
    const overlaps = (a, b) => (
      a.x <= b.x + b.width && a.x + a.width >= b.x
      && a.y <= b.y + b.height && a.y + a.height >= b.y
    );
    const pathTouches = (element, plateBox) => {
      if (element.tagName.toLowerCase() !== "path" || typeof element.getTotalLength !== "function") return null;
      const length = element.getTotalLength();
      const matrix = element.getScreenCTM();
      if (!matrix || !Number.isFinite(length)) return false;
      const padding = 3;
      for (let index = 0; index <= 96; index += 1) {
        const local = element.getPointAtLength(length * index / 96);
        const point = new DOMPoint(local.x, local.y).matrixTransform(matrix);
        if (point.x >= plateBox.left - padding && point.x <= plateBox.right + padding && point.y >= plateBox.top - padding && point.y <= plateBox.bottom + padding) return true;
      }
      return false;
    };
    return plates.flatMap((plate, plateIndex) => {
      const plateBox = plate.getBoundingClientRect();
      return geometry.flatMap((element, geometryIndex) => {
        const box = element.getBoundingClientRect();
        const sampled = pathTouches(element, plateBox);
        if (sampled === false || sampled === null && !overlaps(plateBox, box)) return [];
        return [{ plate: plateIndex, geometry: geometryIndex, tag: element.tagName, className: element.getAttribute("class") || "" }];
      });
    });
  });
  if (collisions.length) fail(`collision:${file}`, JSON.stringify(collisions.slice(0, 4)));
  else pass(`collision:${file}`, "evidence plates clear critical plot geometry");
}
await collisionContext.close();

const readabilityContext = await browser.newContext({ viewport: { width: 1280, height: 720 } });
const readabilityPage = await readabilityContext.newPage();
for (const file of chartFiles) {
  const issues = [];
  for (const surface of ["light", "dark"]) {
    await readabilityPage.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
    await readabilityPage.evaluate((name) => { document.documentElement.dataset.surface = name; }, surface);
    await readabilityPage.evaluate(() => document.fonts?.ready || Promise.resolve());
    const surfaceIssues = await readabilityPage.evaluate((surfaceName) => {
      const selector = [
        "path.data-fill", "path.signal-fill", "path.secondary-fill",
        "rect.data-fill", "rect.signal-fill", "rect.secondary-fill",
        "circle.data-fill", "circle.signal-fill", "circle.secondary-fill",
        "polygon.data-fill", "polygon.signal-fill", "polygon.secondary-fill",
        "path.cat-1", "path.cat-2", "path.cat-3", "path.cat-4",
        "rect.cat-1", "rect.cat-2", "rect.cat-3", "rect.cat-4",
        "circle.cat-1", "circle.cat-2", "circle.cat-3", "circle.cat-4",
        "polygon.cat-1", "polygon.cat-2", "polygon.cat-3", "polygon.cat-4",
      ].join(",");
      const geometry = [...document.querySelectorAll(selector)];
      const parseRgb = (value) => {
        const numbers = value.match(/[\d.]+/g)?.slice(0, 3).map(Number);
        return numbers?.length === 3 ? numbers : null;
      };
      const luminance = (rgb) => {
        const channels = rgb.map((value) => value / 255).map((value) => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
        return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2];
      };
      const ratio = (foreground, background) => {
        const a = luminance(foreground), b = luminance(background);
        return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
      };
      const containsPoint = (shape, point) => {
        const matrix = shape.getScreenCTM();
        if (!matrix || typeof shape.isPointInFill !== "function") return false;
        return shape.isPointInFill(new DOMPoint(point.x, point.y).matrixTransform(matrix.inverse()));
      };
      return [...document.querySelectorAll("svg text")].flatMap((label) => {
        const box = label.getBoundingClientRect();
        if (!box.width || !box.height || !label.textContent.trim()) return [];
        const samples = [
          { x: box.left + box.width * .25, y: box.top + box.height * .5 },
          { x: box.left + box.width * .5, y: box.top + box.height * .5 },
          { x: box.left + box.width * .75, y: box.top + box.height * .5 },
        ];
        const foreground = parseRgb(getComputedStyle(label).fill);
        if (!foreground) return [];
        let minimum = Number.POSITIVE_INFINITY;
        let backgroundClass = "";
        for (const point of samples) {
          const beneath = geometry.filter((shape) => (
            Boolean(shape.compareDocumentPosition(label) & Node.DOCUMENT_POSITION_FOLLOWING)
            && containsPoint(shape, point)
          )).at(-1);
          if (!beneath) continue;
          const background = parseRgb(getComputedStyle(beneath).fill);
          if (!background) continue;
          const current = ratio(foreground, background);
          if (current < minimum) {
            minimum = current;
            backgroundClass = beneath.getAttribute("class") || beneath.tagName;
          }
        }
        if (minimum >= 4.5) return [];
        return [{ surface: surfaceName, text: label.textContent.trim(), ratio: Number(minimum.toFixed(2)), background: backgroundClass }];
      });
    }, surface);
    issues.push(...surfaceIssues);
  }
  if (issues.length) fail(`readability:${file}`, JSON.stringify(issues.slice(0, 8)));
  else pass(`readability:${file}`, "filled-mark labels pass in light and dark surfaces");
}
await readabilityContext.close();

const fillContext = await browser.newContext({ viewport: { width: 1280, height: 720 } });
const fillPage = await fillContext.newPage();
await fillPage.goto(`${pathToFileURL(path.join(templatesDir, "c05-composition-bands.html")).href}?motion=off`, { waitUntil: "load" });
const onFillLabels = await fillPage.locator("svg text.on-fill").count();
if (!onFillLabels) fail("layout:c05-composition-bands.html", "missing adaptive on-fill labels");
else pass("layout:c05-composition-bands.html", `${onFillLabels} adaptive on-fill labels`);
await fillContext.close();

const reducedContext = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: "reduce" });
const reducedPage = await reducedContext.newPage();
await reducedPage.goto(pathToFileURL(path.join(templatesDir, "c03-signal-trend.html")).href, { waitUntil: "load" });
await reducedPage.waitForTimeout(80);
const reducedState = await reducedPage.evaluate(() => ({ running: document.getAnimations().filter((item) => item.playState === "running").length, complete: document.querySelector(".chart-container")?.classList.contains("is-complete") }));
if (reducedState.running || !reducedState.complete) fail("reduced-motion", JSON.stringify(reducedState));
else pass("reduced-motion", "locked frame without motion");
await reducedContext.close();

for (const file of ["c01-structural-rank.html", "c03-signal-trend.html", "c05-composition-bands.html", "c08-stage-channel.html", "c10-decision-interface.html", "c11-sector-lock.html", "c14-cohort-matrix.html", "c15-commerce-flow.html", "c16-decision-bubble-matrix.html", "c17-market-candles.html", "c20-sensitivity-matrix.html", "c22-correlation-matrix.html", "c23-forecast-fan.html"]) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
  await page.evaluate(() => document.fonts?.ready || Promise.resolve());
  await page.screenshot({ path: path.join(previewDir, `v2-${file.slice(0, 3)}.png`) });
  await context.close();
  pass(`preview:${file}`, "locked preview exported");
}

const galleryServer = http.createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname).replace(/^\/+/, "");
  const target = path.resolve(templatesDir, pathname || "gallery.html");
  if (!target.startsWith(`${templatesDir}${path.sep}`) || !fs.existsSync(target)) { response.writeHead(404).end(); return; }
  response.writeHead(200, { "Content-Type": target.endsWith(".html") ? "text/html; charset=utf-8" : "application/octet-stream" });
  fs.createReadStream(target).pipe(response);
});
await new Promise((resolve) => galleryServer.listen(0, "127.0.0.1", resolve));
const galleryPort = galleryServer.address().port;
const galleryContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const galleryPage = await galleryContext.newPage();
await galleryPage.goto(`http://127.0.0.1:${galleryPort}/gallery.html`, { waitUntil: "load" });
const galleryCards = await galleryPage.locator(".card").count();
if (galleryCards !== 24) fail("gallery", `${galleryCards} cards`);
else pass("gallery", "24 compact v2 cards");
await galleryPage.waitForTimeout(180);
const galleryMotion = await galleryPage.evaluate(() => {
  const active = [...document.querySelectorAll("iframe")].filter((frame) => {
    try { return frame.contentDocument?.getAnimations().some((item) => item.playState === "running"); } catch { return false; }
  });
  const offscreen = active.filter((frame) => { const box = frame.closest(".card").getBoundingClientRect(); return box.bottom <= 0 || box.top >= innerHeight; });
  return { active: active.length, offscreen: offscreen.length };
});
if (galleryMotion.active || galleryMotion.offscreen) fail("gallery-motion", JSON.stringify(galleryMotion));
else pass("gallery-motion", "gallery remains static until an explicit replay");
const canaryFrame = galleryPage.locator('[data-chart="C3"] iframe');
await galleryPage.locator('[data-chart="C3"]').scrollIntoViewIfNeeded();
await galleryPage.waitForFunction(() => Boolean(document.querySelector('[data-chart="C3"] iframe')?.contentWindow?.Moxing));
await canaryFrame.evaluate((frame) => frame.contentWindow.Moxing.settle());
const beforeReplay = await canaryFrame.getAttribute("src");
await galleryPage.locator('[data-chart="C3"] [data-replay]').evaluate((button) => button.click());
await galleryPage.waitForTimeout(80);
const afterReplay = await canaryFrame.getAttribute("src");
const canaryRunning = await canaryFrame.evaluate((frame) => frame.contentDocument?.getAnimations().filter((item) => item.playState === "running" && item.effect?.target?.matches?.('[data-motion]')).length || 0);
if (beforeReplay !== afterReplay || canaryRunning < 1) fail("gallery-replay", JSON.stringify({ beforeReplay, afterReplay, canaryRunning }));
else pass("gallery-replay", "canary replay reuses iframe and runs element-level cues");
await galleryContext.close();

const mobileGalleryContext = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: "no-preference" });
const mobileGalleryPage = await mobileGalleryContext.newPage();
await mobileGalleryPage.goto(`http://127.0.0.1:${galleryPort}/gallery.html`, { waitUntil: "load" });
await mobileGalleryPage.waitForTimeout(250);
const mobileListState = await mobileGalleryPage.evaluate(() => {
  const cards = [...document.querySelectorAll(".card:not([hidden])")];
  const openButtons = [...document.querySelectorAll("[data-open]")];
  const mounted = [...document.querySelectorAll(".card-frame[data-mounted='true']")];
  const columns = getComputedStyle(document.querySelector(".gallery")).gridTemplateColumns.split(" ").filter(Boolean);
  return {
    columns: columns.length,
    overflow: document.documentElement.scrollWidth - innerWidth,
    minTarget: Math.min(...openButtons.map((button) => button.getBoundingClientRect().height)),
    mounted: mounted.length,
    cards: cards.length,
  };
});
if (mobileListState.columns !== 1 || mobileListState.overflow > 1 || mobileListState.minTarget < 44 || mobileListState.mounted > 4 || mobileListState.cards !== 24) fail("gallery-mobile-list", JSON.stringify(mobileListState));
else pass("gallery-mobile-list", `single column, ${mobileListState.mounted} mounted previews, ${mobileListState.minTarget}px targets`);
await mobileGalleryPage.screenshot({ path: path.join(previewDir, "gallery-mobile-list.png"), fullPage: false });

await mobileGalleryPage.locator('[data-chart="C3"] [data-open]').click();
await mobileGalleryPage.waitForFunction(() => Boolean(document.querySelector(".viewer-frame")?.contentWindow?.Moxing));
await mobileGalleryPage.waitForTimeout(80);
const portraitViewerState = await mobileGalleryPage.evaluate(() => {
  const viewer = document.getElementById("viewer");
  const canvas = document.querySelector(".viewer-canvas").getBoundingClientRect();
  const stage = document.querySelector(".viewer-stage");
  const hint = getComputedStyle(document.querySelector(".orientation-hint"));
  const runningCards = [...document.querySelectorAll(".card-frame")].reduce((total, frame) => total + (frame.contentDocument?.getAnimations().filter((animation) => animation.playState === "running").length || 0), 0);
  return {
    open: viewer.open,
    lockedBody: document.body.classList.contains("viewer-open"),
    detail: document.getElementById("viewer").dataset.detail,
    horizontalPan: stage.scrollWidth > stage.clientWidth * 1.5 && getComputedStyle(stage).overflowX === "auto",
    canvasHeightInside: canvas.height <= stage.clientHeight + 1,
    ratio: canvas.width / canvas.height,
    hint: hint.display !== "none",
    fitLabel: document.querySelector("[data-viewer-fit]").textContent,
    runningCards,
  };
});
if (!portraitViewerState.open || !portraitViewerState.lockedBody || portraitViewerState.detail !== "true" || !portraitViewerState.horizontalPan || !portraitViewerState.canvasHeightInside || Math.abs(portraitViewerState.ratio - 16 / 9) > .02 || !portraitViewerState.hint || portraitViewerState.fitLabel !== "FIT" || portraitViewerState.runningCards) fail("gallery-mobile-portrait-viewer", JSON.stringify(portraitViewerState));
else pass("gallery-mobile-portrait-viewer", "readable detail canvas pans horizontally and offers fit mode");
await mobileGalleryPage.screenshot({ path: path.join(previewDir, "gallery-mobile-portrait.png"), fullPage: false });
await mobileGalleryPage.locator("[data-viewer-replay]").click();
await mobileGalleryPage.waitForTimeout(80);
const mobileReplayState = await mobileGalleryPage.evaluate(() => ({
  viewer: document.querySelector(".viewer-frame").contentDocument?.getAnimations().filter((animation) => animation.playState === "running" && animation.effect?.target?.matches?.('[data-motion]')).length || 0,
  cards: [...document.querySelectorAll(".card-frame")].reduce((total, frame) => total + (frame.contentDocument?.getAnimations().filter((animation) => animation.playState === "running").length || 0), 0),
}));
if (mobileReplayState.viewer < 1 || mobileReplayState.cards) fail("gallery-mobile-replay", JSON.stringify(mobileReplayState));
else pass("gallery-mobile-replay", "only the focused viewer animates its element-level cues");
await mobileGalleryPage.locator("[data-viewer-fit]").click();
const fitToggleState = await mobileGalleryPage.evaluate(() => {
  const canvas = document.querySelector(".viewer-canvas").getBoundingClientRect();
  return {
    detail: document.getElementById("viewer").dataset.detail,
    canvasInside: canvas.left >= -1 && canvas.right <= innerWidth + 1 && canvas.top >= -1 && canvas.bottom <= innerHeight + 1,
    label: document.querySelector("[data-viewer-fit]").textContent,
  };
});
if (fitToggleState.detail !== "false" || !fitToggleState.canvasInside || fitToggleState.label !== "DETAIL") fail("gallery-mobile-fit-toggle", JSON.stringify(fitToggleState));
else pass("gallery-mobile-fit-toggle", "detail and full-frame views switch without reloading");
await mobileGalleryPage.locator("[data-viewer-close]").click();

await mobileGalleryPage.setViewportSize({ width: 844, height: 390 });
await mobileGalleryPage.locator('[data-chart="C8"] [data-open]').click();
await mobileGalleryPage.waitForFunction(() => Boolean(document.querySelector(".viewer-frame")?.contentWindow?.Moxing));
await mobileGalleryPage.waitForTimeout(80);
const landscapeViewerState = await mobileGalleryPage.evaluate(() => {
  const canvas = document.querySelector(".viewer-canvas").getBoundingClientRect();
  const stage = document.querySelector(".viewer-stage").getBoundingClientRect();
  const hint = getComputedStyle(document.querySelector(".orientation-hint"));
  return {
    open: document.getElementById("viewer").open,
    canvasInside: canvas.left >= stage.left - 1 && canvas.right <= stage.right + 1 && canvas.top >= stage.top - 1 && canvas.bottom <= stage.bottom + 1,
    ratio: canvas.width / canvas.height,
    fillsStage: canvas.height >= stage.height * .96 || canvas.width >= stage.width * .96,
    hint: hint.display,
    overflow: document.documentElement.scrollWidth - innerWidth,
  };
});
if (!landscapeViewerState.open || !landscapeViewerState.canvasInside || Math.abs(landscapeViewerState.ratio - 16 / 9) > .02 || !landscapeViewerState.fillsStage || landscapeViewerState.hint !== "none" || landscapeViewerState.overflow > 1) fail("gallery-mobile-landscape-viewer", JSON.stringify(landscapeViewerState));
else pass("gallery-mobile-landscape-viewer", "16:9 canvas fills the safe landscape stage");
await mobileGalleryPage.screenshot({ path: path.join(previewDir, "gallery-mobile-landscape.png"), fullPage: false });
await mobileGalleryContext.close();
await new Promise((resolve) => galleryServer.close(resolve));
await browser.close();

const report = { generatedAt: new Date().toISOString(), status: failures.length ? "failed" : "passed", checks, failures };
fs.writeFileSync(path.join(previewDir, "qa-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ status: report.status, passed: checks.length, failed: failures.length, failures }, null, 2));
process.exitCode = failures.length ? 1 : 0;
