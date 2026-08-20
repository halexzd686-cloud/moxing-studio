# Motion System

## Semantic sequence

Every chart interprets its structure through four authoring primitives:

1. `ALIGN` establishes datum, scale, and anchors.
2. `DOCK` assembles data components into the structure.
3. `ROUTE` reveals relationships along time, dependency, or flow.
4. `LOCK` attaches the conclusion and leaves the signal in its final position.

These are authoring semantics, not a requirement to animate every mark. Production playback compiles them into a small element-level cue timeline so motion explains structure without producing dozens of competing macro animations.

## Production carriers

Production playback is selected from the chart's presentation mode:

- **A / Direct Canvas:** `DATA_FIELD -> RELATIONSHIP -> [TARGET_LOCK]`.
- **B / Embedded Evidence:** `DATA_FIELD -> RELATIONSHIP -> LOCAL_EVIDENCE -> [TARGET_LOCK]`.
- **C / Evidence Interface:** `DATA_FIELD -> EVIDENCE_BAY -> TERMINAL -> [TARGET_LOCK]`.

The A and B data-field/plot carrier groups remain static. Their marked SVG elements receive cues such as `mx-align`, `mx-dock`, `mx-route`, `mx-rail-rise`, `mx-field-seat`, `mx-band-fill`, `mx-interlock`, `mx-readout`, and `mx-pin`. C keeps the approved cropped split body and gives the evidence bay, terminal handshake, and target lock their own terminal sequence.

`LOCK` is a semantic terminal state, not a mandatory ornament. Resolve it as `implicit` when color/position already identifies the conclusion, `micro` for a compact endpoint/address, and `explicit` only when the target remains ambiguous or must connect to evidence.

The approved visual baselines are C1 for A, C14 for B, and C6 for C. The complete mapping and migration order live in [presentation-modes.md](presentation-modes.md).

## Timing profiles

| Profile | Typical total | Use |
|---|---:|---|
| `brief` | 0.9–1.3 s | presentation and repeated slides |
| `standard` | 1.4–2.2 s | default HTML and Gallery |
| `story` | 2.5–5.0 s | editorial narrative |

Profiles use independent cue delays and durations rather than a uniform playback multiplier. Shape and final visual identity remain unchanged.

## Choreography families

The primitives stay shared, but the data relationship selects the movement family:

- `rail-rise` — C1 establishes the datum, seats columns upward from the rail, then reads the leader.
- `ranked-rail` — C2 reveals ranked labels, loads horizontal rails in order, then reads the top evidence.
- `path-trace` — C3 calibrates the field, draws the series in time order, pins observed points, then reads the peak/latest value.
- `field-aggregation` — C4 seats discrete units into a field before the legend and dominant share settle.
- `band-routing` — C5 fills each composition row from left to right while preserving segment order.
- `ledger-interlock` — C6 alternates contribution docking and balance connectors so the running ledger is causal.
- `milestone-routing` — C7 calibrates time lanes, docks task windows, routes progress, then reads active work.
- `stage-interlock` — C8 alternates connector routing and stage docking so the conversion chain is causal.
- `metric-readout` / `decision-readout` — C9 and C10 establish the decision readout before context.
- `sector-lock` / `metric-pulse` — C11 and C12 seat sectors or panels before settling the dominant metric.
- `pareto-routing` / `cohort-seating` — C13 and C14 assemble ranked contributions or cohort cells in reading order.
- `flow-routing` / `quadrant-lock` — C15 and C16 route weighted links or pin observations before the decisive point.
- `market-build` / `curve-routing` — C17 and C19 construct market observations or maturity points before routing price relationships.
- `drawdown-routing` / `forecast-routing` / `control-lock` — C18, C23, and C24 route risk, uncertainty, or exceptions before the final lock.
- `matrix-seating` / `distribution-build` — C20, C21, and C22 seat cells or bins before settling the decisive statistic.

Select a family from the encoded relationship. Do not add a lock cue merely because an ornament looks attractive; the lock mode and the chart's visual language must justify it.

## Runtime contract

- SVG geometry and final labels are generated before runtime.
- JavaScript only schedules states; it does not compute essential layout.
- Without JavaScript, the final locked state is immediately visible.
- Replay uses one forward-only state machine:

  `settle -> is-resetting (one frame) -> is-playing -> is-complete`

- `is-resetting` clears animated marks immediately; it never plays a reverse animation or exposes a second reveal pass.
- `is-playing` runs the compiled cue timeline. A and B keep carrier groups stable; C animates the evidence bay, terminal, and target lock as a terminal sequence.
- Gallery disables iframe autoplay and stays static until the user requests replay. Replay settles other iframes and reuses the selected iframe without reloading it.
- `prefers-reduced-motion` and `motion=off` show the final state without staged motion.
- Use deterministic delays. Do not use random motion, bounce, elastic easing, or endless loops.
- Animation ends in a readable still frame suitable for SVG/PNG export.

## Primitive behaviour

- `ALIGN`: short line draw or subtle fade, 140–360 ms.
- `DOCK`: 12–22 px translation toward a datum with decisive cubic easing, 420–760 ms.
- `ROUTE`: path draw or sequential activation in the true data direction, 320–900 ms.
- `LOCK`: implicit signal hold, compact endpoint reveal, or explicit focus settle, 180–440 ms when visible.

Only elements with real semantic relationships should route or pulse. Decorative scanning is not a default primitive.
