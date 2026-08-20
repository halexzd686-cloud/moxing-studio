# Motion System

## Semantic sequence

Every chart interprets its structure through four semantic primitives:

1. `ALIGN` — establish datum, scale, and anchors.
2. `DOCK` — assemble data components into the structure.
3. `ROUTE` — reveal relationships along time, dependency, or flow.
4. `LOCK` — attach the conclusion and leave the signal mark in its final position.

These primitives are authoring semantics, not a requirement to animate every mark. Production playback compiles them into a small interface sequence so motion explains structure without producing dozens of simultaneous animations.

## Production precision sequence

The default runtime order is:

1. `DATA_FIELD` — the complete plot enters as one composited layer. It absorbs `ALIGN`, `DOCK`, and ordinary routing marks.
2. `EVIDENCE_BAY` — the reserved evidence plate enters after the field is readable.
3. `TERMINAL` — the evidence ID completes its short local handshake.
4. `TARGET_LOCK` — one decisive ring or focus bracket locks the conclusion.

A chart must run no more than four precision animations at once. Do not animate individual bars, cells, glyphs, labels, or repeated nodes in the production sequence.

`DATA_FIELD` is the cropped plot SVG inside the HTML split body. Isolate that carrier with paint containment so complex geometry is rasterized once and reused during transform/opacity playback. The evidence plate belongs to its own SVG in the side bay; only ports, addresses, and the target lock remain in the plot foreground.

C3, C8, C15, and C22 remain the approved visual canaries for `precision-v2.1`. The complete foundation family C1–C10 now shares their production carrier, side-bay separation, terminal overlays, and four-layer motion ceiling. C11–C14, C16–C21, C23, and C24 retain the legacy primitive runtime until their bounded-batch review is complete.

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
