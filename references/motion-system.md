# Motion System

## Sequence

Every chart composes four primitives in this order:

1. `ALIGN` — establish datum, scale, and anchors.
2. `DOCK` — assemble data components into the structure.
3. `ROUTE` — reveal relationships along time, dependency, or flow.
4. `LOCK` — attach the conclusion and leave the signal mark in its final position.

Typical total duration is 1.4–1.8 seconds; dense band, ledger, and milestone views may extend to 2.2 seconds. Motion explains structure; it must not delay access to the result.

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

Do not apply a family because its movement looks attractive. Select it from the encoded relationship. Additional charts may reuse a family only when their reading order is genuinely equivalent.

## Runtime contract

- SVG geometry and final labels are generated before runtime.
- JavaScript only schedules states; it does not compute essential layout.
- Without JavaScript, the final locked state is immediately visible.
- First viewport entry plays once. Controls provide replay and pause/resume.
- Honour `prefers-reduced-motion`; show the final state without staged motion.
- Use deterministic delays. Do not use random motion, bounce, elastic easing, or endless loops.
- Animation ends in a readable still frame suitable for SVG/PNG export.

## Primitive behaviour

- `ALIGN`: short line draw or 4–8 px fade/shift; 140–260 ms.
- `DOCK`: 12–32 px translation toward a datum with decisive cubic easing; 420–850 ms.
- `ROUTE`: path draw or sequential activation in the true data direction; 320–700 ms.
- `LOCK`: 4–8% scale settle plus signal reveal; 180–340 ms.

Only elements with real semantic relationships should route or pulse. Decorative scanning is not a default primitive.
