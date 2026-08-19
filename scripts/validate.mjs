#!/usr/bin/env node
/** Moxing Studio v2 structural, motion, fallback, and visual validation. */
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(process.argv[2] || ".");
const templatesDir = path.join(root, "templates");
const previewDir = path.join(root, "docs", "previews");
const chartFiles = [
  "c01-structural-rank.html", "c02-ranked-rail.html", "c03-signal-trend.html",
  "c04-composition-field.html", "c05-composition-bands.html", "c06-ledger-steps.html",
  "c07-milestone-lanes.html", "c08-stage-channel.html", "c09-metric-lockup.html",
  "c10-decision-interface.html",
];
const exemplars = {
  "c01-structural-rank.html": { family: "rail-rise", cue: "rail-rise", animation: "mx-rail-rise" },
  "c03-signal-trend.html": { family: "path-trace", cue: "trace", animation: "mx-route" },
  "c08-stage-channel.html": { family: "stage-interlock", cue: "interlock", animation: "mx-interlock" },
  "c10-decision-interface.html": { family: "decision-readout", cue: "readout", animation: "mx-readout" },
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
  if (textRatio < 7) fail(`tokens:${name}`, `ink/bg contrast ${textRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `ink/bg contrast ${textRatio.toFixed(2)}`);
  if (signalRatio < 3) fail(`tokens:${name}`, `signal/bg contrast ${signalRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `signal/bg contrast ${signalRatio.toFixed(2)}`);
  if (matrixStrongRatio < 5) fail(`tokens:${name}`, `matrixStrong/bg contrast ${matrixStrongRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `matrixStrong/bg contrast ${matrixStrongRatio.toFixed(2)}`);
  if (matrixQuietRatio < 3.5) fail(`tokens:${name}`, `matrixQuiet/bg contrast ${matrixQuietRatio.toFixed(2)}`);
  else pass(`tokens:${name}`, `matrixQuiet/bg contrast ${matrixQuietRatio.toFixed(2)}`);
}

for (const file of chartFiles) {
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  const scope = `static:${file}`;
  if (!source.includes('viewBox="0 0 1172 500"')) fail(scope, "missing v2 viewBox");
  if (!source.includes("--matrix-strong:") || !source.includes("--matrix-quiet:")) fail(scope, "missing matrix contrast tokens");
  if (/class="[^"]*index[^"]*"[^>]*font-size="11"/.test(source)) fail(scope, "dot-matrix text below 12px");
  if (!source.includes('data-motion="align"') || !source.includes('data-motion="dock"') || !source.includes('data-motion="lock"')) fail(scope, "missing motion primitives");
  if (!source.includes('data-total-brief="') || !source.includes('data-total-standard="') || !source.includes('data-total-story="')) fail(scope, "missing profile totals");
  if (!source.includes("prefers-reduced-motion") || !source.includes("window.Moxing")) fail(scope, "missing motion accessibility/runtime API");
  if (/<canvas\b/i.test(source)) fail(scope, "canvas is not allowed");
  if (/(?:src|href)\s*=\s*["']https?:\/\//i.test(source) || /url\(\s*["']?https?:\/\//i.test(source)) fail(scope, "external runtime URL");
  if (/paper|boardroom|mori|dawn/i.test(source)) fail(scope, "legacy theme residue");
  if (!/<h1\b[^>]*class="chart-title"[^>]*>[^<]+<\/h1>/i.test(source)) fail(scope, "missing conclusion title");
  if (!failures.some((item) => item.scope === scope)) pass(scope, "v2 static contract");
}

for (const [file, expected] of Object.entries(exemplars)) {
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  const scope = `choreography:${file}`;
  if (!source.includes(`data-choreography="${expected.family}"`)) fail(scope, `missing ${expected.family} family`);
  if (!source.includes(`data-choreo="${expected.cue}"`)) fail(scope, `missing ${expected.cue} cue`);
  const explicit = source.match(new RegExp(`data-choreo="${expected.cue}"[^>]*style="([^"]+)"`))?.[1] || "";
  if (!explicit.includes("--delay-brief:") || !explicit.includes("--delay-story:")) fail(scope, "cue lacks independent profile timing");
  if (!failures.some((item) => item.scope === scope)) pass(scope, `${expected.family} with independent profile timing`);
}

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
      overflow: document.body.scrollWidth > 1280 || document.body.scrollHeight > 720,
    };
  });
  if (state.width !== 1280 || state.height !== 720) fail(scope, `container ${state.width}x${state.height}`);
  if (state.svg !== 1 || state.text === 0 || state.shapes === 0) fail(scope, `svg=${state.svg} text=${state.text} shapes=${state.shapes}`);
  if (state.overflow) fail(scope, "page overflow");
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
const activeMotion = await motionPage.evaluate(() => document.getAnimations().filter((item) => item.playState === "running").length);
if (activeMotion < 3) fail("motion", `only ${activeMotion} active animations`);
else pass("motion", `${activeMotion} deterministic animations active`);
await motionPage.evaluate(() => window.Moxing.setSurface("dark"));
const darkSurface = await motionPage.evaluate(() => document.documentElement.dataset.surface);
if (darkSurface !== "dark") fail("motion", "dark surface toggle failed");
else pass("motion", "dark surface toggle");
await motionContext.close();

