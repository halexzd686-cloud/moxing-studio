# Chart Contracts

Internal IDs remain stable. Public names describe the visual role rather than the legacy silhouette.

| ID | Public name | Data shape | Assembly family |
|---|---|---|---|
| C1 | Structural Rank | one series, up to 10 short categories | rail assembly |
| C2 | Ranked Rail | ranking or long category labels | rail assembly |
| C3 | Signal Trend | time series, up to 4 series | path routing |
| C4 | Composition Field | positive parts of a whole, up to 6 groups | field aggregation |
| C5 | Composition Bands | composition across category/time, up to 4 layers | field aggregation |
| C6 | Ledger Steps | start, contributions, end | stage interlock |
| C7 | Milestone Lanes | dated tasks, up to 10 rows | stage interlock |
| C8 | Stage Channel | 3–6 conversion stages | stage interlock |
| C9 | Metric Lockup | one KPI with context | decision interface |
| C10 | Decision Interface | 2–4 KPIs with deltas | decision interface |
| C11 | Sector Lock | positive parts of a whole, up to 6 sectors; list or `{items, variant: donut|pie}` | radial composition |
| C12 | Metric Small Multiples | aligned labels with up to 4 metric series | time-series routing |
| C13 | Pareto Contribution | positive ranked contributions, up to 10 items | rail + cumulative routing |
| C14 | Cohort Matrix | labelled cohorts with triangular percentage rows | matrix seating |
| C15 | Commerce Flow | levelled nodes and weighted directed links | flow routing |
| C16 | Decision Bubble Matrix | x, y, non-negative size, up to 12 observations | decision field |
| C17 | Market Candles | dated OHLC and volume, up to 20 periods | market assembly |
| C18 | Performance Drawdown | positive indexed performance series | time-series + underwater routing |
| C19 | Yield Curve | ordered maturities with up to 3 rate curves | curve routing |
| C20 | Sensitivity Matrix | rectangular two-variable result grid, up to 8×8 | matrix seating |
| C21 | Distribution Profile | at least 2 numeric observations | distribution assembly |
| C22 | Correlation Matrix | square labelled matrix in −1…1, up to 8×8 | matrix seating |
| C23 | Forecast Fan | actuals plus overlapping forecast/lower/upper series | forecast routing |
| C24 | Control Chart | observations with centre, UCL and LCL | control routing |

## Domains and presets

- Foundation: C1–C10. These remain the first choice for ordinary comparison, trend, composition, bridge, schedule, stage and KPI questions.
- Commerce: C11–C16. C11–C16 are generic contracts with commerce defaults; do not hard-code ecommerce terminology into user data handling.
- Finance: C17–C20. Reuse C6 for profit/cash bridges and C16 for risk-return bubbles instead of adding duplicate finance-only silhouettes.
- Analysis: C21–C24. Use these only when distribution, dependence, uncertainty or process stability is the actual analytical question.

## Shared renderer families

The 24 public contracts intentionally map to nine maintainable geometry families: rail, time-series, matrix, composition, stage/flow, decision/point, radial, market/curve, and distribution. A new public contract must answer a distinct decision question; a visual-only variant belongs in a preset, not a new ID.

## Selection invariants

- Select by data shape, label fit, and intended reading speed before surface mode.
- Record at least two candidates and why they were rejected.
- Bars and length encodings start at zero. A line chart may use a non-zero range only when the range is explicitly labelled and does not imply magnitude from baseline.
- Area and size encodings must be proportional to area; use square-root scaling for radius.
- Colour is never the only distinction between categories.
- The conclusion title, unit/time context, and source remain visible in the locked frame.
- Prefer an existing family and data schema. Add a new ID only when industry usage is established and the decision question cannot be expressed honestly by an existing contract.

## Density and presentation

Start with `brief` and `editorial`. Both use the same data contract and shape grammar; editorial mode adds reading furniture and evidence plates.

Density does not select the evidence layout. Choose A / B / C presentation independently using [presentation-modes.md](presentation-modes.md); do not infer a side bay merely because `editorial` is active.
