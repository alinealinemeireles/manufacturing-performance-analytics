# Data Dictionary & Traceability Reference

> **Portfolio expansion note (added 2026-09-23):** `ProductId`/`BottleId`/`CapId` values now also
> include the prefixes `FA-` (food bottles), `FP-` (pharma bottles), `PT-` (cream pots), `TE-`
> (tamper-evident pharma caps) and `TP-` (pot lids), alongside the original `FR-`/`TR-`/`TF-`.
> `ProductType` stays `Bottle`/`Cap` as before (pots are `Bottle`-typed, injection-molded). New
> control-plan `Characteristic` values: `Mouth Diameter`, `Drop Test`, `Stack Load`, `Migration
> Test (Food Contact)` (bottle control plan) and `Tamper Band Separation` (cap control plan) — see
> `docs/simulation_storylines.md` §"Portfolio expansion storylines" for the real ISO/ASTM/FDA/USP
> standards cited against each, and `scripts/generate_expansion_v01.py` for how the new rows were
> generated (additive-only, verified against the pre-expansion files).

Quick-reference companion to the main README. See `lib/etl_lib.py` for the authoritative,
documented implementation of everything below, and Parte 3 of
`manufacturing_performance_analytics.ipynb` for the exact column list and type of every table in
the warehouse (the DDL lives inline in the notebook, not in a separate `.sql` file).

## Porting notes: MySQL → SQL Server

This project's schema follows a consistent set of substitutions from an earlier MySQL design:

| MySQL | SQL Server (T-SQL) |
|---|---|
| `VARCHAR(n)` | `NVARCHAR(n)` (Unicode — inspector/operator names carry accents) |
| `DOUBLE` | `FLOAT` |
| `BOOLEAN` | `BIT` |
| `BIGINT` / `DATE` / `DATETIME` / `TIME` | unchanged, native in T-SQL |
| `CREATE TABLE IF NOT EXISTS ...` | `IF OBJECT_ID('dbo.table', 'U') IS NULL BEGIN CREATE TABLE ... END` |
| `CREATE OR REPLACE VIEW` | `CREATE OR ALTER VIEW` |
| `DATE_SUB(MAX(Date), INTERVAL 52 WEEK)` | `DATEADD(WEEK, -52, MAX([Date]))` |
| `LOAD DATA LOCAL INFILE` (bulk load) | raw `pyodbc` cursor with `fast_executemany=True` and explicit `setinputsizes` (see `lib/db_lib.py`) |

No primary/foreign keys or indexes are defined anywhere — this is a flat,
unconstrained analytics mart populated entirely from the cleaned pandas
DataFrames in the notebook's Parte 2, not an OLTP schema. Grain and
relationships are documented here, not enforced by the database.

**Medallion schemas** (`bronze`/`silver`/`gold`) sit on top of this physical layout — see the
README's architecture section and Parte 3 of the notebook for the full design. Short version:
query `silver.*` (cleaned, fact-grain) or `gold.*` (pre-aggregated marts) going forward; `dbo.*`
is where the physical tables below actually live.

## Calculated columns added during cleaning (notebook Parte 2)

| Column | Tables | Meaning |
|---|---|---|
| `ISOWeek` | most fact tables | ISO week number of `Date` |
| `ISOWeekday` | most fact tables | ISO weekday, 1=Monday...7=Sunday |
| `Month` | sales, complaints, raw material, supplier complaints, NC | `YYYY-MM` string, for easy grouping/sorting |
| `ShiftNumber` | production, downtime, material consumption | Numeric shift: 1 (06-14h), 2 (14-22h), 3 (22-06h) |
| `LotId` | production, downtime, all QC tables, sales, complaints | 16-char batch traceability code — see README |
| `LotIdStart` | material consumption | LotId at the start of that consumption record |
| `MaterialLotSeq` | production, material consumption | Colorant-lot sequence number within a work order — the last 2 digits of `LotId` |
| `LeadTimeProdHours`, `PlannedHours`, `PlannedTimeHours` | production | Duration in decimal hours |
| `Availability`, `Performance`, `Quality`, `OEE` | production | OEE pillars, per work order |
| `ActualCycleTimeSec`, `SetupTimeHours`, `ThroughputLeadTimeHours` | production | Supporting OEE metrics |
| `XBarUCL/LCL`, `RangeRUCL/LCL`, `Cp`, `Cpk`, `Pp`, `Ppk`, `Cpm`, `SigmaLevel` | QC variable-inspection tables | SPC / process-capability metrics |
| `DefectRateP`, `DPU`, `DPMO` | QC attribute-inspection tables | AQL / Six Sigma defect-rate metrics |
| `DowntimeDurationMin`, `UnplannedFailure`, `IsChangeoverSetup`, `IsPreventiveMaintenance` | downtime | Maintenance classification flags |
| `MatchedWorkOrder` | downtime | The work order whose `[start, end)` window contains the stoppage, matched by time overlap — `NULL` for standalone scheduled maintenance between orders |
| `ResolutionDays`, `ResponseDays`, `ClosureDays`, `IsOverdue`, `IsAccepted`, `IsRejected` | QA extension tables (notebook Parte 2) | Day-count and boolean derived columns |

