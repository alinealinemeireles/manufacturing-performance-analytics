# Root-cause reference — Versão 00 validation key

`datasets/bronze/` is the **frozen, versioned source of truth** for this project — the Versão 00
dataset of the plant (18 months, 2025-07-01 to 2026-12-30, 4 processes, 18 machines, 3 shifts),
built so that **specific, named root causes leave a consistent signature across every table** —
production, downtime, material consumption, SPC, AQL, lot disposition, sales, complaints,
nonconformance and CAPA — instead of independent per-row randomness. `datasets/bronze/*.csv` is the
one and only source anyone reproducing this project reads from; there is nothing to re-run and no
risk of a re-generated dataset silently drifting from the one this notebook's numbers were computed
against.

This document is the reference key behind the dataset: every root cause deliberately built into
the data, which entity it lives on, the mechanism, and where to look to find it.
`manufacturing_performance_analytics.ipynb` cites these root causes throughout, as each Part's own
analysis independently rediscovers the same signal from the data — this is the mechanism that lets
the project validate its analytical pipeline against a known reference, rather than an unverifiable
claim.

## How to read "where it shows up"

Most stories are **not** flat, permanent shifts — they only show up when you
slice the data the right way (by machine, by time window, by product, by
cycles-since-an-event). That's intentional: it mirrors how a real root cause
actually surfaces in a plant's data, and it's what makes the dataset useful
for practicing an actual investigation instead of eyeballing a single
obviously-broken column.

## Required storylines (from the brief)

