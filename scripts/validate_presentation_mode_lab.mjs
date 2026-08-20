import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const html = readFileSync(resolve(root, "designs/presentation-mode-lab/index.html"), "utf8");
const css = readFileSync(resolve(root, "designs/presentation-mode-lab/lab.css"), "utf8");
const js = readFileSync(resolve(root, "designs/presentation-mode-lab/lab.js"), "utf8");
const checks = [];

function check(name, condition) {
  checks.push({ name, ok: Boolean(condition) });
}

const sections = Object.fromEntries(["direct", "embedded", "interface"].map((mode) => {
  const start = html.indexOf(`data-specimen="${mode}"`);
  const next = html.indexOf('<section class="mode-card"', start + 1);
  return [mode, html.slice(start, next < 0 ? html.length : next)];
}));

check("three presentation modes", Object.values(sections).every(Boolean));
check("representative charts", ["C01", "C14", "C06"].every((code) => html.includes(code)));
check("direct canvas has no evidence module", !/evidence-bay|embedded-evidence/.test(sections.direct));
check("embedded mode has local evidence", /embedded-evidence/.test(sections.embedded) && !/evidence-bay/.test(sections.embedded));
check("interface mode has evidence bay", /evidence-bay/.test(sections.interface));
check("no production template iframe", !/<iframe/i.test(html));
check("maximum four macro layers per mode", Object.values(sections).every((section) => (section.match(/motion-layer/g) || []).length <= 4));
check("distinct motion grammars", ["assemble", "scan", "route"].every((motion) => html.includes(`data-motion="${motion}"`)));
check("surface tokens", css.includes('body[data-surface="dark"]') && css.includes("--signal:#d85a36"));
check("reduced-motion fallback", css.includes("prefers-reduced-motion:reduce"));
check("prepared single-frame replay restart", js.includes('classList.add("is-preparing")') && js.includes("void stage.offsetWidth") && !js.includes("requestAnimationFrame(() => requestAnimationFrame"));
check("responsive stage scaling", js.includes("viewport.clientWidth / 1280"));

for (const result of checks) console.log(`${result.ok ? "PASS" : "FAIL"} ${result.name}`);
const failed = checks.filter((result) => !result.ok);
console.log(`${checks.length - failed.length}/${checks.length} checks passed`);
if (failed.length) process.exitCode = 1;
