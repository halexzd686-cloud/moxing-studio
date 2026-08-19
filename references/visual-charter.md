# Moxing v2 Visual Charter

## Design thesis

Moxing is a structural data-communication system for Chinese presentations and editorial storytelling. A chart should feel assembled rather than decorated: information components align to a datum, dock into place, connect, and lock on the conclusion.

The internal metaphor is precise joinery. Public-facing language uses **Structural Interface / 结构接口**.

## Personality

- Architectural order leads; contemporary East-Asian restraint appears through proportion, whitespace, and typography rather than traditional ornament.
- The interface may recall precision hardware, but must not copy Nothing typography, icons, Glyph patterns, or product assets.
- The style must remain recognisable in grayscale. Colour supports meaning; it is not the identity.

## Four signatures

1. **Datum spine** — every chart has a visible or implied load-bearing rail.
2. **Joinery interface** — small seams, cut corners, sockets, or location marks show how data attaches to the structure.
3. **Evidence plate** — annotations use a numbered, ordered plate: index, state, value, explanation.
4. **Lock mark** — the single oxide signal identifies the conclusion, target, turning point, or risk.

## Composition

- Use an asymmetric 16:9 composition by default. Reserve 24–36% of the canvas for the conclusion or evidence column when the chart benefits from it.
- Use a 16 px base grid, with 8 px for local detail and 32/48/64 px for major spacing.
- Prefer open frames, square ends, 45-degree cuts, and fine seams. Do not use rounded cards as a universal container.
- Primary data may be solid. Structure is line-based. Secondary data is outline, hollow, or quiet fill.
- Engineering detail is medium strength: apparent at first glance but never louder than the data.

## Typography

- Chinese conclusion titles: Noto Serif SC, bold, used sparingly.
- Labels, notes, and axes: Noto Sans SC.
- Latin indices, timecodes, percentages, and state codes: Doto.
- Dot-matrix text never carries long Chinese labels or body copy.
- Dot-matrix text uses its own strong/quiet contrast tokens, 12 px minimum, and 560–700 weight; signal states use the oxide colour and the strongest weight.
- Minimum presentation sizes: title 30 px, body/axis 14 px, data label 16 px, source 12 px.

## Colour

- Default surface: cool engineering white.
- Companion surface: charcoal instrument panel.
- Brand signal: oxide orange-red; one locked conclusion per chart.
- Multi-series charts may use up to four low-saturation functional colours. Preserve a second channel such as fill/outline/dash.
- Avoid decorative gradients, glassmorphism, neon glow, and drop shadows. Controlled opacity is allowed for ranges, forecasts, and structural depth.

## Density modes

- `brief`: presentation-first; only the argument and essential evidence.
- `editorial`: adds ticks, indices, annotations, and reading guidance.
- `instrument` is reserved for a later release; do not simulate it by adding noise.

## Acceptance

- Three-second test: the conclusion is visible from two metres away.
- Fifteen-second test: at least one supporting relationship is discoverable.
- Silhouette test: the chart is identifiable as Moxing when blurred or desaturated.
- De-theme test: the visual identity survives a palette swap.
- Motion-off test: disabling JavaScript or reduced-motion still yields a complete chart.
- Data-honesty test: geometry remains proportional and labels retain units, time range, and source.
