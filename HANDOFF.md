# Moxing Studio v2 — Handoff

> Updated: 2026-08-19
>
> Branch: `v2.0.2-layout-safety`
>
> Status: v2.0.2 release candidate; evidence-lane layout and plate/plot collision safeguards implemented
>
> Visual review: approved on 2026-08-19

## Product contract

- Canonical canvas: 1280×720, responsive scale through SVG/viewer.
- Final geometry is generated in Python and remains readable without JavaScript.
- Inline vanilla JavaScript schedules `ALIGN`, `DOCK`, `ROUTE`, and `LOCK`.
- `brief`, `standard`, and `story` timing profiles share one motion grammar.
- Light/dark surfaces share one structural identity.
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
- 168 browser/static/motion/layout checks pass; see `docs/previews/qa-report.json`.
- All 24 templates render with and without JavaScript.
- Reduced-motion mode settles immediately.
- No external runtime requests.
- All 24 templates scan evidence plates against critical plot geometry with zero collisions.
- Signature locked-frame previews cover foundation, commerce, finance, and analysis contracts.

## v1 migration

The reusable data contracts, numerical formatting, boundary cases, browser detection, and static-fallback principle were retained. Six legacy themes, colour-substitution gallery, legacy SVG silhouettes, system-only font stack, and tooltip-only JavaScript restrictions were removed. The complete former project remains recoverable from tag `v1.0`.

## Next release steps

1. Visually review the left evidence lane on C13, C15–C19, C21, C23, and C24.
2. Merge `v2.0.2-layout-safety` after the gallery review passes.
3. Publish a v2.0.2 patch release after CI and Pages pass remotely.