const profileRanges = {
  brief: [900, 1200],
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
    observed[profile] = await page.evaluate((cue) => {
      const element = document.querySelector(`[data-choreo="${cue}"]`);
      const lock = document.querySelector('[data-choreo="alarm"]');
      const style = element ? getComputedStyle(element) : null;
      return {
        profile: window.Moxing?.profile,
        duration: window.Moxing?.duration,
        delay: element ? Number.parseFloat(element.style.getPropertyValue("--active-delay")) : null,
        lockDelay: lock ? Number.parseFloat(lock.style.getPropertyValue("--active-delay")) : null,
        animation: style?.animationName,
        running: document.getAnimations().filter((item) => item.playState === "running").length,
      };
    }, expected.cue);
    await page.evaluate(() => window.Moxing.settle());
  }
  const scope = `profiles:${file}`;
  for (const [profile, state] of Object.entries(observed)) {
    const [minimum, maximum] = profileRanges[profile];
    if (state.profile !== profile) fail(scope, `${profile} runtime reported ${state.profile}`);
    if (state.duration < minimum || state.duration > maximum) fail(scope, `${profile} duration ${state.duration}`);
    if (state.animation !== expected.animation) fail(scope, `${profile} animation ${state.animation}`);
    if (state.running < 3) fail(scope, `${profile} only ${state.running} active animations`);
  }
  const briefRatio = observed.brief.delay / observed.standard.delay;
  const storyRatio = observed.story.delay / observed.standard.delay;
  if (Math.abs(briefRatio - 0.72) < 0.01 && Math.abs(storyRatio - 1.8) < 0.01) fail(scope, "profiles are uniform speed multipliers");
  if (!(observed.standard.delay < observed.standard.lockDelay)) fail(scope, `primary cue ${observed.standard.delay} does not precede lock ${observed.standard.lockDelay}`);
  if (!failures.some((item) => item.scope === scope)) pass(scope, `${expected.family} brief/standard/story choreography`);
  await context.close();
}

const reducedContext = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: "reduce" });
const reducedPage = await reducedContext.newPage();
await reducedPage.goto(pathToFileURL(path.join(templatesDir, "c03-signal-trend.html")).href, { waitUntil: "load" });
await reducedPage.waitForTimeout(80);
const reducedState = await reducedPage.evaluate(() => ({ running: document.getAnimations().filter((item) => item.playState === "running").length, complete: document.querySelector(".chart-container")?.classList.contains("is-complete") }));
if (reducedState.running || !reducedState.complete) fail("reduced-motion", JSON.stringify(reducedState));
else pass("reduced-motion", "locked frame without motion");
await reducedContext.close();

for (const file of ["c01-structural-rank.html", "c03-signal-trend.html", "c08-stage-channel.html", "c10-decision-interface.html"]) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
  await page.evaluate(() => document.fonts?.ready || Promise.resolve());
  await page.screenshot({ path: path.join(previewDir, `v2-${file.slice(0, 3)}.png`) });
  await context.close();
  pass(`preview:${file}`, "locked preview exported");
}

const galleryContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const galleryPage = await galleryContext.newPage();
await galleryPage.goto(pathToFileURL(path.join(templatesDir, "gallery.html")).href, { waitUntil: "load" });
const galleryCards = await galleryPage.locator(".card").count();
if (galleryCards !== 10) fail("gallery", `${galleryCards} cards`);
else pass("gallery", "10 compact v2 cards");
await galleryContext.close();
await browser.close();

const report = { generatedAt: new Date().toISOString(), status: failures.length ? "failed" : "passed", checks, failures };
fs.writeFileSync(path.join(previewDir, "qa-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ status: report.status, passed: checks.length, failed: failures.length, failures }, null, 2));
process.exitCode = failures.length ? 1 : 0;
