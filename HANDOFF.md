# Moxing Studio v2 — Handoff

> Updated: 2026-08-20
>
> Branch: `codex/v2.1-production-rollout`
>
> Status: v2.1 production rollout phase 2; the approved Precision Interface contract is productionized on C3/C8/C15/C22 for review
>
> Visual review: four representative prototypes approved on 2026-08-20; full production gallery awaits review

## Product contract

- Canonical canvas: 1280×720, responsive scale through SVG/viewer.
- Final geometry is generated in Python and remains readable without JavaScript.
- `ALIGN`, `DOCK`, `ROUTE`, and `LOCK` remain authoring semantics; production canaries compile them into `DATA_FIELD`, `EVIDENCE_BAY`, `TERMINAL`, and one `TARGET_LOCK`.
- C3/C8/C15/C22 render the evidence plate in a true 220px side bay, keep a 28px safety gap, and crop the plot SVG at a chart-specific origin.
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
└── chart-contracts.md
tokens/system.json   semantic colour, type, geometry, and motion tokens
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
├── test_boundaries.py
└── validate.mjs
examples/data/       generated C1–C24 copyable JSON inputs
.github/workflows/   CI and GitHub Pages deployment
```

## Build and test

```powershell
python scripts/build_templates.py
python scripts/build_gallery.py
python scripts/test_boundaries.py
node scripts/validate.mjs .
```

If Playwright is installed outside the project, set `MOXING_PLAYWRIGHT_PATH`. Set `MOXING_BROWSER_EXECUTABLE` to Chrome or Edge when the bundled browser is unavailable.

## Current QA

- 103 boundary render cases pass.
- 212 browser/static/motion/layout/readability/gallery-scheduling/frame-pacing checks pass; see `docs/previews/qa-report.json`.
- The approved four-chart Precision Interface Lab passes 17 focused layout, motion-layer, and narrow-viewport checks.
- All 24 templates render with and without JavaScript.
- Reduced-motion mode settles immediately.
- No external runtime requests.
- All 24 templates scan evidence plates against critical plot geometry with zero collisions; precision canaries compare the two SVG viewports in screen coordinates.
- All 24 templates check filled-mark label contrast on both light and dark surfaces.
- Signature locked-frame previews cover foundation, commerce, finance, and analysis contracts.

## v1 migration

The reusable data contracts, numerical formatting, boundary cases, browser detection, and static-fallback principle were retained. Six legacy themes, colour-substitution gallery, legacy SVG silhouettes, system-only font stack, and tooltip-only JavaScript restrictions were removed. The complete former project remains recoverable from tag `v1.0`.

## Next maintenance steps

1. Review C3, C8, C15, and C22 against the approved Lab in the production gallery.
2. After approval, migrate C1–C10, C11–C16, C17–C20, and C21–C24 in bounded batches.
3. Migrate new charts through the shared `ChartArtwork` / `PrecisionInterface` contract; do not duplicate Lab DOM-patching code or reconnect the side bay across the plot.
4. Run boundary, browser, and Precision Interface Lab QA before every release.