| # | Story | Lives on | Mechanism | Where to find it |
|---|---|---|---|---|
| 1 | Wall-thickness variation | **ISBM-003** (Blow Molding) | Parison-programming instability: wider spread and a thin-shoulder bias on the `Thickness` characteristic | `fact_bottle_inspection_variables_cq_raw`, filter `MachineId=ISBM-003, Characteristic=Thickness` — `RangeR` is ~2.6x other blow-molding machines. Also shows as one of the 8 full-lot-redo episodes. |
| 2 | Flash climbing with cycles | **IM-004** (Injection) | IM-004 is deliberately run in much longer campaigns between mold changeovers than other machines (up to 16 orders vs. 1-3 elsewhere); a hidden `setup_cycles` counter (units produced since the last `Mold Change / Setup` event) raises Flash defect probability as it climbs, and resets to zero at every changeover | `fact_cap_attribute_inspection_cq_raw`, `Characteristic=Flash, MachineId=IM-004` — defect counts trend up between `Mold Change / Setup` events in `fact_downtime_raw` for IM-004, then drop. Not visible as a monthly trend (changeovers are event-driven, not calendar-driven) — plot against production sequence/cumulative units since the last changeover instead. |
| 3 | Adhesion failure spike, one PP lot | **SS-002**, product **FR-007-PP-350**, **2026-02-20 to 2026-03-13** | A marginal PP resin window from the problem supplier (see #11) drives a targeted Adhesion defect spike, only for that bottle on that machine in that window | `fact_ink_attribute_inspection_cq_raw`, filter `BottleId=FR-007-PP-350, Characteristic=Adhesion` and compare inside vs. outside the window (~8-9x more defects inside). Matches an off-spec PP lot in `fact_raw_material_inspection_raw`/`fact_raw_material_lot_disposition_raw` around 2026-02. One of the 8 redo episodes. |
| 4 | Incomplete foil transfer at high speed | **HF-001** (Hot Foil) | A hidden per-order "line speed index" (not stored as a column — same as a real plant with no logged speed parameter) drives both throughput and, only on HF-001, `Foil Transfer` defect probability | `fact_ink_attribute_inspection_cq_raw`, `Characteristic=Foil Transfer, MachineId=HF-001` correlates with shorter `ActualCycleTimeSec` once the notebook's Parte 2 computes it from `ProducedQty`/run hours. HF-001's overall reject rate (~3.6%) is visibly higher than HF-002 (~3.0%). |
| 5 | Quality problem, stable uptime | **IM-002** (Injection) | A marginal barrel heater band: elevated Short Shot AQL rejects and wider Weight variable spread (proxy for sink marks — the control plan has no discrete "Sink Mark" characteristic, see Modeling notes below); Availability is untouched | `fact_production_raw` reject rate for IM-002 (~3.2%, highest of all Injection machines) vs. normal Availability in the OEE calc; `fact_cap_attribute_inspection_cq_raw` `Characteristic=Short Shot`. |
| 6 | Operational (uptime) problem, fine quality | **ISBM-005** (Blow Molding) | Aging hydraulics: 2.3x the baseline unplanned-stoppage frequency (`Raw Material Shortage`, `Operator Unavailable`, mechanical/electrical); reject rate stays at the plant baseline | `fact_downtime_raw` unplanned-event count/hours for ISBM-005 vs. other ISBM machines; `fact_production_raw` reject rate for ISBM-005 is at the fleet baseline (~2.1%), not elevated. |
| 7 | Maintenance/reliability decline | **SS-001** (Screen Printing) | Roller/squeegee wear + a maintenance backlog: both breakdown frequency and MTTR climb steadily from 2025-07 to 2026-07, then an overhaul (also one of the 8 redo/CAPA episodes) resets both to below-baseline | `fact_downtime_raw`, unplanned stoppages on SS-001: mean duration rises from ~1.5h (mid-2025) to ~2.4h (early/mid-2026), then drops to ~0.8h from 2026-07 onward. A matching CAPA (`EffectivenessCheck=Effective`) closes right around the overhaul date. |
| 8 | Shift 2 defect premium | **Shift 2** (14:00-22:00), all processes | Fatigue/handover multiplier (~1.35x) applied to every process's defect probability | `fact_production_raw` reject rate by shift: Shift 2 ≈2.9%, Shift 1 ≈2.2%, Shift 3 ≈2.4% (derive `ShiftNumber` from `StartTime` per `etl_lib.compute_shift_number`). |
| 9 | Full-lot reject-and-redo | 8 episodes across all 4 processes (ISBM-003 thickness, contamination on ISBM-008, mold wear on ISBM-001/M-SOP-007, IM-004 flash, IM-004/SUP-005 PP lot, SS-002 adhesion, HF-001 speed, SS-001 wear) | Each episode's batch is rejected at final disposition, then the **entire planned quantity is re-issued as a brand-new work order** on the same machine/mold/product 6-30h later, run under corrective conditions (defect probability cut to ~18% of the original) | `fact_nonconformance_raw` has one row per episode (`Source=Lot Rejection`, `RelatedRecordId`=the original lot). Find the matching redo `WorkOrder`/`ProductBatch` in `fact_production_raw` starting shortly after the original lot's `LotDecisionDateTime` in the matching disposition table, same `MachineId`/`ToolId`/`ProductId`. |
| 10 | Operator variability, not bias | **OP-INJ-003** (Injection) | 2x the measurement spread (not a mean shift) on every characteristic they run | **Look at `RangeR`, not `XBar`.** `fact_cap_inspection_variable_cq_raw`, `Characteristic=Weight`, mean `RangeR` for OP-INJ-003 ≈5.0 vs. ≈2.5 for peers, while `XBar` and average AQL outcomes are indistinguishable. This is a deliberate X-bar-vs-R-chart teaching point: a mean-only view (X-bar) completely misses this operator. |
| 11 | Disproportionate supplier | **SUP-005** (Spot Purchase contract, no long-term relationship) | 16% off-spec probability on incoming lots vs. 4% baseline; feeds PP/PVC (and occasionally wins the material draw for any process using those resins) | `fact_raw_material_lot_disposition_raw`, `FinalDecision != Accepted` rate by `SupplierId`: SUP-005 ≈24% vs. 4-10% for everyone else. Matching elevated `fact_supplier_complaints_raw` volume. Feeds storyline #3 and #5's redo episode. |
| 12 | Gradual mold wear | **M-SOP-007** (Blow Molding mold, machine ISBM-001) | Defect probability on `Flash`/`Leakage` climbs with cumulative units produced on that physical mold since its last refurbishment; refurbished **2026-06-15** (tied to one of the 8 redo/CAPA episodes), then climbs again more slowly | `fact_bottle_attribute_inspection_cq_raw`, `MoldId=M-SOP-007, Characteristic in (Flash, Leakage)` by month: peaks around 2026-02/03 (~2.0 mean defects), drops sharply after the 2026-06 refurbishment (~0.5), then creeps back up toward year-end. |
| 13 | Hidden parameter → rejection probability | Line-speed index (see #4), plus faster Injection cycles → more sink-mark-proxy defects | Never stored as a column — same as a real plant with no per-order speed log | Only discoverable by computing `ActualCycleTimeSec` (notebook Parte 2) and correlating it against reject rate / specific defect characteristics. |
| 14 | Complaints only partially explained by internal defects | All customer complaints | ~half of complaints are generated from a shipped lot with elevated internal defect probability (a "quality escape" — passed AQL sampling but was a marginal lot); the other half are logistics/independent (`Late Delivery`, `Short Shipment`, `Wrong Product Shipped`, unrelated) with no internal quality signal at all | `fact_customer_complaints_raw` — cross-reference `WorkOrder`/`LotId` against the matching disposition/production reject rate; roughly half will show no elevated internal signal, matching the project's existing "correlation ≈ 0, not significant" finding for the honest half. |

## Bonus storylines (added for extra realism, not explicitly requested)

| Story | Where | Mechanism |
|---|---|---|
| Seasonal demand peak | Sep-Nov 2025 and Sep-Nov 2026, all processes | A ~15% line-speed bump during these windows (Brazilian cosmetics/personal-care restocking season) raises throughput and speed-sensitive defects together — visible as a small seasonal bump in reject rate that recurs both years. |
| HDPE-PCR supplier transition | **2026-05-01 to 2026-06-15**, material HDPE-PCR | Primary supplier shifts from SUP-001 to SUP-004 (sustainability-driven resourcing); SUP-004 runs at 22% off-spec during the transition window before settling to baseline — a classic "new supplier growing pains" pattern in `fact_raw_material_lot_disposition_raw`. |
| One-week contamination event | **2026-02-02 to 2026-02-09**, Blow Molding, tied to one masterbatch/`ColorId` | A `Black Specks` defect spike (~1.5x baseline) cascades into one of the 8 redo episodes (machine ISBM-008) plus a small nonconformance/CAPA cluster. |
| New-product-launch learning curve | **FR-011-PET-400**, **FR-012-PET-400**, launched 2026-04-06 | Elevated defect probability at launch (+80%) that decays back to baseline over roughly the first 6 weeks — a textbook Lean "learning curve" for a new SKU. |

## Two data-model notes

1. **Hot Foil Stamping quality-inspection data.** The two "ink" QC tables
   (`fact_ink_attribute_inspection_cq_raw`, `fact_ink_disposition_lot_cq_raw`)
   carry `HF-001`/`HF-002` rows alongside Screen Printing, with five
   Hot-Foil-specific characteristics: `Foil Transfer`, `Foil Adhesion`,
   `Edge Definition`, `Coverage`, `Rub Resistance` — covering the
   incomplete-transfer / low-adhesion / blurred-edge / irregular-coverage /
   rub-resistance defect modes for that process. No schema changes needed to
   the existing two tables.
2. **`dim_machine_setup.csv`** carries a rated-capacity row per
   `(MachineId, ToolId)` combination for every process, including Screen
   Printing and Hot Foil, so OEE's Performance component is measurable
   across all four processes.
3. **`ProductBatch` uses one consistent `LOTE-{mold}-{n}` scheme** across
   `fact_production_raw` and the QC tables for the same lot, so a lot can be
   traced end-to-end from production through QC through disposition — the
   traceability story `LotId` is supposed to tell.

## Modeling simplifications, stated honestly

- **Grain stays at work-order / AQL-lot / SPC-subgroup level, not one row
  per physical unit.** "Millions of units" is satisfied through summed
  `ProducedQty` (tens of millions/year) — literal per-unit rows would
  produce multi-gigabyte files for no analytical benefit.
- **Injection defects that don't map to an existing control-plan
  characteristic** (sink marks, warpage, weld lines, burn marks) are
  modeled as proxies through the characteristics that already exist in
  `dim_cap_control_plan_cq.csv` rather than inventing new ones: sink marks
  → `Short Shot` AQL defects + wider `Weight` variable spread; warpage →
  `Height`/`Diameter` variable drift; weld lines/burn marks → `Stain`/`Color`
  attribute defects. This is a deliberate, documented approximation, in the
  same spirit as the project's existing "rework is an estimate" caveat.
- **Base resin consumption is not tracked per work order** — only
  masterbatch/colorant lots are (`fact_material_consumption_raw`). Incoming
  resin quality lives entirely in `fact_raw_material_inspection_raw`/
  `_lot_disposition_raw`, correlated to downstream defects by material + time
  window, not by a literal shared lot-id join (the schema has no such
  column, on either the raw-material or the production side).
- **AQL Ac/Re numbers use a small simplified table** (three AQL levels ×
  two sample-size code letters), not the full ISO 2859-1 table.
- Deliberate "dirty data" — mixed-case category text, disguised blanks
  (`-`, `n/a`, empty), stray whitespace, a few negative quantities, blank
  `MaterialLot` values, and a small rate of duplicate rows — is present in
  `datasets/bronze/`, because the notebook's Partes 1-2 are written to find
  and clean exactly this. It is intentional material for the cleaning stage
  to work through, not noise to remove.

## Reproducing the project from the frozen data

`datasets/bronze/*.csv` is frozen and versioned as this project's source of truth (see the note at
the top of this document) — there is nothing to re-run and none is needed. To reproduce every
downstream artifact, run `manufacturing_performance_analytics.ipynb` from the top: it reads
`datasets/bronze/` and `datasets/dim/` as-is and (re)builds `datasets/silver/`, the SQL Server
warehouse, the trained models in `models/`, and the charts in `reports/`.
