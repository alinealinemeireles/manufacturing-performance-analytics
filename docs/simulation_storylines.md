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
| Seasonal demand peak | Sep-Nov 2025 and Sep-Nov 2026, all processes | A ~15% line-speed bump during these windows (Iberian/European cosmetics and personal-care pre-Christmas restocking season) raises throughput and speed-sensitive defects together — visible as a small seasonal bump in reject rate that recurs both years. |
| HDPE-PCR supplier transition | **2026-05-01 to 2026-06-15**, material HDPE-PCR | Primary supplier shifts from SUP-001 to SUP-004 (sustainability-driven resourcing); SUP-004 runs at 22% off-spec during the transition window before settling to baseline — a classic "new supplier growing pains" pattern in `fact_raw_material_lot_disposition_raw`. |
| One-week contamination event | **2026-02-02 to 2026-02-09**, Blow Molding, tied to one masterbatch/`ColorId` | A `Black Specks` defect spike (~1.5x baseline) cascades into one of the 8 redo episodes (machine ISBM-008) plus a small nonconformance/CAPA cluster. |
| New-product-launch learning curve | **FR-011-PET-400**, **FR-012-PET-400**, launched 2026-04-06 | Elevated defect probability at launch (+80%) that decays back to baseline over roughly the first 6 weeks — a textbook Lean "learning curve" for a new SKU. |

## Portfolio expansion storylines (additive — added 2026-09-23)

