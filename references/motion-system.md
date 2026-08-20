# Motion System

## Semantic sequence

Every chart interprets its structure through four semantic primitives:

1. `ALIGN` — establish datum, scale, and anchors.
2. `DOCK` — assemble data components into the structure.
3. `ROUTE` — reveal relationships along time, dependency, or flow.
4. `LOCK` — attach the conclusion and leave the signal mark in its final position.

These primitives are authoring semantics, not a requirement to animate every mark. Production playback compiles them into a small interface sequence so motion explains structure without producing dozens of simultaneous animations.

## Production presentation sequences

Production playback is selected from the chart's presentation mode, not from visual preference:

- **A / Direct Canvas:** `DATA_FIELD → TARGET_LOCK`, normally 2–3 macro layers.
- **B / Embedded Evidence:** `DATA_FIELD → RELATIONSHIP → LOCAL_EVIDENCE → TARGET_LOCK`, maximum 4 macro layers.
- **C / Evidence Interface:** `DATA_FIELD → EVIDENCE_BAY → TERMINAL → TARGET_LOCK`, maximum 4 macro layers.

The complete plot enters as one composited `DATA_FIELD` layer. It absorbs `ALIGN`, `DOCK`, and ordinary repeated marks. A separate relationship carrier is allowed only for a genuine trace, route, or matrix address. Do not animate individual bars, cells, candles, glyphs, labels, or repeated nodes.

Only C mode uses the cropped split body. Its evidence plate belongs to an independent SVG in the 220px side bay; only ports, addresses, and the target lock remain in the plot foreground. B mode keeps the full plot and docks one local capsule in verified natural whitespace. A mode keeps the full plot and adds no evidence container.

The approved visual baselines are C1 for A, C14 for B, and C6 for C. The complete mapping and migration order live in [presentation-modes.md](presentation-modes.md). The previous rule that applied the side bay to the complete foundation family is retired.

## Profiles

| Profile | Total | Use |
|---|---:|---|
| `brief` | 0.9–1.2 s | presentation, repeated slides |
| `standard` | 1.4–2.2 s | default HTML and gallery |
| `story` | 2.5–5 s | editorial narrative |

Profiles use independent timelines rather than uniform playback speed. `brief` compresses reading furniture, `standard` preserves the full structural explanation, and `story` adds a deliberate pause before the conclusion. Shape and final visual identity remain unchanged.

## Choreography families

The primitives stay shared, but the data relationship selects the movement family:

- `rail-rise` — C1 establishes the datum, seats columns upward from the rail, then locks the leader.
- `ranked-rail` — C2 reveals ranked labels, loads horizontal rails in order, then locks the top evidence.
- `path-trace` — C3 calibrates the field, draws the series in time order, pins observed points, then locks the peak/latest reading.
- `field-aggregation` — C4 seats discrete units into a field before the legend and dominant share lock.
- `band-routing` — C5 fills each composition row from left to right while preserving segment order, then locks the latest mix.
- `ledger-interlock` — C6 alternates contribution docking and balance connectors so the running ledger is causal.
- `milestone-routing` — C7 calibrates time lanes, docks task windows, routes progress, then locks the active-work count.
- `stage-interlock` — C8 alternates connector routing and stage docking so the conversion chain is assembled in causal order; the largest loss locks last.
- `metric-readout` — C9 establishes the KPI, routes progress toward the target, then exposes context plates.
- `decision-readout` — C10 establishes the hero decision first, assembles comparisons second, then exposes the risk plate.
- `sector-lock` — C11 seats sectors around a fixed centre, then locks the dominant share.
- `metric-pulse` — C12 aligns repeated panels and routes each metric independently before exposing end states.
- `pareto-routing` — C13 assembles ranked contribution bars, routes cumulative share, then locks the 80% boundary.
- `cohort-seating` / `matrix-seating` — C14, C20, and C22 seat cells in reading order before locking the decisive cell.
- `flow-routing` — C15 routes weighted links between levelled nodes and locks the weakest effective flow.
- `quadrant-lock` — C16 calibrates axes, pins observations by area, then locks the priority point.
- `market-build` / `curve-routing` — C17 and C19 construct market observations or maturity points before routing the price relationship.
- `drawdown-routing` / `forecast-routing` / `control-lock` — C18, C23, and C24 establish time, route the evidence, then lock risk, uncertainty, or exception.
- `distribution-build` — C21 assembles bins, interlocks the quartile box, then locks the median.

Do not apply a family because its movement looks attractive. Select it from the encoded relationship. Additional charts may reuse a family only when their reading order is genuinely equivalent.

## Runtime contract

- SVG geometry and final labels are generated before runtime.
- JavaScript only schedules states; it does not compute essential layout.
- Without JavaScript, the final locked state is immediately visible.
- A standalone chart may play on first viewport entry. Controls provide replay and pause/resume.
- A gallery must disable iframe autoplay and remain completely static until the user requests replay. Replay settles every other iframe and calls the existing runtime without reloading the selected iframe.
- Replay restarts on consecutive animation frames; do not force synchronous layout with `offsetWidth`.
- Honour `prefers-reduced-motion`; show the final state without staged motion.
- Use deterministic delays. Do not use random motion, bounce, elastic easing, or endless loops.
- Animation ends in a readable still frame suitable for SVG/PNG export.

## Primitive behaviour

- `ALIGN`: short line draw or 4–8 px fade/shift; 140–260 ms.
- `DOCK`: 12–32 px translation toward a datum with decisive cubic easing; 420–850 ms.
- `ROUTE`: path draw or sequential activation in the true data direction; 320–700 ms.
- `LOCK`: 4–8% scale settle plus signal reveal; 180–340 ms.

Only elements with real semantic relationships should route or pulse. Decorative scanning is not a default primitive.
