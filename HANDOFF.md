# Moxing Studio v2 — Handoff

> Updated: 2026-08-20
>
> Branch: `codex/v2.1-motion-repair`
>
> Status: A / Direct Canvas, B / Embedded Evidence, C / Evidence Interface, responsive Gallery, and continuity-v1 replay repair complete on the review branch
>
> Visual review: C1 Direct Canvas, C14 Embedded Evidence, and C6 Evidence Interface approved on 2026-08-20

## Product contract

- Canonical canvas: 1280×720, responsive scale through SVG/viewer.
- Final geometry is generated in Python and remains readable without JavaScript.
- `ALIGN`, `DOCK`, `ROUTE`, and `LOCK` remain authoring semantics; production compiles them into 2–4 macro carriers selected independently from layout mode.
- `LOCK` resolves to `implicit`, `micro`, or `explicit`; it is a semantic terminal state and no longer requires an ornament on every chart.
- Replay uses a visible `is-rewinding` → `is-playing` handoff. Static structure and data-field brightness remain stable; C3/C12/C18/C19/C23/C24 use stable normalized dash paths with a continuous reverse/forward trace. SVG `<g>` layers do not use clip-path transitions.
- A / Direct Canvas preserves the full plot; B / Embedded Evidence uses verified natural whitespace; C / Evidence Interface reserves a 220px side bay and 28px safety gap.
- Approved mapping: A = C1/C2/C4/C5/C7/C9/C10/C11/C12/C20; B = C13/C14/C16/C17/C18/C19/C21/C23/C24; C = C3/C6/C8/C15/C22.
- `brief`, `standard`, and `story` timing profiles share one motion grammar.
- Continuity revision `continuity-v1` groups charts into `trace-overlay`, `data-reveal`, and `evidence-interface` strategies; Gallery iframe URLs use a new build key to avoid stale template cache.
- Light/dark surfaces share one structural identity.
- All chart contracts share the approved zero-padded device address, live data-shape metadata, calibration ticks, and coded control dock.
- Repository templates link local fonts; custom deliverables embed fonts by default.
- Gallery keeps the desktop two-column review surface while mobile uses a one-column four-frame pool and one isolated full-screen Viewer. Portrait supports readable horizontal detail panning plus `FIT`; landscape preserves the canonical 16:9 stage.

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
- 262 browser/static/motion/layout/readability/gallery-scheduling/frame-pacing/mobile-viewer checks pass; see `docs/previews/qa-report.json`.
- The presentation mapping passes 14 checks and the three-carrier A+B+C architecture passes 21 checks.
- The continuity repair passes 103 boundary cases, 14 presentation-mode checks, 21 carrier checks, 24/24 static template checks, and dynamic replay samples for C3/C12/C18/C19/C23/C24 with stable field opacity and active trace animation.
- All ten A charts contain no side bay or detached evidence card; they compile to `DATA_FIELD → RELATIONSHIP → [TARGET_LOCK]` with 2–3 macro layers.
- All nine B charts use the full-width Embedded Evidence carrier and compile to `DATA_FIELD → RELATIONSHIP → LOCAL_EVIDENCE → [TARGET_LOCK]` with 3–4 macro layers.
- Their evidence capsules occupy chart-specific natural whitespace: threshold, triangular matrix void, empty quadrant, chart endpoint, panel gap, or distribution tail. No B chart uses a detached left evidence plate.
- All five C charts preserve their approved trend, ledger, stage, flow, and matrix compositions on one shared Evidence Interface builder. Each compiles to `DATA_FIELD → EVIDENCE_BAY → TERMINAL → TARGET_LOCK`, and its evidence plate, terminal, and target address share one ID.
- Thirteen signature locked-frame PNGs form the current visual baseline; all three production groups are represented while the approved C compositions remain geometrically unchanged.
- The approved four-chart Precision Interface Lab passes 17 focused layout, motion-layer, and narrow-viewport checks.
- All 24 templates render with and without JavaScript.
- Reduced-motion mode settles immediately.
- Replay continuity checks prove the prepared first frame is active before playback and the completed path is never exposed during reset.
- No external runtime requests.
- All 24 templates scan detached and embedded evidence against critical plot geometry with zero collisions; line-path checks sample actual SVG geometry instead of relying on broad path bounding boxes.
- All 24 templates check filled-mark label contrast on both light and dark surfaces.
- Signature locked-frame previews cover foundation, commerce, finance, and analysis contracts.
- Mobile Gallery checks cover 390×844 portrait list/detail/FIT/replay states and the 844×390 landscape safe stage. Offscreen mobile cards are settled and the mounted iframe pool is capped at four.

## v1 migration

The reusable data contracts, numerical formatting, boundary cases, browser detection, and static-fallback principle were retained. Six legacy themes, colour-substitution gallery, legacy SVG silhouettes, system-only font stack, and tooltip-only JavaScript restrictions were removed. The complete former project remains recoverable from tag `v1.0`.

## Next maintenance steps

1. Review the responsive Gallery on a physical phone through the same-Wi-Fi preview URL.
2. Freeze the release candidate visual baseline after desktop and phone review.
3. Merge and push the rollout branch so GitHub Pages publishes the permanent mobile/desktop URL.
