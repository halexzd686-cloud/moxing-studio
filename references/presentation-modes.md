# Presentation Modes

This reference is the approved layout contract for C1–C24. The machine-readable source of truth is [`tokens/presentation-modes.json`](../tokens/presentation-modes.json).

Presentation mode and motion grammar are independent decisions:

- **Presentation mode** decides where supporting evidence lives.
- **Motion grammar** decides how the encoded relationship is explained.

Never choose the full evidence interface merely because it looks more technical.

## Mode selection

### A / Direct Canvas

Use when the conclusion is already visible in the primary geometry. Keep the complete plot width. A target may be implicit in the geometry, reduced to a micro address, or explicitly marked when ambiguity remains. Do not create an evidence bay or evidence card.

Sequence: `DATA_FIELD → RELATIONSHIP → [TARGET_LOCK]`, 2–3 macro layers. The relationship layer carries the chart's own geometry; it must not manufacture a detached evidence object.

### B / Embedded Evidence

Use when a derived value or relationship needs explanation and the chart owns stable natural whitespace. Dock one compact evidence capsule in that whitespace and connect it with a short local leader. It must not cover marks, labels, axes, row/column headings, or uncertainty ranges.

Sequence: `DATA_FIELD → RELATIONSHIP → LOCAL_EVIDENCE → [TARGET_LOCK]`, 3–4 compiled macro layers in production.

### C / Evidence Interface

Use when the reasoning chain is as important as the result, or when the chart has no safe internal whitespace. Reserve the 220px evidence bay and 28px safety gap. The bay, local terminal, and target lock must refer to the same evidence ID.

Sequence: `DATA_FIELD → EVIDENCE_BAY → TERMINAL → [TARGET_LOCK]`, maximum 4 compiled macro layers. When visible, the evidence plate, bay terminal, and target address reuse one zero-padded evidence ID.

## Lock intensity

- `implicit` — the chart's signal colour, area, rank, or position already identifies the conclusion; add no lock group or late lock animation.
- `micro` — retain only a compact socket, endpoint tick, range bracket, or address. Remove focus corners, rings, and long leaders.
- `explicit` — use a focus corner/ring and evidence relationship only when the target cannot be inferred safely from the primary geometry.

## Approved C1–C24 mapping

| ID | Contract | Mode | Motion | Lock | Evidence treatment | Risk | Batch |
|---|---|---|---|---|---|---|---|
| C1 | Structural Rank | A | assemble | micro | compact winner address | low | A |
| C2 | Ranked Rail | A | assemble | micro | compact top-rank address | medium | A |
| C3 | Signal Trend | C | trace | micro | latest/peak evidence in side bay | low | C |
| C4 | Composition Field | A | assemble | implicit | dominant signal cell is the conclusion | low | A |
| C5 | Composition Bands | A | route | implicit | latest mix is resolved by band geometry | medium | A |
| C6 | Ledger Steps | C | route | explicit | net-change evidence in side bay | low | C |
| C7 | Milestone Lanes | A | route | implicit | active progress segment is the conclusion | medium | A |
| C8 | Stage Channel | C | route | explicit | bottleneck evidence in side bay | low | C |
| C9 | Metric Lockup | A | readout | implicit | the hero metric is the evidence | low | A |
| C10 | Decision Interface | A | readout | micro | compact risk address beside the exception | low | A |
| C11 | Sector Lock | A | assemble | implicit | dominant sector colour/area is primary | low | A |
| C12 | Metric Small Multiples | A | trace | implicit | aligned endpoints remain self-evident | medium | A |
| C13 | Pareto Contribution | B | route | explicit | capsule beside the 80% threshold | medium | B |
| C14 | Cohort Matrix | B | scan | explicit | capsule in the triangular empty field | medium | B |
| C15 | Commerce Flow | C | route | explicit | leak-path evidence in side bay | high | C |
| C16 | Decision Bubble Matrix | B | assemble | implicit | capsule plus bubble encoding identifies priority | medium | B |
| C17 | Market Candles | B | assemble | explicit | breakout capsule above/right of the market field | high | B |
| C18 | Performance Drawdown | B | trace | micro | compact drawdown address in the panel gap | high | B |
| C19 | Yield Curve | B | trace | micro | compact maturity endpoint address | medium | B |
| C20 | Sensitivity Matrix | A | scan | implicit | selected cell colour remains primary | medium | A |
| C21 | Distribution Profile | B | assemble | micro | compact tail address beside the capsule | medium | B |
| C22 | Correlation Matrix | C | scan | explicit | pair evidence in side bay | medium | C |
| C23 | Forecast Fan | B | trace | micro | compact terminal range bracket and capsule | high | B |
| C24 | Control Chart | B | trace | explicit | exception capsule beside the out-of-control point | medium | B |

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
2. **A / Direct Canvas group** — C1, C2, C4, C5, C7, C9, C10, C11, C12, C20. Apply and validate the approved C1 language as one production group.
3. **B / Embedded Evidence group** — C13, C14, C16, C17, C18, C19, C21, C23, C24. Apply the approved C14 language as one production group while validating each natural-whitespace anchor.
4. **C / Evidence Interface group** — C3, C6, C8, C15, C22. Preserve the approved C6 interface language and consolidate the shared carrier as one production group.

Complete and validate one presentation group before starting the next. Within a group, review the shared visual language and system behaviour as a batch rather than running per-chart approval loops.

## Acceptance gates

- Every chart resolves to exactly one presentation mode, one motion grammar, and one lock intensity.
- A mode contains no side bay or detached evidence card.
- B mode contains no split body; its evidence capsule stays inside a verified natural-whitespace region.
- C mode reserves the full 220px bay and 28px safety gap; evidence ID, terminal, and target lock agree.
- Critical mark/label collision checks run in light and dark surfaces at 1280px and the narrow gallery viewport.
- No chart runs more than its mode's macro-layer limit.
- Replay enters a prepared first frame before playback; ordered line families never expose the completed path during reset.
- Gallery playback remains static until requested and never reloads the selected iframe.
- Reduced motion and JavaScript-off states immediately show the complete locked frame.
