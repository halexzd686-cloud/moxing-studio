#!/usr/bin/env node
/** Moxing Studio v1.0 自动验收：静态契约、浏览器、无 JS、主题预览。 */
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { pathToFileURL } from "node:url";

const root = path.resolve(process.argv[2] || ".");
const templatesDir = path.join(root, "templates");
const previewDir = path.join(root, "docs", "previews");
const browserExecutable = process.env.MOXING_BROWSER_EXECUTABLE;
let playwright;
try {
  playwright = await import("playwright");
} catch (error) {
  const playwrightPath = process.env.MOXING_PLAYWRIGHT_PATH;
  if (!playwrightPath) {
    throw new Error("未找到 playwright；请安装依赖或设置 MOXING_PLAYWRIGHT_PATH", { cause: error });
  }
  playwright = await import(pathToFileURL(path.join(playwrightPath, "index.mjs")));
}
const { chromium } = playwright;
fs.mkdirSync(previewDir, { recursive: true });

const chartFiles = [
  "c01-bar.html", "c02-hbar.html", "c03-line.html", "c04-donut.html",
  "c05-stacked.html", "c06-waterfall.html", "c07-gantt.html",
  "c08-funnel.html", "c09-kpi.html", "c10-compare.html",
];
const themes = ["paper", "ink", "boardroom", "tech", "mori", "dawn"];
const failures = [];
const checks = [];
const fail = (scope, message) => failures.push({ scope, message });
const pass = (scope, message) => checks.push({ scope, message });

