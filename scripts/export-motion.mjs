#!/usr/bin/env node
/** Export Moxing motion to WebM, MP4, or GIF. */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const [inputArg, outputArg, profileArg = "standard"] = process.argv.slice(2);
if (!inputArg || !outputArg) {
  console.error("Usage: node scripts/export-motion.mjs <input.html> <output.webm|mp4|gif> [brief|standard|story]");
  process.exit(1);
}
const input = path.resolve(inputArg);
const output = path.resolve(outputArg);
const profile = ["brief", "standard", "story"].includes(profileArg) ? profileArg : "standard";
let playwright;
try {
  playwright = await import("playwright");
} catch (error) {
  const dependencyPath = process.env.MOXING_PLAYWRIGHT_PATH;
  if (!dependencyPath) throw new Error("playwright missing; set MOXING_PLAYWRIGHT_PATH", { cause: error });
  playwright = await import(pathToFileURL(path.join(dependencyPath, "index.mjs")));
}

fs.mkdirSync(path.dirname(output), { recursive: true });
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "moxing-motion-"));
const rawVideo = path.join(temporary, "capture.webm");
const launchOptions = { headless: true };
if (process.env.MOXING_BROWSER_EXECUTABLE) launchOptions.executablePath = process.env.MOXING_BROWSER_EXECUTABLE;
const browser = await playwright.chromium.launch(launchOptions);
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: temporary, size: { width: 1280, height: 720 } } });
const page = await context.newPage();
await page.goto(`${pathToFileURL(input).href}?motion=${profile}`, { waitUntil: "load" });
await page.evaluate(() => document.fonts?.ready || Promise.resolve());
const video = page.video();
await page.evaluate(() => window.Moxing.replay());
const duration = await page.evaluate(() => window.Moxing?.duration || Number(document.querySelector(".chart-container")?.dataset.total || 1800));
await page.waitForTimeout(duration + 500);
await page.close();
await context.close();
await video.saveAs(rawVideo);
await browser.close();

const extension = path.extname(output).toLowerCase();
if (extension === ".webm") {
  fs.copyFileSync(rawVideo, output);
} else {
  const ffmpeg = process.env.MOXING_FFMPEG || "ffmpeg";
  const check = spawnSync(ffmpeg, ["-version"], { stdio: "ignore" });
  if (check.status !== 0) {
    fs.rmSync(temporary, { recursive: true, force: true });
    throw new Error("MP4/GIF export requires ffmpeg; set MOXING_FFMPEG or export WebM instead");
  }
  if (extension === ".mp4") {
    const result = spawnSync(ffmpeg, ["-y", "-i", rawVideo, "-pix_fmt", "yuv420p", "-movflags", "+faststart", output], { stdio: "inherit" });
    if (result.status !== 0) throw new Error("ffmpeg MP4 conversion failed");
  } else if (extension === ".gif") {
    const palette = path.join(temporary, "palette.png");
    let result = spawnSync(ffmpeg, ["-y", "-i", rawVideo, "-vf", "fps=24,scale=960:-1:flags=lanczos,palettegen", palette], { stdio: "inherit" });
    if (result.status === 0) result = spawnSync(ffmpeg, ["-y", "-i", rawVideo, "-i", palette, "-lavfi", "fps=24,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse", output], { stdio: "inherit" });
    if (result.status !== 0) throw new Error("ffmpeg GIF conversion failed");
  } else {
    throw new Error("output extension must be .webm, .mp4, or .gif");
  }
}
fs.rmSync(temporary, { recursive: true, force: true });
console.log(`exported ${output}`);
