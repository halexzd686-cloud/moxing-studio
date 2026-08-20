# Presentation Modes

This reference is the approved layout contract for C1–C24. The machine-readable source of truth is [`tokens/presentation-modes.json`](../tokens/presentation-modes.json).

Presentation mode and motion grammar are independent decisions:

- **Presentation mode** decides where supporting evidence lives.
- **Motion grammar** decides how the encoded relationship is explained.

Never choose the full evidence interface merely because it looks more technical.

## Mode selection

### A / Direct Canvas

Use when the conclusion is already visible in the primary geometry. Keep the complete plot width and use only a local target lock or leader. Do not create an evidence bay or evidence card.

Sequence: `DATA_FIELD → TARGET_LOCK`, normally 2–3 macro layers.

### B / Embedded Evidence

Use when a derived value or relationship needs explanation and the chart owns stable natural whitespace. Dock one compact evidence capsule in that whitespace and connect it with a short local leader. It must not cover marks, labels, axes, row/column headings, or uncertainty ranges.

Sequence: `DATA_FIELD → RELATIONSHIP → LOCAL_EVIDENCE → TARGET_LOCK`, maximum 4 macro layers.

### C / Evidence Interface

Use when the reasoning chain is as important as the result, or when the chart has no safe internal whitespace. Reserve the 220px evidence bay and 28px safety gap. The bay, local terminal, and target lock must refer to the same evidence ID.

Sequence: `DATA_FIELD → EVIDENCE_BAY → TERMINAL → TARGET_LOCK`, maximum 4 macro layers.

## Approved C1–C24 mapping

| ID | Contract | Mode | Motion | Evidence treatment | Risk | Batch |
|---|---|---|---|---|---|---|
| C1 | Structural Rank | A | assemble | leader lock on the winning bar | low | A1 |
| C2 | Ranked Rail | A | assemble | top-rank lock at the rail end | medium | A1 |
| C3 | Signal Trend | C | trace | latest/peak evidence in side bay | low | C1 |
| C4 | Composition Field | A | assemble | dominant-share lock inside the field | low | A1 |
| C5 | Composition Bands | A | route | latest-mix lock on the final band | medium | A1 |
| C6 | Ledger Steps | C | route | net-change evidence in side bay | low | C1 |
| C7 | Milestone Lanes | A | route | active-lane lock inside the timeline | medium | A1 |
| C8 | Stage Channel | C | route | bottleneck evidence in side bay | low | C1 |
| C9 | Metric Lockup | A | readout | the hero metric is the evidence | low | A1 |
| C10 | Decision Interface | A | readout | local risk lock beside the exception | low | A1 |
| C11 | Sector Lock | A | assemble | dominant-sector lock beside the sector | low | A2 |
| C12 | Metric Small Multiples | A | trace | aligned end-state locks, no separate plate | medium | A2 |
| C13 | Pareto Contribution | B | route | capsule beside the 80% threshold | medium | B1 |
| C14 | Cohort Matrix | B | scan | capsule in the triangular empty field | medium | B1 |
| C15 | Commerce Flow | C | route | leak-path evidence in side bay | high | C1 |
| C16 | Decision Bubble Matrix | B | assemble | capsule in an unused quadrant region | medium | B1 |
| C17 | Market Candles | B | assemble | breakout capsule above/right of the market field | high | B2 |
| C18 | Performance Drawdown | B | trace | capsule in the stable gap between panels | high | B2 |
| C19 | Yield Curve | B | trace | capsule after the curve endpoints | medium | B2 |
| C20 | Sensitivity Matrix | A | scan | selected-cell lock; colour field remains primary | medium | A2 |
| C21 | Distribution Profile | B | assemble | capsule in the quiet tail region | medium | B2 |
| C22 | Correlation Matrix | C | scan | pair evidence in side bay | medium | C1 |
| C23 | Forecast Fan | B | trace | range capsule after the forecast endpoint | high | B2 |
| C24 | Control Chart | B | trace | exception capsule beside the out-of-control point | medium | B2 |

Totals: **A 10 / B 9 / C 5**. Approved visual baselines: **C1 / C14 / C6** respectively.

## Motion grammar

- `assemble` — establish a datum, then seat a complete group of marks as one carrier.
- `trace` — reveal a genuine ordered path such as time, maturity, performance, or uncertainty.
- `route` — explain causal transfer, dependency, conversion, or running balance.
- `scan` — resolve a row/column or matrix address; never add decorative radar sweeps.
- `readout` — expose a metric and its context without manufacturing spatial movement.

Repeated marks may be authored with detailed `ALIGN / DOCK / ROUTE / LOCK` semantics, but production playback compiles them into 2–4 macro carriers. Do not animate every bar, cell, candle, label, or glyph.

## Migration batches

1. **I0 / carriers** — replace the binary `precision | legacy` branch with explicit `direct | embedded | interface` carriers. Preserve final SVG geometry and static fallbacks.
2. **A1 / direct foundation** — C1, C2, C4, C5, C7, C9, C10. This removes the unnecessary side bay reported in gallery review.
3. **A2 / direct expansion** — C11, C12, C20.
4. **B1 / embedded canaries** — C13, C14, C16. C14 is the approved reference for local evidence and matrix scan.
5. **B2 / embedded specialist** — C17, C18, C19, C21, C23, C24. Validate each natural-whitespace anchor independently.
6. **C1 / interface consolidation** — C3, C6, C8, C15, C22. Preserve their approved side-bay compositions while moving them onto the shared carrier API.

Do not combine these batches into one visual change. Each batch must pass before the next starts.

## Acceptance gates

- Every chart resolves to exactly one presentation mode and one motion grammar.
- A mode contains no side bay or detached evidence card.
- B mode contains no split body; its evidence capsule stays inside a verified natural-whitespace region.
- C mode reserves the full 220px bay and 28px safety gap; evidence ID, terminal, and target lock agree.
- Critical mark/label collision checks run in light and dark surfaces at 1280px and the narrow gallery viewport.
- No chart runs more than its mode's macro-layer limit.
- Gallery playback remains static until requested and never reloads the selected iframe.
- Reduced motion and JavaScript-off states immediately show the complete locked frame.
