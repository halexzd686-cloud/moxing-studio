# Moxing Studio v2 — Handoff

> Updated: 2026-08-20
>
> Branch: `codex/v2.1-production-rollout`
>
> Status: A1 Direct Canvas migration complete for C1/C2/C4/C5/C7/C9/C10; A2 is next
>
> Visual review: C1 Direct Canvas, C14 Embedded Evidence, and C6 Evidence Interface approved on 2026-08-20

## Product contract

- Canonical canvas: 1280×720, responsive scale through SVG/viewer.
- Final geometry is generated in Python and remains readable without JavaScript.
- `ALIGN`, `DOCK`, `ROUTE`, and `LOCK` remain authoring semantics; production compiles them into 2–4 macro carriers selected independently from layout mode.
- A / Direct Canvas preserves the full plot; B / Embedded Evidence uses verified natural whitespace; C / Evidence Interface reserves a 220px side bay and 28px safety gap.
- Approved mapping: A = C1/C2/C4/C5/C7/C9/C10/C11/C12/C20; B = C13/C14/C16/C17/C18/C19/C21/C23/C24; C = C3/C6/C8/C15/C22.
- `brief`, `standard`, and `story` timing profiles share one motion grammar.
- Light/dark surfaces share one structural identity.
- All chart contracts share the approved zero-padded device address, live data-shape metadata, calibration ticks, and coded control dock.
- Repository templates link local fonts; custom deliverables embed fonts by default.

## Architecture

```text
moxing/
├── core.py          SVG primitives, tokens, HTML shell, runtime
└── charts.py        C1–C24 contracts and shared-family renderers
references/
├── visual-charter.md
├── motion-system.md
├── presentation-modes.md
└── chart-contracts.md
tokens/system.json   semantic colour, type, geometry, and motion tokens
tokens/presentation-modes.json   approved C1–C24 layout/motion mapping
assets/fonts/        subset WOFF2 and OFL licences
scripts/
├── render.py
├── build_templates.py
├── build_gallery.py
├── export.py
├── export-motion.mjs
├── subset_fonts.py
├── export_examples.py
├── validate_skill.py
├── validate_presentation_modes.py
├── validate_presentation_carriers.py
├── test_boundaries.py
└── validate.mjs
examples/data/       generated C1–C24 copyable JSON inputs
.github/workflows/   CI and GitHub Pages deployment
```

## Build and test

```powershell
python scripts/build_templates.py
python scripts/build_gallery.py
python scripts/validate_presentation_modes.py
python scripts/validate_presentation_carriers.py
python scripts/test_boundaries.py
node scripts/validate.mjs .
```

If Playwright is installed outside the project, set `MOXING_PLAYWRIGHT_PATH`. Set `MOXING_BROWSER_EXECUTABLE` to Chrome or Edge when the bundled browser is unavailable.

## Current QA

- 103 boundary render cases pass.
- 232 browser/static/motion/layout/readability/gallery-scheduling/frame-pacing checks pass; see `docs/previews/qa-report.json`.
- The presentation mapping passes 13 checks and the carrier/A1 architecture passes 13 checks.
- C1/C2/C4/C5/C7/C9/C10 contain no side bay or detached evidence card; each compiles playback to `DATA_FIELD → TARGET_LOCK` with two composited layers.
- Thirteen signature locked-frame PNGs form the current visual baseline; A1 intentionally updates C1/C5/C10 while non-A1 signatures remain structurally unchanged.
- The approved four-chart Precision Interface Lab passes 17 focused layout, motion-layer, and narrow-viewport checks.
- All 24 templates render with and without JavaScript.
- Reduced-motion mode settles immediately.
- No external runtime requests.
- All 24 templates scan evidence plates against critical plot geometry with zero collisions; all 12 migrated Precision charts compare the two SVG viewports in screen coordinates.
- All 24 templates check filled-mark label contrast on both light and dark surfaces.
- Signature locked-frame previews cover foundation, commerce, finance, and analysis contracts.

## v1 migration

The reusable data contracts, numerical formatting, boundary cases, browser detection, and static-fallback principle were retained. Six legacy themes, colour-substitution gallery, legacy SVG silhouettes, system-only font stack, and tooltip-only JavaScript restrictions were removed. The complete former project remains recoverable from tag `v1.0`.

## Next maintenance steps

1. Migrate A2 C11/C12/C20 while preserving their existing full-width geometry and adding only data-bound local locks.
2. Migrate B1 C13/C14/C16, then B2 C17/C18/C19/C21/C23/C24; verify every local evidence anchor against critical geometry.
3. Consolidate batch C1 (C3/C6/C8/C15/C22) on the shared full-interface carrier without changing their approved compositions.
4. Run presentation-mode, carrier, boundary, browser, and Lab QA before each batch is accepted.