function contrastRatio(a, b) {
  const lum = (hex) => {
    const parts = hex.slice(1).match(/../g).map((v) => parseInt(v, 16) / 255);
    const rgb = parts.map((v) => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
  };
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

const themeSource = fs.readFileSync(path.join(root, "tokens", "themes.js"), "utf8");
const themeTokens = vm.runInNewContext(`${themeSource}\nTHEMES`);
for (const name of themes) {
  const t = themeTokens[name];
  if (!t) { fail("themes", `缺少 ${name}`); continue; }
  const txtRatio = contrastRatio(t.TXT, t.BG);
  const mutRatio = contrastRatio(t.MUT, t.BG);
  if (txtRatio < 7) fail(name, `TXT/BG 对比度仅 ${txtRatio.toFixed(2)}`);
  else pass(name, `TXT/BG 对比度 ${txtRatio.toFixed(2)}`);
  if (mutRatio < 3) fail(name, `MUT/BG 对比度仅 ${mutRatio.toFixed(2)}`);
  else pass(name, `MUT/BG 对比度 ${mutRatio.toFixed(2)}`);
}

for (const file of chartFiles) {
  const scope = file;
  const source = fs.readFileSync(path.join(templatesDir, file), "utf8");
  if (!/<svg\b[^>]*viewBox="0 0 1184 578"/i.test(source)) fail(scope, "缺少预期的 1184×578 内层 SVG viewBox");
  if (/<canvas\b/i.test(source)) fail(scope, "包含 canvas");
  if (/(?:src|href)\s*=\s*["']https?:\/\//i.test(source) || /url\(\s*["']?https?:\/\//i.test(source)) fail(scope, "包含外部资源 URL");
  if ((source.match(/<script\b/gi) || []).length > 1) fail(scope, "包含多个 script，需确认是否仅为 tooltip");
  if (!/<div\b[^>]*class="chart-title"[^>]*>[^<]+<\/div>/i.test(source)) fail(scope, "缺少静态结论标题");
}

const launchOptions = { headless: true };
if (browserExecutable) launchOptions.executablePath = browserExecutable;
const browser = await chromium.launch(launchOptions);

async function inspectTemplate(file, javaScriptEnabled) {
  const scope = `${file}:${javaScriptEnabled ? "js" : "no-js"}`;
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
    javaScriptEnabled,
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const externalRequests = [];
  const failedRequests = [];
  page.on("console", (msg) => { if (msg.type() === "error") consoleErrors.push(msg.text()); });
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    const url = request.url();
    if (!url.startsWith("file:") && !url.startsWith("data:")) externalRequests.push(url);
  });
  page.on("requestfailed", (request) => failedRequests.push(request.url()));
  await page.goto(pathToFileURL(path.join(templatesDir, file)).href, { waitUntil: "load" });
  const state = await page.evaluate(() => {
    const svg = document.querySelector("svg");
    const container = document.querySelector(".chart-container");
    const containerRect = container?.getBoundingClientRect();
    return {
      svgCount: document.querySelectorAll("svg").length,
      viewBox: svg?.getAttribute("viewBox"),
      containerWidth: containerRect?.width,
      containerHeight: containerRect?.height,
      bodyScrollWidth: document.body.scrollWidth,
      bodyScrollHeight: document.body.scrollHeight,
      title: document.title,
      textCount: document.querySelectorAll("svg text").length,
    };
  });
  if (state.svgCount !== 1) fail(scope, `SVG 数量为 ${state.svgCount}`);
  if (state.viewBox !== "0 0 1184 578") fail(scope, `viewBox=${state.viewBox}`);
  if (state.containerWidth !== 1280 || state.containerHeight !== 720) fail(scope, `定尺容器为 ${state.containerWidth}×${state.containerHeight}`);
  if (state.bodyScrollWidth > 1280 || state.bodyScrollHeight > 720) fail(scope, `页面溢出 ${state.bodyScrollWidth}×${state.bodyScrollHeight}`);
  if (state.textCount === 0) fail(scope, "SVG 内没有静态文本");
  if (consoleErrors.length) fail(scope, `console error: ${consoleErrors.join(" | ")}`);
  if (pageErrors.length) fail(scope, `page error: ${pageErrors.join(" | ")}`);
  if (externalRequests.length) fail(scope, `外部请求: ${externalRequests.join(" | ")}`);
  if (failedRequests.length) fail(scope, `失败请求: ${failedRequests.join(" | ")}`);
  if (![state.svgCount, state.textCount].includes(0) && !consoleErrors.length && !pageErrors.length && !externalRequests.length && !failedRequests.length) {
    pass(scope, "静态 SVG、尺寸、控制台与请求检查通过");
  }
  await context.close();
}

for (const file of chartFiles) {
  await inspectTemplate(file, true);
  await inspectTemplate(file, false);
}

const galleryContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
const galleryPage = await galleryContext.newPage();
const galleryErrors = [];
galleryPage.on("console", (msg) => { if (msg.type() === "error") galleryErrors.push(msg.text()); });
galleryPage.on("pageerror", (error) => galleryErrors.push(error.message));
await galleryPage.goto(pathToFileURL(path.join(templatesDir, "gallery.html")).href, { waitUntil: "load" });
const cardCount = await galleryPage.locator(".card").count();
if (cardCount !== 60) fail("gallery", `卡片数量为 ${cardCount}`);
for (const theme of themes) {
  await galleryPage.selectOption("#themeSelect", theme);
  const visibleCount = await galleryPage.locator(`.card[data-theme="${theme}"]:visible`).count();
  if (visibleCount !== 10) fail(`gallery:${theme}`, `可见卡片数量为 ${visibleCount}`);
  const card = galleryPage.locator(`.card[data-theme="${theme}"][data-chart="c10"]`);
  await card.screenshot({ path: path.join(previewDir, `${theme}.png`) });
  pass(`gallery:${theme}`, "10 个图型可见并已导出 C10 主题样张");
}
if (galleryErrors.length) fail("gallery", `浏览器错误: ${galleryErrors.join(" | ")}`);
await galleryContext.close();

const noJsGalleryContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, javaScriptEnabled: false });
const noJsGalleryPage = await noJsGalleryContext.newPage();
await noJsGalleryPage.goto(pathToFileURL(path.join(templatesDir, "gallery.html")).href, { waitUntil: "load" });
const noJsVisible = await noJsGalleryPage.locator('.card[data-theme="paper"]:visible').count();
if (noJsVisible !== 10) fail("gallery:no-js", `paper 可见卡片数量为 ${noJsVisible}`);
else pass("gallery:no-js", "禁用 JS 时 paper 主题 10 个图型完整可见");
await noJsGalleryContext.close();
await browser.close();

const report = {
  generatedAt: new Date().toISOString(),
  status: failures.length ? "failed" : "passed",
  checks,
  failures,
};
fs.writeFileSync(path.join(previewDir, "qa-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ status: report.status, passed: checks.length, failed: failures.length, failures }, null, 2));
process.exitCode = failures.length ? 1 : 0;
