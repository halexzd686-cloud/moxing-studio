#!/usr/bin/env node
/** Moxing Studio v2 structural, motion, fallback, and visual validation. */
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(process.argv[2] || ".");
const templatesDir = path.join(root, "templates");
const previewDir = path.join(root, "docs", "previews");
const chartFiles = fs.readdirSync(templatesDir).filter((file) => /^c\d{2}-.*\.html$/.test(file)).sort();
const exemplars = {
  "c01-structural-rank.html": { family: "rail-rise", cue: "rail-rise", animation: "mx-rail-rise" },
  "c02-ranked-rail.html": { family: "ranked-rail", cue: "rail-slide", animation: "mx-rail-slide" },
  "c03-signal-trend.html": { family: "path-trace", cue: "trace", animation: "mx-route" },
  "c04-composition-field.html": { family: "field-aggregation", cue: "field-seat", animation: "mx-field-seat" },
  "c05-composition-bands.html": { family: "band-routing", cue: "band-fill", animation: "mx-band-fill" },
  "c06-ledger-steps.html": { family: "ledger-interlock", cue: "field-seat", animation: "mx-field-seat" },
  "c07-milestone-lanes.html": { family: "milestone-routing", cue: "interlock", animation: "mx-interlock" },
  "c08-stage-channel.html": { family: "stage-interlock", cue: "interlock", animation: "mx-interlock" },
  "c09-metric-lockup.html": { family: "metric-readout", cue: "readout", animation: "mx-readout" },
  "c10-decision-interface.html": { family: "decision-readout", cue: "readout", animation: "mx-readout" },
  "c11-sector-lock.html": { family: "sector-lock", cue: "field-seat", animation: "mx-field-seat" },
  "c12-metric-small-multiples.html": { family: "metric-pulse", cue: "trace", animation: "mx-route" },
  "c13-pareto-contribution.html": { family: "pareto-routing", cue: "rail-rise", animation: "mx-rail-rise" },
  "c14-cohort-matrix.html": { family: "cohort-seating", cue: "field-seat", animation: "mx-field-seat" },
  "c15-commerce-flow.html": { family: "flow-routing", cue: "trace", animation: "mx-route" },
  "c16-decision-bubble-matrix.html": { family: "quadrant-lock", cue: "pin", animation: "mx-pin" },
  "c17-market-candles.html": { family: "market-build", cue: "field-seat", animation: "mx-field-seat" },
  "c18-performance-drawdown.html": { family: "drawdown-routing", cue: "trace", animation: "mx-route" },
  "c19-yield-curve.html": { family: "curve-routing", cue: "trace", animation: "mx-route" },
  "c20-sensitivity-matrix.html": { family: "matrix-seating", cue: "field-seat", animation: "mx-field-seat" },
  "c21-distribution-profile.html": { family: "distribution-build", cue: "rail-rise", animation: "mx-rail-rise" },
  "c22-correlation-matrix.html": { family: "matrix-seating", cue: "field-seat", animation: "mx-field-seat" },
  "c23-forecast-fan.html": { family: "forecast-routing", cue: "trace", animation: "mx-route" },
  "c24-control-chart.html": { family: "control-lock", cue: "trace", animation: "mx-route" },
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
  if (!source.includes('viewBox="0 0 1172 500"')) fail(scope, "missing v2 viewBox");
  if (!source.includes("--matrix-strong:") || !source.includes("--matrix-quiet:") || !source.includes("--on-signal:")) fail(scope, "missing contrast tokens");
  if (/class="[^"]*index[^"]*"[^>]*font-size="11"/.test(source)) fail(scope, "dot-matrix text below 12px");
  if (!source.includes('data-motion="align"') || !source.includes('data-motion="dock"') || !source.includes('data-motion="lock"')) fail(scope, "missing motion primitives");
  if (!source.includes('data-total-brief="') || !source.includes('data-total-standard="') || !source.includes('data-total-story="')) fail(scope, "missing profile totals");
  if (!source.includes("prefers-reduced-motion") || !source.includes("window.Moxing")) fail(scope, "missing motion accessibility/runtime API");
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
  if (state.svg !== 1 || state.text === 0 || state.shapes === 0) fail(scope, `svg=${state.svg} text=${state.text} shapes=${state.shapes}`);
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

for (const [file, headingSelector] of Object.entries({
  "c02-ranked-rail.html": ".rank-heading text",
  "c07-milestone-lanes.html": ".milestone-heading text",
})) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();
  await page.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
  const overlap = await page.evaluate((selector) => {
    const plate = document.querySelector(".evidence-plate")?.getBBox();
    if (!plate) return true;
    return [...document.querySelectorAll(selector)].some((element) => {
      const box = element.getBBox();
      return plate.x < box.x + box.width && plate.x + plate.width > box.x && plate.y < box.y + box.height && plate.y + plate.height > box.y;
    });
  }, headingSelector);
  if (overlap) fail(`layout:${file}`, "evidence plate overlaps row heading");
  else pass(`layout:${file}`, "evidence plate clears row headings");
  await context.close();
}

const collisionContext = await browser.newContext({ viewport: { width: 1280, height: 720 } });
const collisionPage = await collisionContext.newPage();
for (const file of chartFiles) {
  await collisionPage.goto(`${pathToFileURL(path.join(templatesDir, file)).href}?motion=off`, { waitUntil: "load" });
  const collisions = await collisionPage.evaluate(() => {
    const plates = [...document.querySelectorAll(".evidence-plate")];
    const geometry = [...document.querySelectorAll([
      "line.rail-strong",
      "path.data-stroke", "path.signal-stroke", "path.secondary-stroke",
      "rect.data-fill", "rect.signal-fill", "rect.secondary-fill", "rect.cat-1",
      "circle.data-fill", "circle.signal-fill", "circle.secondary-fill", "circle.cat-1",
      "polygon.data-fill", "polygon.signal-fill", "polygon.secondary-fill", "polygon.cat-1",
    ].join(","))].filter((element) => !element.closest(".evidence-plate"));
    const overlaps = (a, b) => (
      a.x <= b.x + b.width && a.x + a.width >= b.x
      && a.y <= b.y + b.height && a.y + a.height >= b.y
    );
    return plates.flatMap((plate, plateIndex) => {
      const plateBox = plate.getBBox();
      return geometry.flatMap((element, geometryIndex) => {
        const box = element.getBBox();
        if (!overlaps(plateBox, box)) return [];
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

const galleryContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const galleryPage = await galleryContext.newPage();
await galleryPage.goto(pathToFileURL(path.join(templatesDir, "gallery.html")).href, { waitUntil: "load" });
const galleryCards = await galleryPage.locator(".card").count();
if (galleryCards !== 24) fail("gallery", `${galleryCards} cards`);
else pass("gallery", "24 compact v2 cards");
await galleryContext.close();
await browser.close();

const report = { generatedAt: new Date().toISOString(), status: failures.length ? "failed" : "passed", checks, failures };
fs.writeFileSync(path.join(previewDir, "qa-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ status: report.status, passed: checks.length, failed: failures.length, failures }, null, 2));
process.exitCode = failures.length ? 1 : 0;
