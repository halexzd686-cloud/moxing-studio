# Moxing Studio v2 — Handoff

> Updated: 2026-08-21
> Branch: `codex/v2.1-motion-repair`
> Status: motion-v2 replay rewrite complete on the review branch

## Current contract

- Canonical canvas: 1280x720, responsive scaling through SVG and Gallery Viewer.
- Python remains the source of truth for chart geometry and static fallback.
- The three approved carriers are Direct Canvas (A), Embedded Evidence (B), and Evidence Interface (C).
- `ALIGN`, `DOCK`, `ROUTE`, and `LOCK` remain authoring semantics; the runtime compiles them into element-level cues.
- `implicit`, `micro`, and `explicit` lock modes are intentional; a lock ornament is not forced onto every chart.
- `brief`, `standard`, and `story` are independent timing profiles, not simple playback speed labels.

## Motion v2

Replay is a single forward-only state machine:

```text
settle -> is-resetting (one frame) -> is-playing -> is-complete
```

- `is-resetting` clears animated marks immediately and never plays a reverse animation.
- `is-playing` runs only the compiled element-level cue timeline.
- Direct and embedded data-field/plot carrier groups stay static; only marked SVG elements, local evidence, and target locks animate.
- Evidence Interface animates the evidence bay, terminal handshake, and target lock as a separate terminal sequence.
- No rewind phase, second reveal pass, clip-path transition, or `continuity-v1` runtime remains in production templates.
- `prefers-reduced-motion` and `motion=off` settle immediately to the complete frame.

## Approved mapping

- A / Direct Canvas: C1, C2, C4, C5, C7, C9, C10, C11, C12, C20
- B / Embedded Evidence: C13, C14, C16, C17, C18, C19, C21, C23, C24
- C / Evidence Interface: C3, C6, C8, C15, C22

## Gallery

- Desktop keeps the two-column review surface.
- Mobile uses a one-column list, a four-iframe mounted pool, and one isolated full-screen Viewer.
- Portrait supports horizontal detail panning plus `FIT`; landscape preserves the canonical 16:9 stage.
- Gallery iframe URLs use the `motion-v2` build key to prevent stale template caching.

## Build and test

```powershell
python scripts/build_templates.py
python scripts/build_gallery.py
python scripts/validate_presentation_modes.py
python scripts/validate_presentation_carriers.py
python scripts/test_boundaries.py
node scripts/validate.mjs .
```

If Playwright is installed outside the project, set `MOXING_PLAYWRIGHT_PATH`; set `MOXING_BROWSER_EXECUTABLE` when the bundled browser is unavailable.

## QA baseline

- 103 boundary cases pass.
- Presentation mapping: 14/14.
- Carrier contract: 21/21.
- All 24 templates render with and without JavaScript.
- All 24 templates use local fonts and make no external runtime requests.
- Dynamic samples cover all 24 charts and assert the motion-v2 revision, active element cues, reset frame, playing frame, and complete frame.
- Reduced-motion settles immediately.
- Gallery mobile/desktop viewer and mounting checks remain part of the browser validation suite.

## v1 migration

Reusable data contracts, numerical formatting, boundary cases, browser detection, and static fallback were retained. Legacy themes, color-substitution gallery code, old SVG silhouettes, and the old rewind/reveal runtime were removed. The former project remains recoverable from Git tag `v1.0`.

## Next maintenance steps

1. Review the responsive Gallery on a physical phone over the same Wi-Fi preview URL.
2. Freeze the release-candidate visual baseline after desktop and phone review.
3. Merge and push the rollout branch so GitHub Pages publishes the permanent URL.
