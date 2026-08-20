#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(process.argv[2] || ".");
const baseUrl = process.env.MOXING_LAB_URL || "http://127.0.0.1:4400/designs/precision-interface-lab/index.html";
const previewDir = path.join(root, "designs", "precision-interface-lab", "previews");
fs.mkdirSync(previewDir, { recursive: true });

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
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const errors = [];
const checks = [];
page.on("console", (message) => { if (message.type() === "error") errors.push(`console: ${message.text()}`); });
page.on("pageerror", (error) => errors.push(`page: ${error.message}`));

const pass = (name, details = "") => checks.push({ name, pass: true, details });
const fail = (name, details = "") => { checks.push({ name, pass: false, details }); errors.push(`${name}: ${details}`); };

await page.goto(baseUrl, { waitUntil: "networkidle" });
await page.waitForFunction(() => [...document.querySelectorAll("iframe")].every((frame) => frame.dataset.ready === "true"));
await page.evaluate(async () => {
  await Promise.all([...document.querySelectorAll("iframe")].map((frame) => frame.contentDocument.fonts?.ready));
});

const chartIds = ["c03", "c08", "c15", "c22"];
for (const chartId of chartIds) {
  const state = await page.evaluate((id) => {
    const frame = document.querySelector(`[data-prototype="${id}"] iframe`);
    const doc = frame?.contentDocument;
    return {
      ready: frame?.dataset.ready,
      precision: doc?.documentElement.dataset.precision,
      code: doc?.querySelector(".pi-code")?.textContent.trim(),
      meta: doc?.querySelectorAll(".pi-meta span").length,
      overlay: doc?.querySelectorAll(".pi-overlay").length,
      evidenceBay: doc?.querySelectorAll(".pi-evidence-bay").length,
      bayPlate: doc?.querySelectorAll(".pi-evidence-bay .evidence-plate").length,
      plateInDataField: doc?.querySelectorAll(".pi-data-field .evidence-plate").length,
      terminal: doc?.querySelectorAll(".pi-bay-terminal").length,
      targetLock: doc?.querySelectorAll(".pi-lock-ring, .pi-focus-corner").length,
      legacyMotion: doc?.querySelectorAll("[data-motion]").length,
      motionLayers: doc?.querySelectorAll("[data-pi-motion]").length,
      dataViewBoxX: Number.parseFloat(doc?.querySelector(".pi-data-field")?.getAttribute("viewBox") || "0"),
      stageAxesBehind: id === "c08" ? [...doc.querySelectorAll(".pi-stage-axis")].filter((axis) => axis.nextElementSibling?.classList.contains("stage-module")).length : null,
      controls: doc?.querySelectorAll(".motion-controls button").length,
    };
  }, chartId);
  const stageStackingValid = chartId !== "c08" || state.stageAxesBehind === 5;
  if (state.ready === "true" && state.precision === "lab" && state.code?.includes(chartId.toUpperCase()) && state.meta === 3 && state.overlay === 1 && state.evidenceBay === 1 && state.bayPlate === 1 && state.plateInDataField === 0 && state.terminal === 1 && state.targetLock >= 1 && state.legacyMotion === 0 && state.motionLayers <= 24 && state.dataViewBoxX > 0 && state.controls === 3 && stageStackingValid) {
    pass(`${chartId} instrument contract`, JSON.stringify(state));
  } else {
    fail(`${chartId} instrument contract`, JSON.stringify(state));
  }

  await page.locator(`[data-chart="${chartId}"]`).click();
  await page.waitForTimeout(1750);
  const active = await page.getAttribute("body", "data-active");
  if (active === chartId) pass(`${chartId} focus selection`);
  else fail(`${chartId} focus selection`, `active=${active}`);
  await page.screenshot({ path: path.join(previewDir, `${chartId}-light.png`), fullPage: true });
}

await page.locator('[data-chart="c08"]').click();
await page.locator('[data-lab-action="surface"]').click();
await page.waitForTimeout(250);
const darkStates = await page.evaluate(() => [...document.querySelectorAll("iframe")].map((frame) => frame.contentDocument.documentElement.dataset.surface));
if (darkStates.every((surface) => surface === "dark")) pass("dark surface synchronization", darkStates.join(","));
else fail("dark surface synchronization", darkStates.join(","));
await page.screenshot({ path: path.join(previewDir, "c08-dark.png"), fullPage: true });

await page.locator('[data-lab-action="output"]').click();
const exportState = await page.evaluate(() => [...document.querySelectorAll("iframe")].map((frame) => {
  const doc = frame.contentDocument;
  return {
    output: doc.documentElement.dataset.output,
    display: getComputedStyle(doc.querySelector(".motion-controls")).display,
  };
}));
if (exportState.every(({ output, display }) => output === "export" && display === "none")) pass("export-safe controls", JSON.stringify(exportState));
else fail("export-safe controls", JSON.stringify(exportState));

