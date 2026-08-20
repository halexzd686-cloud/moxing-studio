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

const launchOptions = { headless: true };
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
      route: doc?.querySelectorAll(".pi-evidence-route, .pi-evidence-route-accent").length,
      controls: doc?.querySelectorAll(".motion-controls button").length,
    };
  }, chartId);
  if (state.ready === "true" && state.precision === "lab" && state.code?.includes(chartId.toUpperCase()) && state.meta === 3 && state.overlay === 2 && state.route === 2 && state.controls === 3) {
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
await page.waitForTimeout(1750);
const view = await page.getAttribute("body", "data-view");
if (view === "grid") pass("four-up comparison view");
else fail("four-up comparison view", `view=${view}`);
await page.screenshot({ path: path.join(previewDir, "lab-grid-light.png"), fullPage: true });

await page.locator('[data-lab-action="replay"]').click();
const animationState = await page.evaluate(() => [...document.querySelectorAll("iframe")].map((frame) => {
  const doc = frame.contentDocument;
  const route = doc.querySelector(".pi-evidence-route");
  return {
    playing: doc.querySelector(".chart-container")?.classList.contains("is-playing"),
    routeAnimation: route ? getComputedStyle(route).animationName : "missing",
  };
}));
if (animationState.every(({ playing, routeAnimation }) => playing && routeAnimation === "pi-route-grow")) pass("precision replay choreography", JSON.stringify(animationState));
else fail("precision replay choreography", JSON.stringify(animationState));

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
