"""
backfill_pote_qc_and_storyline_f.py

Fix-up pass on top of generate_expansion_v01.py, discovered after that script's
first run: IM-007 (potes) was assigned donor machine IM-005, which historically
only ever produced CAPS (all its real QC history lives in the fact_cap_*_cq_raw
tables, none in fact_bottle_*_cq_raw) -- so potes ended up with production/
downtime rows but ZERO quality-inspection rows. This script backfills that gap
by cloning IM-005's real CAP QC rows (same WorkOrders, same AQL/lot cadence)
into the BOTTLE QC schema (potes are ProductType=Bottle) with characteristics
remapped to what makes physical sense for an injection-molded jar.

It also implements Storyline F here (needs the pote attribute rows to exist
first): a proactive AQL sampling tightening for PT- products, 2026-10-01 to
2026-10-15, triggered by a documented external customer audit (CUST-015) --
SampleSize increases, no elevated defect probability (this is NOT a quality
escape, it's a control tightened in response to an external trigger).

Re-derives the exact same donor_wo_to_new_wo / wo_info / batch_assign_all
mapping generate_expansion_v01.py produced (deterministic: same counters,
same donor data, same iteration order) WITHOUT re-appending production/plan
rows -- only appends the missing bottle-QC rows plus 2 new NC/CAPA rows.

Run: python scripts/backfill_pote_qc_and_storyline_f.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_expansion_v01 as g  # noqa: E402

STORYLINE_F_WINDOW = (pd.Timestamp("2026-10-01"), pd.Timestamp("2026-10-15"))

CAP_TO_POTE_VAR_CHAR = {"Weight": "Weight", "Height": "Height", "Diameter": "Mouth Diameter", "Torque": "Stack Load"}
CAP_TO_POTE_ATTR_CHAR = {"Thread": "Drop Test", "Sealing": "Sealing", "Flash": "Flash",
                          "Short Shot": "Short Shot", "Stain": "Stain", "Color": "Color"}


def gen_pote_variables(cap_var_donor, donor_wo_to_new_wo, wo_info, batch_lookup):
    rows = []
    sub = cap_var_donor[(cap_var_donor["MachineId"] == "IM-005")
                         & (cap_var_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys()))]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] != "IM-007":
            continue
        char = CAP_TO_POTE_VAR_CHAR.get(row.Characteristic)
        if char is None:
            continue
        product, mold, new_batch = batch_lookup("IM-007", row.ProductBatch)
        if not product.startswith("PT-"):
            continue
        material = g._material_of(product)
        ms = [float(getattr(row, f"M{i}")) for i in range(1, 6)]
        xbar = sum(ms) / len(ms)
        rng_r = max(ms) - min(ms)
        std_s = float(np.std(ms, ddof=1)) if len(ms) > 1 else 0.0
        lsl, usl = float(row.LSL), float(row.USL)
        conforming = all(lsl <= m <= usl for m in ms)
        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": "IM-007", "MoldId": mold, "BottleId": product,
            "Material": material, "Characteristic": char, "Equipment": row.Equipment,
            "Standard": row.Standard, "Unit": row.Unit, "InspectionDateTime": row.InspectionDateTime,
            "SampleGroup": row.SampleGroup, "LSL": row.LSL, "Nominal": row.Nominal, "USL": row.USL,
            "M1": round(ms[0], 3), "M2": round(ms[1], 3), "M3": round(ms[2], 3), "M4": round(ms[3], 3),
            "M5": round(ms[4], 3), "XBar": round(xbar, 3), "RangeR": round(rng_r, 3),
            "StdDevS": round(std_s, 3), "GroupResult": "Conforming" if conforming else "Nonconforming",
            "Inspector": row.Inspector,
        })
    cols = ["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "BottleId",
            "Material", "Characteristic", "Equipment", "Standard", "Unit", "InspectionDateTime",
            "SampleGroup", "LSL", "Nominal", "USL", "M1", "M2", "M3", "M4", "M5", "XBar", "RangeR",
            "StdDevS", "GroupResult", "Inspector"]
    return pd.DataFrame(rows, columns=cols)


def gen_pote_attributes(cap_attr_donor, donor_wo_to_new_wo, wo_info, batch_lookup):
    rows = []
    sub = cap_attr_donor[(cap_attr_donor["MachineId"] == "IM-005")
                          & (cap_attr_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys()))]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] != "IM-007":
            continue
        char = CAP_TO_POTE_ATTR_CHAR.get(row.Characteristic)
        if char is None:
            continue
        product, mold, new_batch = batch_lookup("IM-007", row.ProductBatch)
        if not product.startswith("PT-"):
            continue
        material = g._material_of(product)
        date = pd.to_datetime(row.ProductionDate)

        sample_size = int(row.SampleSize) if str(row.SampleSize).isdigit() else 315
        donor_defects = int(row.DefectsFound)
        base_p = min(donor_defects / sample_size, 0.5) if sample_size else 0.0

        # Storyline F: proactive sampling tightening for PT- in the window, no defect elevation.
        in_f_window = STORYLINE_F_WINDOW[0] <= date <= STORYLINE_F_WINDOW[1]
        if in_f_window:
            sample_size = int(round(sample_size * 1.5))
        defects = int(g.RNG.binomial(sample_size, base_p))
        rejection_n = int(row.RejectionNumber) if str(row.RejectionNumber).isdigit() else 999
        decision = "Rejected" if defects > rejection_n else "Approved"

        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "MachineId": "IM-007", "MoldId": mold, "BottleId": product, "Material": material,
            "Characteristic": char, "Class": row.Class, "AQL": row.AQL,
            "Standard": row.Standard, "InspectionLevel": row.InspectionLevel, "LotSize": row.LotSize,
            "CodeLetter": row.CodeLetter, "SampleSize": sample_size,
            "AcceptanceNumber": row.AcceptanceNumber, "RejectionNumber": row.RejectionNumber,
            "DefectsFound": defects, "LotDecision": decision, "InspectionDateTime": row.InspectionDateTime,
            "Inspector": row.Inspector,
        })
    cols = ["ProductBatch", "WorkOrder", "ProductionDate", "MachineId", "MoldId", "BottleId", "Material",
            "Characteristic", "Class", "AQL", "Standard", "InspectionLevel", "LotSize", "CodeLetter",
            "SampleSize", "AcceptanceNumber", "RejectionNumber", "DefectsFound", "LotDecision",
            "InspectionDateTime", "Inspector"]
    return pd.DataFrame(rows, columns=cols)


def gen_pote_disposition(cap_disp_donor, donor_wo_to_new_wo, wo_info, batch_lookup):
    rows = []
    sub = cap_disp_donor[(cap_disp_donor["MachineId"] == "IM-005")
                          & (cap_disp_donor["WorkOrder"].isin(donor_wo_to_new_wo.keys()))]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] != "IM-007":
            continue
        product, mold, new_batch = batch_lookup("IM-007", row.ProductBatch)
        if not product.startswith("PT-"):
            continue
        major = max(0, int(row.MajorDefects))
        minor = max(0, int(row.MinorDefects))
        critical = int(row.CriticalDefects)
        total = critical + major + minor
        rejection_n = int(row.SampleSize) // 10 + 1
        final = "Rejected" if critical > 0 or major > rejection_n else "Approved"
        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": "IM-007", "MoldId": mold, "BottleId": product,
            "LotSize": row.LotSize, "CodeLetter": row.CodeLetter, "SampleSize": row.SampleSize,
            "CriticalDefects": critical, "MajorDefects": major, "MinorDefects": minor,
            "TotalSampleDefects": total, "VariablesDecision": row.VariablesDecision,
            "AttributesDecision": "Approved" if final == "Approved" else "Rejected",
            "FinalLotDecision": final,
            "DispositionDetail": "Approved - First Pass" if final == "Approved" else "Rejected - Segregated",
            "LotDecisionDateTime": row.LotDecisionDateTime, "Remarks": row.Remarks, "Inspector": row.Inspector,
        })
    cols = ["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "BottleId",
            "LotSize", "CodeLetter", "SampleSize", "CriticalDefects", "MajorDefects", "MinorDefects",
            "TotalSampleDefects", "VariablesDecision", "AttributesDecision", "FinalLotDecision",
            "DispositionDetail", "LotDecisionDateTime", "Remarks", "Inspector"]
    return pd.DataFrame(rows, columns=cols)


def _next_free_id(csv_name, id_col, prefix, width=0):
    """Recomputes the next-free id from the CURRENT file on disk -- generate_expansion_v01's
    module-level counters (g.nc_ctr, g.capa_ctr, ...) reset to their pre-first-run starting
    points on a fresh import, which would collide with IDs that first run already wrote."""
    df = g.read_bronze(csv_name)
    nums = df[id_col].str.replace(prefix, "", regex=False).astype(int)
    n = nums.max() + 1
    return f"{prefix}{n:0{width}d}" if width else f"{prefix}{n}"


def storyline_f_evidence_rows():
    nc_id = _next_free_id("fact_nonconformance_raw", "NCId", "NC-", width=5)
    capa_id = _next_free_id("fact_capa_raw", "CAPAId", "CAPA-")
    nc = pd.DataFrame([{
        "NCId": nc_id, "Date": "2026-10-01", "Type": "External", "Source": "Customer Audit",
        "Area": "Quality", "Process": "Injection Molding", "Category": "Proactive Sampling Tightening",
        "Severity": "Minor", "RelatedRecordId": "CUST-015",
    }])
    capa = pd.DataFrame([{
        "CAPAId": capa_id, "OpenDate": "2026-10-01", "DueDate": "2026-10-15", "CloseDate": "2026-10-15",
        "Status": "Closed", "CAPAType": "Preventive", "RelatedNCId": nc_id, "Area": "Quality",
        "Process": "Injection Molding", "Severity": "Minor", "RootCauseCategory": "Customer Requirement",
        "Owner": "Diogo Ferreira", "EffectivenessCheck": "Effective",
    }])
    return nc, capa


def main():
    targets = [
        g.BRONZE / "fact_bottle_inspection_variables_cq_raw.csv",
        g.BRONZE / "fact_bottle_attribute_inspection_cq_raw.csv",
        g.BRONZE / "fact_bottle_disposition_lot_cq_raw.csv",
        g.BRONZE / "fact_nonconformance_raw.csv",
        g.BRONZE / "fact_capa_raw.csv",
    ]
    print("Snapshotting current files for the additive-only proof...")
    snap = g.snapshot(targets)

    print("Re-deriving the deterministic donor_wo_to_new_wo / wo_info / batch_assign_all mapping "
          "(does NOT re-append production/plan rows -- those are already correct on disk)...")
    production = g.read_bronze("fact_production_raw")
    plan = g.read_bronze("fact_production_plan_raw")
    _new_production, _new_plan, donor_wo_to_new_wo, wo_info, batch_assign_all = g.gen_production_and_plan(production, plan)

    def batch_lookup(machine, donor_batch):
        return batch_assign_all[(machine, donor_batch)]

    print("Loading cap QC donor tables (IM-005's real history)...")
    cap_var = g.read_bronze("fact_cap_inspection_variable_cq_raw")
    cap_attr = g.read_bronze("fact_cap_attribute_inspection_cq_raw")
    cap_disp = g.read_bronze("fact_cap_disposition_lot_cq_raw")

    print("Generating pote bottle-QC rows (backfill) + Storyline F sampling tightening...")
    pote_var = gen_pote_variables(cap_var, donor_wo_to_new_wo, wo_info, batch_lookup)
    pote_attr = gen_pote_attributes(cap_attr, donor_wo_to_new_wo, wo_info, batch_lookup)
    pote_disp = gen_pote_disposition(cap_disp, donor_wo_to_new_wo, wo_info, batch_lookup)
    print(f"  pote variable rows: {len(pote_var)}, attribute rows: {len(pote_attr)}, disposition rows: {len(pote_disp)}")
    assert len(pote_var) > 0 and len(pote_attr) > 0 and len(pote_disp) > 0, "backfill produced zero rows -- investigate"

    nc, capa = storyline_f_evidence_rows()

    print("Appending to bronze CSVs...")
    g.append_csv(g.BRONZE / "fact_bottle_inspection_variables_cq_raw.csv", pote_var)
    g.append_csv(g.BRONZE / "fact_bottle_attribute_inspection_cq_raw.csv", pote_attr)
    g.append_csv(g.BRONZE / "fact_bottle_disposition_lot_cq_raw.csv", pote_disp)
    g.append_csv(g.BRONZE / "fact_nonconformance_raw.csv", nc)
    g.append_csv(g.BRONZE / "fact_capa_raw.csv", capa)

    print("\nVerifying additivity...")
    ok = g.verify_additivity(snap)
    print("\nADDITIVITY CHECK:", "PASSED" if ok else "FAILED -- investigate before proceeding")
    return ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
