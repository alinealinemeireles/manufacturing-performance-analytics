"""
fix_audit_2026_09_30.py

Data fixes from the 2026-09-30 multidisciplinary audit (docs/audit_2026-09-30.md). Every fix
below was found by checking the committed bronze data against a rule the rest of the project
already claims to follow; each one is restricted to the rows that break that rule, and the
script is idempotent (a second run changes nothing).

1. **Rejected batches shipped / shipped before the batch decision** (expansion rows only).
   QC releases or rejects a PRODUCT BATCH (`ProductBatch`; `PrintLot` for decoration), and a
   batch spans 1-16 work orders -- but its disposition row names only the batch's last
   WorkOrder. `fix_expansion_sales_release.py` enforced release at WorkOrder level, so sales of
   the batch's OTHER work orders kept going out: 31 expansion rows from Rejected
   (scrapped/segregated) batches (Versão 00: 0) and 11 expansion rows shipped before their batch
   was decided. Fix: drop the rows of Rejected batches; re-date the early expansion rows to the
   day after the batch decision (dropping any that would then fall after the dataset window, the
   rule `fix_expansion_sales_release.py` already used). Versão 00 ships 173 rows 1-6 days before
   the batch decision -- frozen reference data, kept and reported as a documented warning.

2. **Attribute lot decision contradicting Ac/Re** (expansion rows only). ISO 2859-1 rejects when
   defects >= Re (= Ac + 1); the expansion generator tested `defects > Re`, so 47 samples with
   exactly Re defects were "Approved". Fix: LotDecision = Rejected for those rows (root cause
   also fixed in generate_expansion_v01.py).

3. **Material "consumed" upward** (expansion rows only). backfill_food_cap_and_material_consumption.py
   jittered StartWeightKg and EndWeightKg INDEPENDENTLY by +/-10%, on bags of 40-250 kg, so the
   4 kg a run consumes drowned in noise: 338 records end heavier than they started (up to
   +35.8 kg), and the weight chain inside a lot (next start = previous end: 87% in Versão 00)
   was broken (0.4%). Fix: rebuild each expansion lot as a chain -- first start kept (raised if
   the bag could not hold the lot's runs), 4.00 kg per run (the Versão 00 mode, 86% of its
   records), next start = previous end.

4. **LotId year one year off at the ISO year boundary** (Versão 00 and expansion). The LotId is
   YY + ISO week, but YY was the CALENDAR year: 2025-12-29..31 (ISO week 1 of 2026) were coded
   "2501...", i.e. the first week of 2025. The generator and `etl_lib.build_lotid_prefix`
   shared the bug, so sales and production agreed with each other and the contract never saw
   it. Fix: YY = ISO year in `build_lotid_prefix` and in the shipped LotIds (sales, complaints).

5. **dim_supplier** -- SUP-001 delivered HDPE-PCR lots (the documented 2026-05 transition from
   SUP-001 to SUP-004, docs/simulation_storylines.md), but its `MaterialsSupplied` omitted it.

Decisions D2 and D3 (implemented on request after the audit, same script so one run reproduces
the whole corrected dataset):

6. **D2 -- food-contact caps get their own injection line, IM-009.** The food-cap backfill put a
   third mold (M-INJ-014, TA-014 caps, 263 orders) on IM-008 "additively", on top of the two
   molds IM-008 already ran full time: IM-008 ended up with 188% of its calendar hours booked,
   which no machine can do. Those orders (and their plan, process parameters, QC and material
   rows -- they have no sales or downtime rows) move to a new, dedicated IM-009, installed in
   2026 with automated defect detection like the other new lines -- food-contact segregation is
   also what a food-safety scheme would ask for. dim_machine_profile / dim_machine_setup follow.

7. **D3 -- attribute sampling plans per ISO 2859-1** (all attribute inspections). The data used
   the Ac/Re of the NEXT code letter (L / AQL 0.65 -> Ac 5, the standard says 3; M / 1.5 -> 14 vs
   10), i.e. plans one step more lenient than the standard they cite. Fix: Ac/Re from Table II-A
   for the code letter actually sampled (the physical sample cannot be re-drawn), LotDecision
   re-derived (reject at d >= Re), and `InspectionLevel` set to the general level (Table I) the
   lot size / code letter pair really corresponds to -- "Não normativo" where none does. The
   Storyline F tightening (n x 1.5 = 300 / 472, not sizes the standard has) becomes what the
   standard prescribes for more discrimination: inspection level III (M/315, N/500).

Run: python scripts/fix_audit_2026_09_30.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import aql  # noqa: E402

BRONZE = ROOT / "datasets" / "bronze"
DIM = ROOT / "datasets" / "dim"
NEW_MACHINES = {"IM-007", "IM-008", "IM-009", "ISBM-009", "ISBM-010"}
FOOD_CAP_MOLD, FOOD_CAP_FROM, FOOD_CAP_TO = "M-INJ-014", "IM-008", "IM-009"
ATTRIBUTE_TABLES = ("fact_bottle_attribute_inspection_cq_raw", "fact_cap_attribute_inspection_cq_raw",
                    "fact_ink_attribute_inspection_cq_raw")
WINDOW_END = pd.Timestamp("2026-12-30")
RUN_CONSUMPTION_KG = 4.00  # Versão 00 mode: 13,259 of 15,452 records consume exactly 4.00 kg


def read(folder: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(folder / f"{name}.csv", encoding="utf-8-sig", dtype={"LotId": str}, keep_default_na=False,
                       na_values=[""])


def write(df: pd.DataFrame, folder: Path, name: str) -> None:
    df.to_csv(folder / f"{name}.csv", index=False, encoding="utf-8-sig")


def _order_key(ids: pd.Series) -> pd.Series:
    return ids.str.extract(r"(\d+)")[0].astype(int)


# ---------------------------------------------------------------------------
# 1. Batch-level product release
# ---------------------------------------------------------------------------
def fix_batch_release(production: pd.DataFrame) -> None:
    sales = read(BRONZE, "fact_sales_raw")
    complaints = read(BRONZE, "fact_customer_complaints_raw")
    parts = []
    for name, key in [("fact_bottle_disposition_lot_cq_raw", "ProductBatch"),
                      ("fact_cap_disposition_lot_cq_raw", "ProductBatch"),
                      ("fact_ink_disposition_lot_cq_raw", "PrintLot")]:
        d = read(BRONZE, name)
        parts.append(pd.DataFrame({"Batch": d[key].str.strip(), "Decision": d["FinalLotDecision"].str.strip().str.title(),
                                   "DecidedAt": pd.to_datetime(d["LotDecisionDateTime"], format="mixed", errors="coerce")}))
    dispositions = pd.concat(parts, ignore_index=True)
    rejected = set(dispositions.loc[dispositions["Decision"] == "Rejected", "Batch"])
    decision_day = dispositions.groupby("Batch")["DecidedAt"].max().dt.normalize()

    batch = sales["WorkOrder"].map(production.set_index("WorkOrder")["ProductBatch"].str.strip())
    is_expansion = sales["MachineId"].isin(NEW_MACHINES)
    from_rejected = batch.isin(rejected)
    ship_date = pd.to_datetime(sales["Date"])
    decided = batch.map(decision_day)
    early_any = decided.notna() & (ship_date < decided)
    assert not (~is_expansion & from_rejected).any(), "a Versão 00 sales row ships a Rejected batch"
    # Versão 00 itself ships 173 rows 1-6 days before their BATCH decision (its generator tied
    # release to the work order named on the disposition). Frozen reference data: kept, and
    # reported by the contract as a documented warning (BR-SHIP-AFTER-BATCH-DECISION).
    early = early_any & is_expansion

    new_date = ship_date.where(~early, decided + pd.Timedelta(days=1))
    outside = new_date > WINDOW_END
    drop = from_rejected | (early & outside)
    dropped_ids = set(sales.loc[drop, "SalesOrderId"])
    linked = complaints["SalesOrderId"].isin(dropped_ids)
    assert not linked.any(), f"{linked.sum()} complaints point at sales rows this fix would drop"

    redated = early & ~drop
    sales.loc[redated, "Date"] = new_date[redated].dt.strftime("%Y-%m-%d")
    sales = sales.loc[~drop]
    late = complaints.merge(sales[["SalesOrderId", "Date"]], on="SalesOrderId", suffixes=("", "_ship"))
    assert not (pd.to_datetime(late["Date"]) < pd.to_datetime(late["Date_ship"])).any(), \
        "re-dating a shipment would put a complaint before its delivery"
    write(sales, BRONZE, "fact_sales_raw")
    print(f"[1] sales: dropped {int(from_rejected.sum())} rows from Rejected batches and "
          f"{int((early & outside).sum())} that would ship after {WINDOW_END.date()}; re-dated {int(redated.sum())}")


# ---------------------------------------------------------------------------
# 2. Attribute decision vs. Ac/Re
# ---------------------------------------------------------------------------
def fix_attribute_decisions() -> None:
    for name in ("fact_bottle_attribute_inspection_cq_raw", "fact_cap_attribute_inspection_cq_raw",
                 "fact_ink_attribute_inspection_cq_raw"):
        a = read(BRONZE, name)
        wrong = (a["DefectsFound"] >= a["RejectionNumber"]) & (a["LotDecision"].str.strip().str.title() == "Approved")
        assert a.loc[wrong, "MachineId"].isin(NEW_MACHINES).all(), f"{name}: a Versão 00 decision contradicts Ac/Re"
        a.loc[wrong, "LotDecision"] = "Rejected"
        write(a, BRONZE, name)
        print(f"[2] {name}: {int(wrong.sum())} decisions set to Rejected (defects >= Re)")


# ---------------------------------------------------------------------------
# 3. Material consumption chain
# ---------------------------------------------------------------------------
def fix_material_consumption() -> None:
    c = read(BRONZE, "fact_material_consumption_raw")
    expansion = c.loc[c["MachineId"].isin(NEW_MACHINES)].sort_values("RecordSeq")
    for _, lot in expansion.groupby(["MachineId", "MaterialLot"], sort=False):
        n_runs = len(lot)
        start = max(float(lot["StartWeightKg"].iloc[0]), round(RUN_CONSUMPTION_KG * n_runs + 0.5, 2))
        for index in lot.index:
            c.loc[index, "StartWeightKg"] = round(start, 2)
            start = round(start - RUN_CONSUMPTION_KG, 2)
            c.loc[index, "EndWeightKg"] = start
    grew = int((c["EndWeightKg"] > c["StartWeightKg"]).sum())
    assert grew == 0
    write(c, BRONZE, "fact_material_consumption_raw")
    print(f"[3] material consumption: {len(expansion):,} expansion records rebuilt as per-lot weight chains")


# ---------------------------------------------------------------------------
# 4. LotId ISO year
# ---------------------------------------------------------------------------
def fix_lotid_iso_year(production: pd.DataFrame) -> None:
    iso_year = pd.to_datetime(production["Date"]).dt.isocalendar()["year"].astype(int) % 100
    yy_by_order = pd.Series(iso_year.astype(str).str.zfill(2).to_numpy(), index=production["WorkOrder"])
    for name in ("fact_sales_raw", "fact_customer_complaints_raw"):
        df = read(BRONZE, name)
        has_lot = df["LotId"].notna() & df["WorkOrder"].notna()
        expected_yy = df["WorkOrder"].map(yy_by_order)
        wrong = has_lot & expected_yy.notna() & (df["LotId"].str[:2] != expected_yy)
        df.loc[wrong, "LotId"] = expected_yy[wrong] + df.loc[wrong, "LotId"].str[2:]
        write(df, BRONZE, name)
        print(f"[4] {name}: {int(wrong.sum())} LotIds re-coded to the ISO year of their ISO week")


# ---------------------------------------------------------------------------
# 5. dim_supplier
# ---------------------------------------------------------------------------
def fix_supplier_materials() -> None:
    suppliers = read(DIM, "dim_supplier")
    row = suppliers["SupplierId"] == "SUP-001"
    materials = [m.strip() for m in suppliers.loc[row, "MaterialsSupplied"].iloc[0].split(",")]
    if "HDPE-PCR" not in materials:
        materials.insert(materials.index("HDPE") + 1, "HDPE-PCR")
        suppliers.loc[row, "MaterialsSupplied"] = ", ".join(materials)
        write(suppliers, DIM, "dim_supplier")
    print(f"[5] dim_supplier: SUP-001 supplies {', '.join(materials)}")


# ---------------------------------------------------------------------------
# 6. D2 -- dedicated food-contact injection line
# ---------------------------------------------------------------------------
def move_food_caps_to_dedicated_line() -> None:
    production = read(BRONZE, "fact_production_raw")
    food_orders = set(production.loc[production["ToolId"].str.strip() == FOOD_CAP_MOLD, "WorkOrder"])
    moved = {}
    for name in ("fact_production_raw", "fact_production_plan_raw", "fact_process_parameters_raw",
                 "fact_cap_inspection_variable_cq_raw", "fact_cap_attribute_inspection_cq_raw",
                 "fact_cap_disposition_lot_cq_raw", "fact_material_consumption_raw", "fact_sales_raw",
                 "fact_downtime_raw"):
        df = read(BRONZE, name)
        if "WorkOrder" not in df.columns:
            assert not (df["MachineId"] == FOOD_CAP_FROM).any() or name == "fact_downtime_raw"
            continue
        rows = df["WorkOrder"].isin(food_orders) & (df["MachineId"].str.strip() == FOOD_CAP_FROM)
        assert not (rows & (name == "fact_sales_raw")).any(), "food-cap orders were never shipped"
        df.loc[rows, "MachineId"] = FOOD_CAP_TO
        moved[name] = int(rows.sum())
        write(df, BRONZE, name)

    profile = read(DIM, "dim_machine_profile")
    if FOOD_CAP_TO not in set(profile["MachineId"]):
        new_line = pd.DataFrame([{"MachineId": FOOD_CAP_TO, "InstallationYear": 2026, "HasAutomatedDefectDetection": True}])
        position = profile.index[profile["MachineId"] == FOOD_CAP_FROM][0] + 1
        profile = pd.concat([profile.iloc[:position], new_line, profile.iloc[position:]], ignore_index=True)
        write(profile, DIM, "dim_machine_profile")
    setup = read(DIM, "dim_machine_setup")
    setup.loc[setup["MoldId"] == FOOD_CAP_MOLD, "MachineId"] = FOOD_CAP_TO
    write(setup, DIM, "dim_machine_setup")
    print(f"[6] D2: {len(food_orders)} food-cap orders ({FOOD_CAP_MOLD}) on {FOOD_CAP_TO}; rows moved: {moved}")


# ---------------------------------------------------------------------------
# 7. D3 -- ISO 2859-1 sampling plans
# ---------------------------------------------------------------------------
STORYLINE_F_LEVEL_III = {300: ("M", 315), 472: ("N", 500)}  # n x 1.5 -> level III letter/size


def apply_iso_2859_plans() -> None:
    for name in ATTRIBUTE_TABLES:
        a = read(BRONZE, name)
        before = a["LotDecision"].str.strip().str.title().eq("Rejected").sum()
        for n_old, (letter, n_new) in STORYLINE_F_LEVEL_III.items():
            rows = a["SampleSize"] == n_old
            assert a.loc[rows, "MachineId"].eq("IM-007").all(), "n = 300/472 is Storyline F (IM-007) only"
            a.loc[rows, ["CodeLetter", "SampleSize"]] = [letter, n_new]
        plans = [aql.single_normal_plan(letter, q) for letter, q in zip(a["CodeLetter"], a["AQL"])]
        a["AcceptanceNumber"] = [ac for _, ac, _, _ in plans]
        a["RejectionNumber"] = [re for _, _, re, _ in plans]
        a["LotDecision"] = (a["DefectsFound"] >= a["RejectionNumber"]).map({True: "Rejected", False: "Approved"})
        a["InspectionLevel"] = [aql.inspection_level_used(int(lot), letter) or "Não normativo"
                                for lot, letter in zip(a["LotSize"], a["CodeLetter"])]
        write(a, BRONZE, name)
        after = int((a["LotDecision"] == "Rejected").sum())
        print(f"[7] D3 {name}: rejected characteristic-lots {int(before)} -> {after}; "
              f"levels {a['InspectionLevel'].value_counts().to_dict()}")


def main() -> None:
    production = read(BRONZE, "fact_production_raw").drop_duplicates("WorkOrder")
    fix_batch_release(production)
    fix_attribute_decisions()
    move_food_caps_to_dedicated_line()
    apply_iso_2859_plans()
    fix_material_consumption()
    fix_lotid_iso_year(production)
    fix_supplier_materials()


if __name__ == "__main__":
    main()
