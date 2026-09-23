"""
backfill_food_cap_and_material_consumption.py

Second fix-up pass, from a full end-to-end audit requested after the first two
generation passes:

1. Food bottles (FA-030/FA-031) had NO matching closure -- only pharma (TE-)
   and pote (TP-) caps were created in the first pass. A real factory selling
   food packaging needs a food-grade closure, not a reused cosmetics PP-PCR
   cap (PCR content is deliberately excluded from direct food contact
   elsewhere in this project). Adds a new SKU family `TA-` (Tampa
   Alimenticia), mold M-INJ-014, produced on IM-008 (which already runs 2
   other cap molds -- a 3rd mold on the same injection machine is exactly
   how the ORIGINAL 18-machine dataset already works, e.g. M-INJ-001 also
   runs on IM-003). Since IM-008's primary donor (IM-006) was already fully
   consumed by the first pass's 3-product cycle, this uses IM-003 as a
   second, independent donor window for just this new product -- purely
   additive (new production/QC rows on top of what's already there), not a
   retroactive change to already-generated IM-008 batches.

2. `fact_material_consumption_raw` was never generated for ANY of the new
   lines (documented simplification in the first pass) -- but on closer look
   the original data tracks masterbatch consumption even for "Natural"
   (COR-008) product runs, so it's not a table that's naturally sparse for
   uncolored products; skipping it entirely was a real end-to-end gap.
   Backfills it for all 4 new machines (including the new food-cap rows
   from fix #1 above) by cloning the same donors' consumption rows via the
   same WorkOrder join used everywhere else in this expansion, mapped to
   each new row's own product color.

Run: python scripts/backfill_food_cap_and_material_consumption.py
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_expansion_v01 as g  # noqa: E402

# ---------------------------------------------------------------------------
# Fix 1: food-grade cap for FA- bottles
# ---------------------------------------------------------------------------
FOOD_CAP_MACHINE = "IM-008"
FOOD_CAP_DONOR = "IM-003"  # IM-008's primary donor (IM-006) is already fully used
FOOD_CAP_MOLD = "M-INJ-014"
FOOD_CAP_PRODUCTS = {
    # ProductId -> (BaseMaterial, ColorId, ColorName)
    "TA-014-HDPE-FG-28410": ("HDPE-FG", "COR-008", "Natural (Uncolored)"),
    "TA-014-PP-FG-28410": ("PP-FG", "COR-001", "Opaque White"),
}


def build_food_cap_dim_rows():
    setup = pd.DataFrame([{
        "MoldId": FOOD_CAP_MOLD, "MachineId": FOOD_CAP_MACHINE, "Product": "Tampa Rosca Alimenticia 28/410",
        "Cavities": 24, "RatedCapacityPerDay": "~30.800 pieces/day", "RatedCapacityPerHour": "~1275 pieces/h",
        "CyclesPerHour": 50, "IdealCycleTimeSec": 72.0,
    }])
    cap_rows = []
    for pid, (mat, color_id, _color_name) in FOOD_CAP_PRODUCTS.items():
        cap_rows.append({
            "CapId": pid, "ItemDescription": f"Tampa rosca alimentícia 28/410 {mat}",
            "OpeningType": "Screw Cap", "MoldId": FOOD_CAP_MOLD, "OuterDiameterMm": 33, "HeightMm": 20,
            "Material": mat, "MinWeightG": 13.5, "MaxWeightG": 18.3, "MinThicknessMm": 0.9,
            "MaxThicknessMm": 1.4, "ThreadType": "Screw Neck", "ThreadDiameterMm": 28, "FiodaRosca": 410,
            "ThreadFinish": "28/410",
        })
    dim_cap = pd.DataFrame(cap_rows)
    mb_rows = []
    for pid, (mat, color_id, color_name) in FOOD_CAP_PRODUCTS.items():
        mb_type = "No Masterbatch" if color_id == "COR-008" else "White Masterbatch"
        dosage = 0.0 if color_id == "COR-008" else 0.02
        pantone = "—" if color_id == "COR-008" else "Pantone White"
        mb_rows.append([pid, "Cap", FOOD_CAP_MOLD, mat, color_id, color_name, pantone, mb_type, dosage])
    dim_masterbatch = pd.DataFrame(mb_rows, columns=["ProductId", "ProductType", "MoldId", "BaseMaterial",
                                                       "ColorId", "ColorName", "PantoneCodeApprox",
                                                       "MasterbatchType", "StandardDosagePctMass"])
    return setup, dim_cap, dim_masterbatch


def gen_food_cap_production_and_plan(production, plan, wo_start):
    d = production[production.MachineId == FOOD_CAP_DONOR].copy()
    d["DateParsed"] = pd.to_datetime(d["Date"])
    d = d[(d["DateParsed"] >= g.LAUNCH_DATE) & (d["DateParsed"] <= g.END_DATE)].sort_values("DateParsed")
    plan_by_wo = plan.set_index("WorkOrder")

    wo_ctr = g.counter(wo_start)
    product_cycle = itertools.cycle(FOOD_CAP_PRODUCTS.keys())
    operators = ["OP-INJ-005", "OP-INJ-001"]  # reuse IM-008's existing new-line operator roster
    op_cycle = itertools.cycle(operators)
    mold_batch_ctr = itertools.count(3200)  # fresh range, distinct from the first pass's 3000s

    new_production, new_plan = [], []
    donor_wo_to_new_wo, wo_info, batch_assign_all = {}, {}, {}
    batch_assign = {}

    for row in d.itertuples(index=False):
        db = row.ProductBatch
        if db not in batch_assign:
            product = next(product_cycle)
            new_batch = f"LOTE-{FOOD_CAP_MOLD}-{next(mold_batch_ctr)}"
            batch_assign[db] = (product, new_batch)
            batch_assign_all[(FOOD_CAP_MACHINE, db)] = (product, FOOD_CAP_MOLD, new_batch)
        product, new_batch = batch_assign[db]

        new_wo = f"WO-{next(wo_ctr)}"
        donor_wo_to_new_wo[row.WorkOrder] = new_wo
        operator = next(op_cycle)
        date = row.DateParsed

        produced = int(row.ProducedQty)
        rejected_donor = int(row.RejectedQty)
        base_rate = (rejected_donor / produced) if produced else 0.0
        p = 0.0 if not np.isfinite(base_rate) else float(np.clip(base_rate, 0.0, 0.9))
        rejected = int(g.RNG.binomial(produced, p)) if produced > 0 else 0

        wo_info[new_wo] = {"mold": FOOD_CAP_MOLD, "product": product, "date": date,
                            "machine": FOOD_CAP_MACHINE, "operator": operator,
                            "process": "Injection Molding", "donor_wo": row.WorkOrder}

        new_production.append({
            "Date": row.Date, "Process": "Injection Molding", "MachineId": FOOD_CAP_MACHINE,
            "ToolId": FOOD_CAP_MOLD, "WorkOrder": new_wo, "ProductId": product, "ProductBatch": new_batch,
            "StartTime": row.StartTime, "EndTime": row.EndTime, "PlannedQty": row.PlannedQty,
            "ProducedQty": produced, "RejectedQty": rejected, "OperatorId": operator,
            "IsRedo": "False", "RedoOfBatch": "",
        })
        if row.WorkOrder in plan_by_wo.index:
            prow = plan_by_wo.loc[row.WorkOrder]
            if isinstance(prow, pd.DataFrame):
                prow = prow.iloc[0]
            new_plan.append({
                "Date": row.Date, "Process": "Injection Molding", "MachineId": FOOD_CAP_MACHINE,
                "ToolId": FOOD_CAP_MOLD, "WorkOrder": new_wo, "PlannedQty": row.PlannedQty,
                "StartTime": row.StartTime, "EndTime": row.EndTime, "PlannedHours": prow["PlannedHours"],
                "ProductId": product,
            })

    prod_cols = ["Date", "Process", "MachineId", "ToolId", "WorkOrder", "ProductId", "ProductBatch",
                 "StartTime", "EndTime", "PlannedQty", "ProducedQty", "RejectedQty", "OperatorId",
                 "IsRedo", "RedoOfBatch"]
    plan_cols = ["Date", "Process", "MachineId", "ToolId", "WorkOrder", "PlannedQty", "StartTime",
                 "EndTime", "PlannedHours", "ProductId"]
    return (pd.DataFrame(new_production, columns=prod_cols), pd.DataFrame(new_plan, columns=plan_cols),
            donor_wo_to_new_wo, wo_info, batch_assign_all)


def gen_food_cap_qc(cap_var_donor, cap_attr_donor, cap_disp_donor, donor_wo_to_new_wo, wo_info, batch_assign_all):
    def batch_lookup(machine, donor_batch):
        return batch_assign_all[(machine, donor_batch)]

    def material_of(pid):
        return FOOD_CAP_PRODUCTS[pid][0]

    # --- variables ---
    var_rows = []
    sub = cap_var_donor[(cap_var_donor["MachineId"] == FOOD_CAP_DONOR)
                         & (cap_var_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys()))]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        product, mold, new_batch = batch_lookup(FOOD_CAP_MACHINE, row.ProductBatch)
        material = material_of(product)
        ms = [float(getattr(row, f"M{i}")) for i in range(1, 11)]
        xbar = sum(ms) / len(ms)
        rng_r = max(ms) - min(ms)
        std_s = float(np.std(ms, ddof=1)) if len(ms) > 1 else 0.0
        lsl, usl = float(row.LSL), float(row.USL)
        conforming = all(lsl <= m <= usl for m in ms)
        rec = {
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": FOOD_CAP_MACHINE, "MoldId": mold, "CapId": product,
            "Material": material, "CapType": "Screw Cap", "Characteristic": row.Characteristic,
            "Equipment": row.Equipment, "Standard": row.Standard, "Unit": row.Unit,
            "InspectionDateTime": row.InspectionDateTime, "SampleGroup": row.SampleGroup,
            "LSL": row.LSL, "Nominal": row.Nominal, "USL": row.USL,
        }
        for i, m in enumerate(ms, start=1):
            rec[f"M{i}"] = round(m, 3)
        rec.update({"XBar": round(xbar, 3), "RangeR": round(rng_r, 3), "StdDevS": round(std_s, 3),
                     "GroupResult": "Conforming" if conforming else "Nonconforming", "Inspector": row.Inspector})
        var_rows.append(rec)
    var_cols = (["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "CapId",
                 "Material", "CapType", "Characteristic", "Equipment", "Standard", "Unit",
                 "InspectionDateTime", "SampleGroup", "LSL", "Nominal", "USL"]
                + [f"M{i}" for i in range(1, 11)]
                + ["XBar", "RangeR", "StdDevS", "GroupResult", "Inspector"])
    var_df = pd.DataFrame(var_rows, columns=var_cols)

    # --- attributes ---
    attr_rows = []
    sub = cap_attr_donor[(cap_attr_donor["MachineId"] == FOOD_CAP_DONOR)
                          & (cap_attr_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys()))]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        product, mold, new_batch = batch_lookup(FOOD_CAP_MACHINE, row.ProductBatch)
        material = material_of(product)
        sample_size = int(row.SampleSize) if str(row.SampleSize).isdigit() else 315
        donor_defects = int(row.DefectsFound)
        base_p = min(donor_defects / sample_size, 0.5) if sample_size else 0.0
        defects = int(g.RNG.binomial(sample_size, base_p))
        rejection_n = int(row.RejectionNumber) if str(row.RejectionNumber).isdigit() else 999
        decision = "Rejected" if defects > rejection_n else "Approved"
        attr_rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": FOOD_CAP_MACHINE, "MoldId": mold, "CapId": product,
            "Material": material, "CapType": "Screw Cap", "Characteristic": row.Characteristic,
            "Class": row.Class, "AQL": row.AQL, "Standard": row.Standard,
            "InspectionLevel": row.InspectionLevel, "LotSize": row.LotSize, "CodeLetter": row.CodeLetter,
            "SampleSize": sample_size, "AcceptanceNumber": row.AcceptanceNumber,
            "RejectionNumber": row.RejectionNumber, "DefectsFound": defects, "LotDecision": decision,
            "InspectionDateTime": row.InspectionDateTime, "Inspector": row.Inspector,
        })
    attr_cols = ["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "CapId",
                 "Material", "CapType", "Characteristic", "Class", "AQL", "Standard", "InspectionLevel",
                 "LotSize", "CodeLetter", "SampleSize", "AcceptanceNumber", "RejectionNumber",
                 "DefectsFound", "LotDecision", "InspectionDateTime", "Inspector"]
    attr_df = pd.DataFrame(attr_rows, columns=attr_cols)

    # --- disposition ---
    disp_rows = []
    sub = cap_disp_donor[(cap_disp_donor["MachineId"] == FOOD_CAP_DONOR)
                          & (cap_disp_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys()))]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        product, mold, new_batch = batch_lookup(FOOD_CAP_MACHINE, row.ProductBatch)
        material = material_of(product)
        major = max(0, int(row.MajorDefects))
        minor = max(0, int(row.MinorDefects))
        critical = int(row.CriticalDefects)
        total = critical + major + minor
        rejection_n = int(row.SampleSize) // 10 + 1
        final = "Rejected" if critical > 0 or major > rejection_n else "Approved"
        disp_rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": FOOD_CAP_MACHINE, "MoldId": mold, "CapId": product,
            "Material": material, "CapType": "Screw Cap", "LotSize": row.LotSize,
            "CodeLetter": row.CodeLetter, "SampleSize": row.SampleSize, "CriticalDefects": critical,
            "MajorDefects": major, "MinorDefects": minor, "TotalSampleDefects": total,
            "VariablesDecision": row.VariablesDecision,
            "AttributesDecision": "Approved" if final == "Approved" else "Rejected",
            "FinalLotDecision": final,
            "DispositionDetail": "Approved - First Pass" if final == "Approved" else "Rejected - Segregated",
            "LotDecisionDateTime": row.LotDecisionDateTime, "Remarks": row.Remarks, "Inspector": row.Inspector,
        })
    disp_cols = ["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "CapId",
                 "Material", "CapType", "LotSize", "CodeLetter", "SampleSize", "CriticalDefects",
                 "MajorDefects", "MinorDefects", "TotalSampleDefects", "VariablesDecision",
                 "AttributesDecision", "FinalLotDecision", "DispositionDetail", "LotDecisionDateTime",
                 "Remarks", "Inspector"]
    disp_df = pd.DataFrame(disp_rows, columns=disp_cols)

    return var_df, attr_df, disp_df


def gen_process_parameters_for(pp_donor, donor_wo_to_new_wo, wo_info):
    rows = []
    sub = pp_donor[pp_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]

        def jitter(val):
            try:
                v = float(val)
            except (TypeError, ValueError):
                return val
            return round(v * float(g.RNG.normal(1.0, 0.02)), 1)

        rows.append({
            "WorkOrder": new_wo, "Process": info["process"], "MachineId": info["machine"],
            "MoldId": info["mold"], "ProductionDate": row.ProductionDate,
            "BarrelTemperatureC": jitter(row.BarrelTemperatureC),
            "InjectionSpeedPct": jitter(row.InjectionSpeedPct),
            "CoolingTimeSec": jitter(row.CoolingTimeSec),
            "PackingPressureBar": jitter(row.PackingPressureBar),
            "MoldTemperatureC": jitter(row.MoldTemperatureC),
            "MoldHumidityPct": row.MoldHumidityPct,
        })
    cols = ["WorkOrder", "Process", "MachineId", "MoldId", "ProductionDate", "BarrelTemperatureC",
            "InjectionSpeedPct", "CoolingTimeSec", "PackingPressureBar", "MoldTemperatureC", "MoldHumidityPct"]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------------------
# Fix 2: material consumption for all 4 original new machines + the new food-cap rows
# ---------------------------------------------------------------------------
def product_color_lookup():
    mb = g.read_bronze("dim_masterbatch") if False else pd.read_csv(g.DIM / "dim_masterbatch.csv", encoding="utf-8-sig")
    return dict(zip(mb["ProductId"], mb["ColorId"]))


def gen_material_consumption(mc_donor, donor_wo_to_new_wo, wo_info, color_of, recseq_start):
    rows = []
    recseq_ctr = g.counter(recseq_start)
    lot_state = {}  # machine -> (last_donor_lot, current_our_seq_per_color: dict)
    sub = mc_donor[mc_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo.get(row.WorkOrder)
        if new_wo is None:
            continue
        info = wo_info[new_wo]
        machine = info["machine"]
        product = info["product"]
        color_id = color_of.get(product)
        if color_id is None:
            continue

        state = lot_state.setdefault(machine, {"last_donor_lot": None, "seq_by_color": {}})
        seq_by_color = state["seq_by_color"]
        if row.MaterialLot != state["last_donor_lot"]:
            seq_by_color[color_id] = seq_by_color.get(color_id, 0) + 1
            state["last_donor_lot"] = row.MaterialLot
        seq = seq_by_color.setdefault(color_id, 1)
        lot = f"COL-{color_id}-{seq:03d}"

        try:
            start_w = float(row.StartWeightKg) * float(g.RNG.uniform(0.9, 1.1))
            end_w = float(row.EndWeightKg) * float(g.RNG.uniform(0.9, 1.1))
        except (TypeError, ValueError):
            start_w, end_w = row.StartWeightKg, row.EndWeightKg

        rows.append({
            "RecordSeq": next(recseq_ctr), "Date": row.Date, "Process": info["process"],
            "MachineId": machine, "Shift": row.Shift, "WorkOrder": new_wo, "MaterialId": color_id,
            "MaterialLot": lot, "StartWeightKg": round(start_w, 2), "EndWeightKg": round(end_w, 2),
        })
    cols = ["RecordSeq", "Date", "Process", "MachineId", "Shift", "WorkOrder", "MaterialId", "MaterialLot",
            "StartWeightKg", "EndWeightKg"]
    return pd.DataFrame(rows, columns=cols)


def main():
    dim_targets = [g.DIM / "dim_machine_setup.csv", g.DIM / "dim_cap.csv", g.DIM / "dim_masterbatch.csv"]
    bronze_targets = [
        g.BRONZE / "fact_production_raw.csv", g.BRONZE / "fact_production_plan_raw.csv",
        g.BRONZE / "fact_process_parameters_raw.csv",
        g.BRONZE / "fact_cap_inspection_variable_cq_raw.csv",
        g.BRONZE / "fact_cap_attribute_inspection_cq_raw.csv",
        g.BRONZE / "fact_cap_disposition_lot_cq_raw.csv",
        g.BRONZE / "fact_material_consumption_raw.csv",
    ]
    print("Snapshotting current files for the additive-only proof...")
    snap = g.snapshot(dim_targets + bronze_targets)

    print("Loading source tables...")
    production = g.read_bronze("fact_production_raw")
    plan = g.read_bronze("fact_production_plan_raw")
    cap_var = g.read_bronze("fact_cap_inspection_variable_cq_raw")
    cap_attr = g.read_bronze("fact_cap_attribute_inspection_cq_raw")
    cap_disp = g.read_bronze("fact_cap_disposition_lot_cq_raw")
    pp_donor = g.read_bronze("fact_process_parameters_raw")
    mc_donor = g.read_bronze("fact_material_consumption_raw")

    wo_max = production["WorkOrder"].str.replace("WO-", "", regex=False).astype(int).max()
    recseq_max = mc_donor["RecordSeq"].astype(int).max()

    print("Building food-cap dim rows...")
    setup_row, cap_rows, mb_rows = build_food_cap_dim_rows()

    print("Generating food-cap production/plan (new donor window: IM-003 -> IM-008)...")
    fc_production, fc_plan, fc_wo_map, fc_wo_info, fc_batch_map = gen_food_cap_production_and_plan(
        production, plan, wo_max + 1)
    print(f"  food-cap production rows: {len(fc_production)}")
    assert len(fc_production) > 0, "food-cap backfill produced zero production rows -- investigate"

    print("Generating food-cap QC (variables/attributes/disposition)...")
    fc_var, fc_attr, fc_disp = gen_food_cap_qc(cap_var, cap_attr, cap_disp, fc_wo_map, fc_wo_info, fc_batch_map)
    print(f"  variable={len(fc_var)} attribute={len(fc_attr)} disposition={len(fc_disp)}")

    print("Generating food-cap process parameters...")
    fc_pp = gen_process_parameters_for(pp_donor, fc_wo_map, fc_wo_info)

    print("Re-deriving the original 4-machine donor_wo_to_new_wo/wo_info mapping (deterministic)...")
    _p, _pl, orig_wo_map, orig_wo_info, _batch = g.gen_production_and_plan(production, plan)

    print("Building product->color lookup (post food-cap dim additions)...")
    color_of = product_color_lookup()
    color_of.update({pid: FOOD_CAP_PRODUCTS[pid][1] for pid in FOOD_CAP_PRODUCTS})

    print("Generating material consumption for the original 4 new machines...")
    mc_orig = gen_material_consumption(mc_donor, orig_wo_map, orig_wo_info, color_of, recseq_max + 1)
    print(f"  original-4-machine consumption rows: {len(mc_orig)}")

    print("Generating material consumption for the new food-cap rows...")
    mc_food = gen_material_consumption(mc_donor, fc_wo_map, fc_wo_info, color_of,
                                        recseq_max + 1 + len(mc_orig))
    print(f"  food-cap consumption rows: {len(mc_food)}")

    print("\nAll generation succeeded in memory. Writing to disk...")
    g.append_csv(g.DIM / "dim_machine_setup.csv", setup_row)
    g.append_csv(g.DIM / "dim_cap.csv", cap_rows)
    g.append_csv(g.DIM / "dim_masterbatch.csv", mb_rows)
    g.append_csv(g.BRONZE / "fact_production_raw.csv", fc_production)
    g.append_csv(g.BRONZE / "fact_production_plan_raw.csv", fc_plan)
    g.append_csv(g.BRONZE / "fact_process_parameters_raw.csv", fc_pp)
    g.append_csv(g.BRONZE / "fact_cap_inspection_variable_cq_raw.csv", fc_var)
    g.append_csv(g.BRONZE / "fact_cap_attribute_inspection_cq_raw.csv", fc_attr)
    g.append_csv(g.BRONZE / "fact_cap_disposition_lot_cq_raw.csv", fc_disp)
    g.append_csv(g.BRONZE / "fact_material_consumption_raw.csv", mc_orig)
    g.append_csv(g.BRONZE / "fact_material_consumption_raw.csv", mc_food)

    print("\nVerifying additivity...")
    ok = g.verify_additivity(snap)
    print("\nADDITIVITY CHECK:", "PASSED" if ok else "FAILED -- investigate before proceeding")
    return ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
