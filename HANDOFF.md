# Moxing Studio v2 — Handoff

> Updated: 2026-08-19
>
> Branch: `v2-design`
>
> Status: v2 renderer, 24 public chart contracts, motion gallery, fonts, export, and QA implemented
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
├── test_boundaries.py
└── validate.mjs
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
- 143 browser/static/motion checks pass; see `docs/previews/qa-report.json`.
- All 24 templates render with and without JavaScript.
- Reduced-motion mode settles immediately.
- No external runtime requests.
- Signature locked-frame previews cover foundation, commerce, finance, and analysis contracts.

## v1 migration

The reusable data contracts, numerical formatting, boundary cases, browser detection, and static-fallback principle were retained. Six legacy themes, colour-substitution gallery, legacy SVG silhouettes, system-only font stack, and tooltip-only JavaScript restrictions were removed. The complete former project remains recoverable from tag `v1.0`.

## Next release steps

1. Run the QA commands after any visual change.
2. Merge `v2-design` to `main` when the local release commit is confirmed.
3. Tag the release as `v2.0.0` and attach large video demos to GitHub Releases rather than Git history.
