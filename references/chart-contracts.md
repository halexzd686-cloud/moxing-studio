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

## Selection invariants

- Select by data shape, label fit, and intended reading speed before surface mode.
- Record at least two candidates and why they were rejected.
- Bars and length encodings start at zero. A line chart may use a non-zero range only when the range is explicitly labelled and does not imply magnitude from baseline.
- Area and size encodings must be proportional to area; use square-root scaling for radius.
- Colour is never the only distinction between categories.
- The conclusion title, unit/time context, and source remain visible in the locked frame.

## Modes

Start with `brief` and `editorial`. Both use the same data contract and shape grammar; editorial mode adds reading furniture and evidence plates.