## Process code map (used inside `LotId`)

| Process | Code |
|---|---|
| Blow Molding | 1 |
| Injection Molding | 2 |
| Screen Printing | 4 |
| Hot Foil Stamping | 5 |

(Digit `3` is intentionally unused/reserved, per the original specification.)

## Table grain (one row = ...)

| Table | Grain |
|---|---|
| `fact_production_plan_processed` | one planned work order |
| `fact_production_processed` | one actual work order |
| `fact_downtime_processed` | one machine stoppage event |
| `fact_material_consumption_processed` | one colorant/masterbatch lot consumption record (base resin isn't tracked per work order — see `docs/simulation_storylines.md`, "Modeling simplifications") |
| `fact_*_inspection_variable_cq_processed` | one SPC subgroup sample, per characteristic |
| `fact_*_attribute_inspection_cq_processed` | one AQL attribute inspection, per lot per characteristic |
| `fact_*_disposition_lot_cq_processed` | one final accept/reject decision, per lot |
| `fact_sales_processed` | one finished-goods shipment |
| `fact_customer_complaints_processed` | one customer complaint |
| `fact_raw_material_inspection_processed` | one incoming raw-material lot × characteristic tested |
| `fact_raw_material_lot_disposition_processed` | one incoming raw-material lot (final decision) |
| `fact_supplier_complaints_processed` | one complaint filed to a supplier |
| `fact_nonconformance_processed` | one non-conformance record (Internal or External) |
| `fact_capa_processed` | one corrective/preventive action |
| `fact_process_parameters_processed` | one work order × physical process parameter reading — **Injection Molding and Blow Molding only** (see note below); Screen Printing and Hot Foil Stamping have no process-parameter table at all |
| `ml_predictions_*` | see below |

**Note on `fact_process_parameters_processed` coverage**: it carries `BarrelTemperatureC`,
`InjectionSpeedPct`, `PackingPressureBar` (~44% populated — Injection Molding rows only),
`CoolingTimeSec`, `MoldTemperatureC` (100% populated) and `MoldHumidityPct` (~56% populated). Parte 9.5
of the notebook (BQ-068) only tests `BarrelTemperatureC` and `MoldHumidityPct` against defect rate —
`InjectionSpeedPct` and `PackingPressureBar` are collected but not yet analyzed, and Screen
Printing/Hot Foil Stamping have no equivalent table at all. Framing BQ-068 as "this dataset has zero
process parameters" is inaccurate; the honest framing is "routine tables have none, and this
narrower instrumentation table only covers half the plant."

## One-off engineering study tables (MSA, DOE)

Back the Gage R&R and DOE analysis in Parte 9 of the notebook (BQ-058/059/080 and BQ-067/068).
Unlike every other fact table, these are **not** derived from the routine 18-month work-order
timeline; they're standalone engineering studies (`fact_gage_rr_study_processed`,
`fact_doe_im002_processed`), worth calling out separately because their structure differs from the
rest of the warehouse. `datasets/bronze/*.csv` — including these two tables — is the frozen,
versioned Versão 00 source (see `docs/simulation_storylines.md`).

| Table | Grain | Design |
|---|---|---|
| `fact_gage_rr_study_processed` | one measurement (1 of 10 parts × 3 inspectors × 3 trials = 90 rows) | Crossed Gage R&R (10 parts × 3 inspectors × 3 trials) |
| `fact_doe_im002_processed` | one experimental run (27 rows: 8-corner 2³ factorial × 3 reps + 3 center points) | 2³ full factorial + center points |