await page.locator('[data-lab-action="output"]').click();
await page.locator('[data-lab-action="surface"]').click();
await page.locator('[data-lab-action="view"]').click();
await page.waitForTimeout(250);
const view = await page.getAttribute("body", "data-view");
if (view === "grid") pass("four-up comparison view");
else fail("four-up comparison view", `view=${view}`);
const gridMotion = await page.evaluate(() => [...document.querySelectorAll("iframe")].map((frame) => ({
  view: frame.contentDocument.documentElement.dataset.labView,
  playing: frame.contentDocument.querySelector(".chart-container")?.classList.contains("is-playing"),
})));
if (gridMotion.every(({ view: frameView, playing }) => frameView === "grid" && !playing)) pass("grid remains static", JSON.stringify(gridMotion));
else fail("grid remains static", JSON.stringify(gridMotion));
await page.screenshot({ path: path.join(previewDir, "lab-grid-light.png"), fullPage: true });

await page.locator('[data-lab-action="replay"]').click();
await page.waitForTimeout(80);
const animationState = await page.evaluate(() => [...document.querySelectorAll("iframe")].map((frame) => {
  const doc = frame.contentDocument;
  const terminal = doc.querySelector(".pi-bay-terminal");
  return {
    view: doc.documentElement.dataset.labView,
    playing: doc.querySelector(".chart-container")?.classList.contains("is-playing"),
    terminalAnimation: terminal ? getComputedStyle(terminal).animationName : "missing",
  };
}));
const playingFrames = animationState.filter(({ playing }) => playing);
if (playingFrames.length === 1 && playingFrames[0].view === "focus" && playingFrames[0].terminalAnimation === "pi-terminal-handshake") pass("single-frame precision replay", JSON.stringify(animationState));
else fail("precision replay choreography", JSON.stringify(animationState));

await page.setViewportSize({ width: 824, height: 1018 });
await page.locator('[data-chart="c22"]').click();
await page.waitForTimeout(80);
const narrowGeometry = await page.evaluate(() => {
  const frame = document.querySelector('[data-prototype="c22"] iframe');
  const doc = frame?.contentDocument;
  const bay = doc?.querySelector('.pi-evidence-bay')?.getBoundingClientRect();
  const field = doc?.querySelector('.pi-data-field')?.getBoundingClientRect();
  const stage = document.querySelector('[data-prototype="c22"] .frame-stage');
  return {
    gap: bay && field ? Math.round((field.left - bay.right) * 10) / 10 : -1,
    overflow: doc ? getComputedStyle(doc.querySelector('.pi-data-field')).overflow : 'missing',
    scaleMethod: stage && getComputedStyle(stage).zoom !== '1' ? 'zoom' : 'transform',
  };
});
if (narrowGeometry.gap >= 24 && narrowGeometry.overflow === "hidden") pass("narrow evidence separation", JSON.stringify(narrowGeometry));
else fail("narrow evidence separation", JSON.stringify(narrowGeometry));

const cadence = await page.evaluate(async () => {
  const frame = document.querySelector('[data-prototype="c22"] iframe');
  const win = frame.contentWindow;
  const doc = frame.contentDocument;
  win.Moxing.replay();
  await new Promise((resolve) => win.requestAnimationFrame(resolve));
  const runningAnimations = doc.getAnimations().filter((animation) => animation.playState === 'running').length;
  const stamps = [];
  const startedAt = win.performance.now();
  await new Promise((resolve) => {
    const sample = (time) => {
      stamps.push(time);
      if (time - startedAt < 1450) win.requestAnimationFrame(sample);
      else resolve();
    };
    win.requestAnimationFrame(sample);
  });
  const deltas = stamps.slice(1).map((time, index) => time - stamps[index]);
  const ordered = [...deltas].sort((a, b) => a - b);
  const percentile = (ratio) => ordered[Math.min(ordered.length - 1, Math.floor(ordered.length * ratio))] || 0;
  return {
    frames: stamps.length,
    runningAnimations,
    medianMs: Math.round(percentile(.5) * 10) / 10,
    p95Ms: Math.round(percentile(.95) * 10) / 10,
    longFrames: deltas.filter((delta) => delta > 28).length,
  };
});
if (cadence.runningAnimations <= 5) pass("replay motion-layer budget", JSON.stringify(cadence));
else fail("replay motion-layer budget", JSON.stringify(cadence));
if (cadence.frames >= 70 && cadence.p95Ms <= 24 && cadence.longFrames <= 3) pass("narrow replay cadence", JSON.stringify(cadence));
else fail("narrow replay cadence", JSON.stringify(cadence));
await page.screenshot({ path: path.join(previewDir, "lab-narrow-c22.png"), fullPage: true });

if (errors.length === 0) pass("runtime errors", "none");
else fail("runtime errors", errors.join(" | "));

const report = {
  url: baseUrl,
  generatedAt: new Date().toISOString(),
  checks,
  failures: checks.filter((check) => !check.pass).length,
};
fs.writeFileSync(path.join(previewDir, "qa-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
await browser.close();

console.log(`Precision Interface Lab: ${checks.length - report.failures}/${checks.length} checks passed`);
if (report.failures) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
}
