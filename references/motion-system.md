# Motion System

## Sequence

Every chart composes four primitives in this order:

1. `ALIGN` — establish datum, scale, and anchors.
2. `DOCK` — assemble data components into the structure.
3. `ROUTE` — reveal relationships along time, dependency, or flow.
4. `LOCK` — attach the conclusion and leave the signal mark in its final position.

Typical total duration is 1.4–1.8 seconds. Motion explains structure; it must not delay access to the result.

## Profiles

| Profile | Total | Use |
|---|---:|---|
| `brief` | 0.9–1.2 s | presentation, repeated slides |
| `standard` | 1.4–1.8 s | default HTML and gallery |
| `story` | 2.5–5 s | editorial narrative |

Profiles alter timing and pauses, not shape or visual identity.

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