`fact_gage_rr_study_processed` is a cap `Weight` Gage R&R: parts `PART-01`..`PART-05` are drawn
from **OP-INJ-003**'s wider process distribution (`operator_variance_mult`, storyline 10),
`PART-06`..`PART-10` from a baseline operator — so a correctly-run study should attribute the
part-to-part spread to *production*, not to which of the 3 inspectors measured it.

`fact_doe_im002_processed` is a 2³ full factorial on **IM-002** (storyline 5 — marginal barrel
heater band): factors `BarrelTemperatureC`, `InjectionSpeedPct`, `CoolingTimeSec` (plus their
`*Coded` -1/0/+1 columns), response `Characteristic='Short Shot'` with `InspectedQty`/
`DefectsFound`/`DefectRateP`. Cooling time is a deliberate near-null factor for Parte 9's
analysis to find via ANOVA, not an assumption.

## Hot Foil Stamping quality data

The "ink" QC tables (`fact_ink_attribute_inspection_cq_processed`,
`fact_ink_disposition_lot_cq_processed`) carry `MachineId` values for both
Screen Printing (`SS-001`/`SS-002`) and Hot Foil (`HF-001`/`HF-002`), with
five Hot-Foil-specific characteristics: `Foil Transfer`, `Foil Adhesion`,
`Edge Definition`, `Coverage`, `Rub Resistance`. See
`docs/simulation_storylines.md` for the full detail.

## Machine Learning tables (notebook Parte 11)

| Table | Grain |
|---|---|
| `ml_predictions_production_forecast` | one row per process, next-week forecast |
| `ml_predictions_production_forecast_history` | one row per process × test-set week (actual vs. predicted) |
| `ml_predictions_downtime_forecast` / `_history` | same pattern, downtime hours |
| `ml_predictions_rejected_forecast` / `_history` | same pattern, rejected units |
| `ml_predictions_scrap_rate` | one row per test-set work order (actual vs. predicted scrap %) |
| `ml_predictions_lot_quality` | one row per test-set lot, with predicted rejection risk |
| `ml_predictions_predictive_maintenance` | one row per machine, today's failure-risk ranking |
| `ml_predictions_predictive_maintenance_history` | one row per machine × test-set day (actual vs. predicted risk) |

Trained models are saved to `models/*.pkl` via `ml_lib.save_model` (a
dict of `{model, metadata}`, where `metadata` includes the feature list,
model name, and test-set metrics) and reloaded with `ml_lib.load_model`.
Every model is chosen via `ml_lib.tune_regression_models` /
`tune_classification_models` — a `GridSearchCV` comparison across three
algorithm families under `TimeSeriesSplit`, never a single fixed-
hyperparameter model. See `lib/ml_lib.py`.

## Statistical process control (notebook Parte 5)

Every SPC/capability routine (X-bar/R limits, Cp/Cpk/Cpm, ANOVA/Tukey, Bartlett's test, Western
Electric run rules, two-sample proportion test) runs in Python, in the same kernel as the rest of
the notebook — see `lib/stats_lib.py` — so the whole project reproduces from a single notebook and
a single kernel, with no R installation required.

## KPI checklist cross-reference

One indicator — **Rework** — is an estimate rather than a directly-
measured figure: this dataset has no rework-transaction field anywhere
upstream, so it would be approximated from each defect characteristic's
`ReactionPlan` (control-plan dimension tables), counting only
`Reprocess (...)` reaction plans as reworkable. Treat it as directional
if computed.

## Quality Assurance domain tables (cleaned in notebook Parte 2, analyzed in Parte 6)

| Table | Grain |
|---|---|
| `fact_sales_processed` | one finished-goods shipment (one row per work order shipped to a customer) |
| `fact_customer_complaints_processed` | one customer complaint |
| `fact_raw_material_inspection_processed` | one incoming raw-material lot × characteristic tested |
| `fact_raw_material_lot_disposition_processed` | one incoming raw-material lot (final decision) |
| `fact_supplier_complaints_processed` | one complaint filed to a supplier |
| `fact_nonconformance_processed` | one non-conformance record (Internal or External) |
| `fact_capa_processed` | one corrective/preventive action |

Complaints-per-million-shipped and supplier approval rate are aggregates,
computed in notebook Parte 6 via `etl_lib.compute_complaints_per_million_shipped`
and `etl_lib.compute_supplier_approval_rate`, not stored as fact columns —
true aggregates live in the analysis layer, not the warehouse.