**Scope note (read this first):** everything above this section describes the original, frozen
Versão 00 dataset (18 months, 4 processes, 18 machines, cosmetics-only portfolio) exactly as it
was validated and audited — none of it changed. (This portfolio expansion is unrelated to, and
does not renumber, the "Versão 01" of `README.md` §13 / `docs/technical_audit_and_methodology.md`,
which refers to the post-fix multidisciplinary audit of the notebook itself.) This section
documents a strictly **additive** expansion: 4 brand-new machines (`ISBM-009`, `ISBM-010`, `IM-007`, `IM-008`), ~15 new product SKUs
(food/pharma bottles, cream pots, a tamper-evident cap, a pot lid — prefixes `FA-`, `FP-`, `PT-`,
`TE-`, `TP-`), 2 new suppliers (`SUP-009`, `SUP-010`), 4 new customers (`CUST-015`-`CUST-018`,
segments `Food Packaging`/`Pharmaceutical`), and ~6 new employees, all commissioned on
**2026-07-06** and running through the end of the frozen window (**2026-12-30**, ~25 weeks). Every
row in every table added here is a *new* row, appended to the same 22 `datasets/bronze/*.csv`
files (proven byte-identical for all pre-existing rows by
`scripts/generate_expansion_v01.py`'s own additivity check) — no existing machine, product,
supplier, operator, or storyline above is touched, and every finding already published in
`docs/post_fix_independent_audit.md` / `docs/client_root_cause_action_plan.md` /
`docs/technical_audit_and_methodology.md` remains exactly as valid as when it was written.

Generation method: each new machine clones a real analogous work order / QC lot / downtime event
from a clean, non-storyline **donor machine** in the *same* trailing date window (e.g. `ISBM-009`
clones from `ISBM-006`), remaps identifiers, and then biases probabilities for the specific
entity+window each story below lives on — the same "specific, named root cause with a consistent
signature across tables" philosophy as the original 18 storylines, not independent per-row
randomness.

| # | Story | Lives on | Mechanism | Where to find it | Deliberate contrast with an existing storyline |
|---|---|---|---|---|---|
| A | New-line learning curve | `ISBM-009`, product `FA-030-HDPE-FG-1000`/`FA-030-PP-FG-1000`, **2026-07-06 to 2026-08-24** (7 weeks) | Attribute-defect probability starts ~70% above the (stable, full-history) baseline rate for that characteristic and decays linearly back to baseline over 7 weeks | `fact_bottle_attribute_inspection_cq_raw`, filter `MachineId=ISBM-009, BottleId` starts with `FA-030` — defect rate ≈0.85% in the launch window vs ≈0.60% after (≈+41%, matches the decaying-average multiplier) | Same family as the Versão 00 bonus "new-product learning curve" (`FR-011`/`FR-012`), but this time it is a new *machine* and a new *product* launching together — a compounding case |
| B | Infant mortality (new-equipment downtime) | `IM-007`, commissioned 2026-07-06, elevated window **2026-07-06 to 2026-08-31** (8 weeks) | Extra unplanned stoppages on top of the cloned baseline, tagged with electrical/commissioning-specific reasons (`Electrical Fault - Commissioning`, `Controller Calibration`, `PLC/HMI Fault`, `Sensor Wiring Fault`), scaled to ~2x the machine's own baseline weekly rate at week 0 and decaying to zero by week 8 | `fact_downtime_raw`, `MachineId=IM-007`, `PlannedStoppage=No` — weekly count runs ≈190-200/week in weeks 0-3, falling to the ≈65-95/week baseline by week 8 | Direct bathtub-curve contrast to `ISBM-005` (Versão 00 story #6, aging hydraulics / wear-out tail): same shape of finding (uptime problem, not quality), opposite cause (infant mortality vs. wear-out) |
| C | New pharma-grade resin supplier, early quality escape | `SUP-009` (new, `Spot Purchase`, 1 year as supplier — same risk profile that already makes `SUP-005` risky) feeding `ISBM-010`/`FP-032-*` products, window **2026-08-01 to 2026-09-15** | Incoming-lot reject rate ~20-25% during the window vs. a single-digit baseline outside it; the off-spec resin also widens `Weight`/`Thickness` variable spread on `FP-032` bottles produced on `ISBM-010` in that window | `fact_raw_material_lot_disposition_raw`, `SupplierId=SUP-009` — reject rate ≈25% in-window vs ≈6% outside it. `fact_bottle_inspection_variables_cq_raw`, `MachineId=ISBM-010, BottleId` starts with `FP-032`, `Characteristic` in `{Weight,Thickness}` — `RangeR` wider in-window | Same "growing pains" shape as the Versão 00 bonus HDPE-PCR/`SUP-004` transition, but for a pharma-grade material; `SUP-010` (also new, `Annual Contract`, food-grade) stays clean the entire window — not everything new comes with a defect |
| D | Operator training-curve bias, new line | `OP-SOP-006` (new operator) on `ISBM-010`, window **2026-08-01 to 2026-09-05** (5 weeks post-commissioning) | A mean-shift bias (~1.5σ-equivalent, no extra spread) on `Weight`/`Thickness` measurements only for this operator's lots in the window, fading afterward | `fact_bottle_inspection_variables_cq_raw` joined to `fact_production_raw.OperatorId` — normalized deviation `(XBar-Nominal)/(USL-LSL)` ≈+0.24 for `OP-SOP-006` in-window vs ≈0.00 for `OP-SOP-004` in-window and ≈0.00 for both operators outside the window | Direct teaching contrast to `OP-INJ-003` (Versão 00 story #10: variance without bias, permanent): this one is bias without excess variance, and it fades with experience instead of persisting |
| E | Tamper-evidence mold wear, pharma caps | Mold `M-INJ-012` (product `TE-012-PP-PG-24410`) on `IM-008`, from commissioning **2026-07-06** through the end of the frozen window, **not yet refurbished** | `Tamper Band Separation` defect probability climbs roughly linearly from ~2% at launch to ~5% by 2026-12-30 as cumulative units run on the new mold | `fact_cap_attribute_inspection_cq_raw`, `MachineId=IM-008, Characteristic=Tamper Band Separation` — monthly rate ≈2.7% (Jul) rising to ≈5.3% (Dec); matching `fact_nonconformance_raw`/`fact_capa_raw` rows dated 2026-11-18/19 (`RelatedRecordId=M-INJ-012`, `CAPAType=Corrective`, still `Open` at period end) | Contrast to `M-SOP-007` (Versão 00 story #12, already refurbished 2026-06-15): this one is left **open/unresolved** within the frozen window, an ongoing finding rather than a resolved one |

Two rows of narrative evidence were also added by hand (not proportionally cloned, since these are
rare events): a customer complaint (`CC-...`) from `CUST-017` about `FP-032-PP-PG-100` weight
during Storyline C's window, and one from `CUST-018` about `TE-012-PP-PG-24410` tamper-band
separation tied to Storyline E; a matching `SC-...` supplier complaint against `SUP-009`; and the
`NC-...`/`CAPA-...` pair referenced in Storyline E above.

No new full-lot reject-and-redo episode was created — the original "8 of 8 episodes" reference in
the notebook's Parte 9 stays accurate as written.

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
