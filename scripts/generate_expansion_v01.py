"""
generate_expansion_v01.py

Additive portfolio-expansion generator for the manufacturing-performance-analytics
project. Adds NEW rows only, for NEW entities (4 new machines, ~15 new product
SKUs, 2 new suppliers, 4 new customers, 6 new employees) across the trailing
window 2026-07-06 -> 2026-12-30 of the already-frozen 18-month dataset
(2025-07-01 -> 2026-12-30).

Hard invariant: every existing row in datasets/bronze/*.csv and
datasets/dim/*.csv is left byte-identical. This script only appends. It
proves that invariant itself (see verify_additivity()) rather than asking
the reader to trust it.

Design: "clone-and-perturb" a real analogous work order / QC lot / downtime
event from a clean, non-storyline donor machine in the SAME trailing date
window, then remap identifiers (machine/mold/product/operator/work order)
and, for the 5 deliberate storylines (A-E), bias the defect/downtime/
off-spec probabilities for the specific entity+window each story lives on.
Reusing a donor's real row (instead of a from-scratch statistical model)
is what keeps the new data's baseline noise/shift/seasonality realistic
without re-deriving it.

Run: python scripts/generate_expansion_v01.py
"""
from __future__ import annotations

import sys
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BRONZE = ROOT / "datasets" / "bronze"
DIM = ROOT / "datasets" / "dim"

sys.path.insert(0, str(ROOT))
from lib.etl_lib import build_lotid_prefix  # noqa: E402

RNG = np.random.default_rng(20260706)

LAUNCH_DATE = pd.Timestamp("2026-07-06")
END_DATE = pd.Timestamp("2026-12-30")

# ---------------------------------------------------------------------------
# 0. Next-free-id counters (confirmed maxima in the frozen bronze data)
# ---------------------------------------------------------------------------
NEXT_WO = 16095
NEXT_NC = 1327
NEXT_CAPA = 4811
NEXT_CC = 20208
NEXT_SO = 18007
NEXT_SC = 30079
NEXT_RI = 6879
NEXT_PO = 6844
NEXT_RECORDSEQ = 15422


def counter(start):
    n = start
    while True:
        yield n
        n += 1


wo_ctr = counter(NEXT_WO)
nc_ctr = counter(NEXT_NC)
capa_ctr = counter(NEXT_CAPA)
cc_ctr = counter(NEXT_CC)
so_ctr = counter(NEXT_SO)
sc_ctr = counter(NEXT_SC)
ri_ctr = counter(NEXT_RI)
po_ctr = counter(NEXT_PO)
recseq_ctr = counter(NEXT_RECORDSEQ)

# ---------------------------------------------------------------------------
# 1. New machines / donors / operators / molds / products
# ---------------------------------------------------------------------------
NEW_MACHINES = {
    "ISBM-009": {"process": "Blow Molding", "donor": "ISBM-006", "install_year": 2026},
    "ISBM-010": {"process": "Blow Molding", "donor": "ISBM-004", "install_year": 2026},
    "IM-007": {"process": "Injection Molding", "donor": "IM-005", "install_year": 2026},
    "IM-008": {"process": "Injection Molding", "donor": "IM-006", "install_year": 2026},
}

# Blow-Molding maintenance already staffed (Sandra Reis et al.) -> reused as-is.
BLOW_MOLDING_TECHS = [
    ("Sandra Reis", "Mechanical"), ("Hugo Marques", "Mechanical"),
    ("Patrícia Lima", "Mechanical"), ("José Pinto", "Mechanical"),
    ("Vitor Sousa", "Electrical"), ("Camila Duarte", "Electrical"),
]
# Injection Molding gets its first-ever named maintenance staff (new machines only).
INJECTION_TECHS = [("Rui Fonseca", "Mechanical"), ("Marta Nogueira", "Electrical")]

NEW_OPERATORS = {
    "ISBM-009": ["OP-SOP-005", "OP-SOP-002"],
    "ISBM-010": ["OP-SOP-006", "OP-SOP-004"],  # OP-SOP-006 is Storyline D's trainee
    "IM-007": ["OP-INJ-004", "AUX-INJ-001"],
    "IM-008": ["OP-INJ-005", "OP-INJ-001"],
}

# ProductId -> (MoldId, MachineId, BaseMaterial, ColorId, ColorName, family) for bottles/potes
BOTTLE_PRODUCTS = {
    "FA-030-HDPE-FG-1000": ("M-SOP-030", "ISBM-009", "HDPE-FG", "COR-008", "Natural (Uncolored)"),
    "FA-030-PP-FG-1000": ("M-SOP-030", "ISBM-009", "PP-FG", "COR-008", "Natural (Uncolored)"),
    "FA-031-HDPE-FG-500": ("M-SOP-031", "ISBM-009", "HDPE-FG", "COR-008", "Natural (Uncolored)"),
    "FA-031-PP-FG-500": ("M-SOP-031", "ISBM-009", "PP-FG", "COR-008", "Natural (Uncolored)"),
    "FP-032-PP-PG-100": ("M-SOP-032", "ISBM-010", "PP-PG", "COR-009", "Pharma White"),
    "FP-032-PET-PG-100": ("M-SOP-032", "ISBM-010", "PET-PG", "COR-008", "Natural (Uncolored)"),
    "FP-033-PP-PG-250": ("M-SOP-033", "ISBM-010", "PP-PG", "COR-009", "Pharma White"),
    "FP-033-PET-PG-250": ("M-SOP-033", "ISBM-010", "PET-PG", "COR-008", "Natural (Uncolored)"),
    "PT-010-PP-050": ("M-INJ-010", "IM-007", "PP", "COR-001", "Opaque White"),
    "PT-010-PP-PG-050": ("M-INJ-010", "IM-007", "PP-PG", "COR-009", "Pharma White"),
    "PT-011-PP-100": ("M-INJ-011", "IM-007", "PP", "COR-001", "Opaque White"),
    "PT-011-PP-PG-100": ("M-INJ-011", "IM-007", "PP-PG", "COR-009", "Pharma White"),
}
CAP_PRODUCTS = {
    "TE-012-PP-PG-24410": ("M-INJ-012", "IM-008", "PP-PG", "COR-009", "Pharma White", "Tamper-Evident Screw Cap"),
    "TP-013-PP-070": ("M-INJ-013", "IM-008", "PP", "COR-001", "Opaque White", "Snap Lid"),
    "TP-013-PP-PG-070": ("M-INJ-013", "IM-008", "PP-PG", "COR-009", "Pharma White", "Snap Lid"),
}

PRODUCTS_BY_MACHINE = {}
for pid, (mold, machine, *_rest) in {**BOTTLE_PRODUCTS, **CAP_PRODUCTS}.items():
    PRODUCTS_BY_MACHINE.setdefault(machine, []).append(pid)

NEW_SUPPLIERS = {"SUP-009": "PP-PG,PET-PG", "SUP-010": "HDPE-FG,PP-FG"}
STORYLINE_C_WINDOW = (pd.Timestamp("2026-08-01"), pd.Timestamp("2026-09-15"))
STORYLINE_D_WINDOW = (pd.Timestamp("2026-08-01"), pd.Timestamp("2026-09-05"))
STORYLINE_A_WINDOW = (pd.Timestamp("2026-07-06"), pd.Timestamp("2026-08-24"))
STORYLINE_B_WINDOW = (pd.Timestamp("2026-07-06"), pd.Timestamp("2026-08-31"))


def read_bronze(name):
    return pd.read_csv(BRONZE / f"{name}.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)


def snapshot(paths):
    """Row count + sha256 of the file's current bytes, for the additive-only proof."""
    snap = {}
    for p in paths:
        b = p.read_bytes()
        snap[p] = (b.count(b"\n"), hashlib.sha256(b).hexdigest())
    return snap


def verify_additivity(snap_before):
    ok = True
    for p, (lines_before, hash_before) in snap_before.items():
        b = p.read_bytes()
        lines_after = b.count(b"\n")
        prefix = b"\n".join(b.split(b"\n")[:lines_before]) + (b"\n" if lines_before else b"")
        prefix_hash = hashlib.sha256(prefix).hexdigest()
        added = lines_after - lines_before
        status = "OK" if prefix_hash == hash_before and added >= 0 else "MISMATCH"
        if status != "OK":
            ok = False
        print(f"  {p.name}: +{added} rows  [{status}]")
    return ok


def append_csv(path, df):
    if df.empty:
        return
    df.to_csv(path, mode="a", header=False, index=False, lineterminator="\n")


# ---------------------------------------------------------------------------
# 2. Dimension / catalog appends (Section 1-4 of the plan)
# ---------------------------------------------------------------------------

def build_dim_machine_profile_rows():
    rows = [{"MachineId": m, "InstallationYear": cfg["install_year"], "HasAutomatedDefectDetection": "True"}
            for m, cfg in NEW_MACHINES.items()]
    return pd.DataFrame(rows)


def build_dim_machine_setup_rows():
    # (MoldId, MachineId, Product, Cavities, RatedCapacityPerDay, RatedCapacityPerHour, CyclesPerHour, IdealCycleTimeSec)
    rows = [
        ("M-SOP-030", "ISBM-009", "Frasco Alimenticio Redondo, 1000 ml", 6, "~11.500 bottles/day", "~475 bottles/h", 75, 48.0),
        ("M-SOP-031", "ISBM-009", "Frasco Alimenticio Oval, 500 ml", 8, "~15.400 bottles/day", "~650 bottles/h", 75, 48.0),
        ("M-SOP-032", "ISBM-010", "Frasco Farma Redondo, 100 ml", 8, "~15.400 bottles/day", "~650 bottles/h", 75, 48.0),
        ("M-SOP-033", "ISBM-010", "Frasco Farma Redondo, 250 ml", 8, "~15.400 bottles/day", "~650 bottles/h", 75, 48.0),
        ("M-INJ-010", "IM-007", "Pote Creme, 50 g", 16, "~20.500 pieces/day", "~850 pieces/h", 50, 72.0),
        ("M-INJ-011", "IM-007", "Pote Creme, 100 g", 16, "~20.500 pieces/day", "~850 pieces/h", 50, 72.0),
        ("M-INJ-012", "IM-008", "Tampa Farma Lacre 24/410", 24, "~30.800 pieces/day", "~1275 pieces/h", 50, 72.0),
        ("M-INJ-013", "IM-008", "Tampa de Pote 70mm", 16, "~20.500 pieces/day", "~850 pieces/h", 50, 72.0),
    ]
    cols = ["MoldId", "MachineId", "Product", "Cavities", "RatedCapacityPerDay", "RatedCapacityPerHour", "CyclesPerHour", "IdealCycleTimeSec"]
    return pd.DataFrame(rows, columns=cols)


def build_dim_masterbatch_rows():
    rows = []
    for pid, (mold, machine, mat, color_id, color_name) in BOTTLE_PRODUCTS.items():
        mb_type = "No Masterbatch" if color_id == "COR-008" else f"{color_name.split()[0]} Masterbatch"
        dosage = 0.0 if color_id == "COR-008" else 0.02
        pantone = "—" if color_id == "COR-008" else "Pantone Cool Gray 1 C" if color_id == "COR-009" else "Pantone White"
        rows.append([pid, "Bottle", mold, mat, color_id, color_name, pantone, mb_type, dosage])
    for pid, (mold, machine, mat, color_id, color_name, _opening) in CAP_PRODUCTS.items():
        mb_type = "No Masterbatch" if color_id == "COR-008" else f"{color_name.split()[0]} Masterbatch"
        dosage = 0.0 if color_id == "COR-008" else 0.02
        pantone = "—" if color_id == "COR-008" else "Pantone Cool Gray 1 C" if color_id == "COR-009" else "Pantone White"
        rows.append([pid, "Cap", mold, mat, color_id, color_name, pantone, mb_type, dosage])
    cols = ["ProductId", "ProductType", "MoldId", "BaseMaterial", "ColorId", "ColorName", "PantoneCodeApprox", "MasterbatchType", "StandardDosagePctMass"]
    return pd.DataFrame(rows, columns=cols)


def build_dim_cap_rows():
    rows = [
        ("TE-012-PP-PG-24410", "Tampa farma lacre 24/410 PP-PG", "Tamper-Evident Screw Cap", "M-INJ-012",
         29, 22, "PP-PG", 9.5, 13.5, 0.9, 1.4, "Screw Neck", 24, 410, "24/410"),
        ("TP-013-PP-070", "Tampa de pote 70mm PP", "Snap Lid", "M-INJ-013",
         70, 12, "PP", 14.0, 19.0, 1.0, 1.6, "Snap Fit", 70, "", "Snap 70mm"),
        ("TP-013-PP-PG-070", "Tampa de pote 70mm PP-PG", "Snap Lid", "M-INJ-013",
         70, 12, "PP-PG", 14.0, 19.0, 1.0, 1.6, "Snap Fit", 70, "", "Snap 70mm"),
    ]
    cols = ["CapId", "ItemDescription", "OpeningType", "MoldId", "OuterDiameterMm", "HeightMm", "Material",
            "MinWeightG", "MaxWeightG", "MinThicknessMm", "MaxThicknessMm", "ThreadType", "ThreadDiameterMm",
            "FiodaRosca", "ThreadFinish"]
    return pd.DataFrame(rows, columns=cols)


def build_dim_customer_rows():
    rows = [
        ("CUST-015", "NutriBoas Embalagens Alimentares Lda", "Leiria", "Food Packaging", "Medium", "LEI", "Portugal", "Iberian Peninsula"),
        ("CUST-016", "Iberconserva Foods S.A.", "Porto", "Food Packaging", "Large", "POR", "Portugal", "Iberian Peninsula"),
        ("CUST-017", "FarmaPack Ibérica S.L.", "Madrid", "Pharmaceutical", "Large", "M", "Spain", "Iberian Peninsula"),
        ("CUST-018", "Rheinland MedPack GmbH", "Frankfurt", "Pharmaceutical", "Medium", "HE", "Germany", "Rest of Europe"),
    ]
    cols = ["CustomerId", "CustomerName", "City", "Segment", "CustomerTier", "State", "Country", "Region"]
    return pd.DataFrame(rows, columns=cols)


def build_dim_supplier_rows():
    rows = [
        ("SUP-009", "FarmaResin Especialidades Ltda", "Brazil", "São Paulo", "PP-PG, PET-PG", "Tier 2", 1, "Spot Purchase"),
        ("SUP-010", "NutriPolímeros Ibéria S.A.", "Spain", "Valencia", "HDPE-FG, PP-FG", "Tier 1", 1, "Annual Contract"),
    ]
    cols = ["SupplierId", "SupplierName", "Country", "HeadquartersCity", "MaterialsSupplied", "SupplierTier", "YearsAsSupplier", "ContractType"]
    return pd.DataFrame(rows, columns=cols)


def build_dim_bottle_control_plan_rows():
    cols = ["Process", "Operation", "Characteristic", "Class", "InspectionType", "Specification", "Method",
            "Equipment", "Standard", "ISOLevel", "AQL", "Frequency", "LotSize", "ISOCode", "SampleSize",
            "AcceptanceNumber", "RejectionNumber", "Owner", "ReactionPlan"]
    rows = [
        ("Blow Molding", "Production", "Migration Test (Food Contact)", "Major", "Attribute",
         "Compliant with Regulation (EU) 10/2011", "Migration Cell Test", "Migration Test Cell",
         "Regulamento (UE) 10/2011 / EN 1186-3:2022", "II", 1.5, "Per lot", "Per lot", "Auto", "Auto",
         "ver tabela", "ver tabela", "Laboratory", "Block Lot"),
        ("Injection Molding", "Production", "Mouth Diameter", "Critical", "Variable", "Per drawing",
         "Go/No-Go", "Gauge", "ISO 3951", "—", "—", "Every 1 h", "Production run", "—",
         "10 pieces", "—", "—", "Quality", "Adjust Mold"),
        ("Injection Molding", "Production", "Drop Test", "Critical", "Attribute", "No cracking/leakage",
         "Drop Test", "ASTM D2463 Drop Rig", "ASTM D2463-23", "II", 0.65, "Per lot", "Per lot", "Auto",
         "Auto", "ver tabela", "ver tabela", "Laboratory", "Block Lot"),
        ("Injection Molding", "Production", "Stack Load", "Major", "Variable", "Per technical data sheet",
         "Compression Test", "Universal Testing Machine", "ASTM D642", "—", "—", "Per lot", "Lot",
         "—", "5 pieces", "—", "—", "Laboratory", "Adjust Process"),
    ]
    return pd.DataFrame(rows, columns=cols)


def build_dim_cap_control_plan_rows():
    cols = ["Process", "Operation", "Characteristic", "Class", "InspectionType", "Specification", "Method",
            "Equipment", "Standard", "ISOLevel", "AQL", "Frequency", "LotSize", "ISOCode", "SampleSize",
            "AcceptanceNumber", "RejectionNumber", "Owner", "ReactionPlan"]
    rows = [
        ("Injection Molding", "Production", "Tamper Band Separation", "Critical", "Attribute",
         "No separation under 5N axial pull", "Pull Test", "Tamper Band Tester", "21 CFR 211.132", "II",
         0.1, "Per lot", "Per lot", "Auto", "Auto", 0, 1, "Laboratory", "Block Lot"),
    ]
    return pd.DataFrame(rows, columns=cols)


def build_dim_raw_material_control_plan_rows():
    cols = ["Material", "Characteristic", "Standard", "Method", "Unit", "LSL", "Nominal", "USL",
            "InspectionType", "Frequency", "SampleSize", "ReactionPlan"]
    rows = [
        ("HDPE-FG", "Melt Flow Index", "ASTM D1238 / ISO 1133-1", "Melt Indexer", "g/10min", 0.25, 0.35, 0.45, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("HDPE-FG", "Density", "ASTM D792 / ISO 1183-1", "Density Column", "g/cm3", 0.95, 0.954, 0.958, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("HDPE-FG", "Overall Migration (Food Contact)", "Regulamento (UE) 10/2011 / EN 1186-3:2022", "Migration Cell Test", "mg/dm2", 0.0, 3.0, 10.0, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("PP-FG", "Melt Flow Index", "ASTM D1238 / ISO 1133-1", "Melt Indexer", "g/10min", 2.0, 3.0, 4.5, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("PP-FG", "Density", "ASTM D792 / ISO 1183-1", "Density Column", "g/cm3", 0.9, 0.905, 0.91, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("PP-FG", "Overall Migration (Food Contact)", "Regulamento (UE) 10/2011 / EN 1186-3:2022", "Migration Cell Test", "mg/dm2", 0.0, 3.0, 10.0, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("PP-PG", "Melt Flow Index", "ASTM D1238 / ISO 1133-1", "Melt Indexer", "g/10min", 2.0, 3.0, 4.5, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("PP-PG", "Density", "ASTM D792 / ISO 1183-1", "Density Column", "g/cm3", 0.9, 0.905, 0.91, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("PP-PG", "Biological Reactivity (USP <661.1>)", "USP <661.1> Plastic Materials of Construction, Class VI", "Extractables Panel", "pass/fail", "", "", "", "Attribute", "Annual Qualification", "1 study", "Reject Lot"),
        ("PET-PG", "Intrinsic Viscosity", "ASTM D4603 / ISO 1628-5", "Viscometer", "dL/g", 0.72, 0.8, 0.86, "Variable", "Per incoming lot", "3 readings", "Quarantine & Notify Supplier"),
        ("PET-PG", "Biological Reactivity (USP <661.1>)", "USP <661.1> Plastic Materials of Construction, Class VI", "Extractables Panel", "pass/fail", "", "", "", "Attribute", "Annual Qualification", "1 study", "Reject Lot"),
    ]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------------------
# 3. Storyline probability/bias multipliers (Section 6 of the plan)
# ---------------------------------------------------------------------------

def storyline_a_multiplier(machine, product, date):
    """A: ISBM-009 learning curve on FA-030, +70% decaying over 7 weeks."""
    if machine == "ISBM-009" and str(product).startswith("FA-030"):
        start, end = STORYLINE_A_WINDOW
        if start <= date <= end:
            weeks = (date - start).days / 7.0
            return 1.0 + 0.7 * max(0.0, 1.0 - weeks / 7.0)
    return 1.0


def storyline_c_spread_multiplier(machine, product, characteristic, date):
    """C: SUP-009 early off-spec resin widens Weight/Thickness spread on FP-032/ISBM-010."""
    if machine == "ISBM-010" and str(product).startswith("FP-032") and characteristic in ("Weight", "Thickness"):
        start, end = STORYLINE_C_WINDOW
        if start <= date <= end:
            return 1.8
    return 1.0


def storyline_d_bias(operator, characteristic, date):
    """D: OP-SOP-006 training-curve mean bias (no extra spread), Weight/Thickness only."""
    if operator == "OP-SOP-006" and characteristic in ("Weight", "Thickness"):
        start, end = STORYLINE_D_WINDOW
        if start <= date <= end:
            return True
    return False


def storyline_e_multiplier(machine, product, characteristic, date):
    """E: mold wear on M-INJ-012 (TE-012), Tamper Band Separation climbs ~2%->5% all window, unresolved."""
    if machine == "IM-008" and str(product).startswith("TE-012") and characteristic == "Tamper Band Separation":
        span = (END_DATE - LAUNCH_DATE).days
        frac = min(max((date - LAUNCH_DATE).days / span, 0.0), 1.0)
        return 1.0 + 1.5 * frac
    return 1.0


# ---------------------------------------------------------------------------
# 4. Production & plan (defines the WorkOrder/ProductBatch universe every
#    other table joins against)
# ---------------------------------------------------------------------------
import itertools  # noqa: E402


def gen_production_and_plan(production, plan):
    new_production, new_plan = [], []
    donor_wo_to_new_wo = {}
    wo_info = {}  # new_wo -> dict(mold, product, date, machine, operator, process)
    mold_batch_counters = {}
    batch_assign_all = {}  # (machine, donor_batch) -> (product, mold, new_batch)

    plan_by_wo = plan.set_index("WorkOrder")

    for machine, cfg in NEW_MACHINES.items():
        donor = cfg["donor"]
        d = production[production.MachineId == donor].copy()
        d["DateParsed"] = pd.to_datetime(d["Date"])
        d = d[(d["DateParsed"] >= LAUNCH_DATE) & (d["DateParsed"] <= END_DATE)].sort_values("DateParsed")

        product_cycle = itertools.cycle(PRODUCTS_BY_MACHINE[machine])
        op_cycle = itertools.cycle(NEW_OPERATORS[machine])
        batch_assign = {}

        for row in d.itertuples(index=False):
            db = row.ProductBatch
            if db not in batch_assign:
                product = next(product_cycle)
                mold = (BOTTLE_PRODUCTS.get(product) or CAP_PRODUCTS.get(product))[0]
                mold_batch_counters.setdefault(mold, itertools.count(3000))
                new_batch = f"LOTE-{mold}-{next(mold_batch_counters[mold])}"
                batch_assign[db] = (product, mold, new_batch)
                batch_assign_all[(machine, db)] = (product, mold, new_batch)
            product, mold, new_batch = batch_assign[db]

            new_wo = f"WO-{next(wo_ctr)}"
            donor_wo_to_new_wo[row.WorkOrder] = new_wo
            operator = next(op_cycle)

            produced = int(row.ProducedQty)
            rejected_donor = int(row.RejectedQty)
            base_rate = (rejected_donor / produced) if produced else 0.0
            mult = storyline_a_multiplier(machine, product, row.DateParsed)
            p = base_rate * mult
            p = 0.0 if not np.isfinite(p) else float(np.clip(p, 0.0, 0.9))
            rejected = int(RNG.binomial(produced, p)) if produced > 0 else 0

            wo_info[new_wo] = {"mold": mold, "product": product, "date": row.DateParsed, "machine": machine,
                                "operator": operator, "process": cfg["process"], "donor_wo": row.WorkOrder}

            new_production.append({
                "Date": row.Date, "Process": cfg["process"], "MachineId": machine, "ToolId": mold,
                "WorkOrder": new_wo, "ProductId": product, "ProductBatch": new_batch,
                "StartTime": row.StartTime, "EndTime": row.EndTime, "PlannedQty": row.PlannedQty,
                "ProducedQty": produced, "RejectedQty": rejected, "OperatorId": operator,
                "IsRedo": "False", "RedoOfBatch": "",
            })

            if row.WorkOrder in plan_by_wo.index:
                prow = plan_by_wo.loc[row.WorkOrder]
                if isinstance(prow, pd.DataFrame):
                    prow = prow.iloc[0]
                new_plan.append({
                    "Date": row.Date, "Process": cfg["process"], "MachineId": machine, "ToolId": mold,
                    "WorkOrder": new_wo, "PlannedQty": row.PlannedQty, "StartTime": row.StartTime,
                    "EndTime": row.EndTime, "PlannedHours": prow["PlannedHours"], "ProductId": product,
                })

    prod_cols = ["Date", "Process", "MachineId", "ToolId", "WorkOrder", "ProductId", "ProductBatch",
                 "StartTime", "EndTime", "PlannedQty", "ProducedQty", "RejectedQty", "OperatorId",
                 "IsRedo", "RedoOfBatch"]
    plan_cols = ["Date", "Process", "MachineId", "ToolId", "WorkOrder", "PlannedQty", "StartTime",
                 "EndTime", "PlannedHours", "ProductId"]
    return (pd.DataFrame(new_production, columns=prod_cols), pd.DataFrame(new_plan, columns=plan_cols),
            donor_wo_to_new_wo, wo_info, batch_assign_all)


# ---------------------------------------------------------------------------
# 5. Process parameters (simple clone + light jitter, no storyline tie-in)
# ---------------------------------------------------------------------------

def gen_process_parameters(process_parameters, donor_wo_to_new_wo, wo_info):
    rows = []
    pp = process_parameters[process_parameters["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in pp.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]

        def jitter(val):
            try:
                v = float(val)
            except (TypeError, ValueError):
                return val
            return round(v * float(RNG.normal(1.0, 0.02)), 1)

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
# 6. Bottle / cap QC tables (variables, attributes, disposition)
#    Bottle-family machines: ISBM-009, ISBM-010, IM-007 (potes are ProductType=Bottle)
#    Cap-family machine: IM-008
# ---------------------------------------------------------------------------
BOTTLE_MACHINES = {"ISBM-009", "ISBM-010", "IM-007"}
CAP_MACHINES = {"IM-008"}


def _material_of(product):
    d = BOTTLE_PRODUCTS.get(product) or CAP_PRODUCTS.get(product)
    return d[2]


def gen_bottle_variables(donor_var, donor_wo_to_new_wo, wo_info, batch_lookup):
    rows = []
    sub = donor_var[donor_var["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] not in BOTTLE_MACHINES:
            continue
        product, mold, new_batch = batch_lookup(info["machine"], row.ProductBatch)
        material = _material_of(product)
        date = pd.to_datetime(row.ProductionDate)
        ms = [float(getattr(row, f"M{i}")) for i in range(1, 6)]

        spread_mult = storyline_c_spread_multiplier(info["machine"], product, row.Characteristic, date)
        biased = storyline_d_bias(info["operator"], row.Characteristic, date)

        mean_m = sum(ms) / len(ms)
        if spread_mult != 1.0:
            ms = [mean_m + (m - mean_m) * spread_mult for m in ms]
        if biased:
            lsl, usl = float(row.LSL), float(row.USL)
            bias_amt = 1.5 * (usl - lsl) / 6.0  # ~1.5 sigma-equivalent shift
            ms = [m + bias_amt for m in ms]

        xbar = sum(ms) / len(ms)
        rng_r = max(ms) - min(ms)
        std_s = float(np.std(ms, ddof=1)) if len(ms) > 1 else 0.0
        lsl, usl = float(row.LSL), float(row.USL)
        conforming = all(lsl <= m <= usl for m in ms)

        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": info["machine"], "MoldId": mold, "BottleId": product,
            "Material": material, "Characteristic": row.Characteristic, "Equipment": row.Equipment,
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


def gen_bottle_attributes(donor_attr, donor_wo_to_new_wo, wo_info, batch_lookup):
    # Stable per-characteristic baseline rate from the DONOR's full 18-month history
    # (not the individual cloned row's own noisy count) -- Storyline A's +70% needs a
    # steady base to multiply, otherwise per-row/per-batch donor noise swamps the signal.
    char_baseline = (donor_attr.groupby("Characteristic")
                      .apply(lambda g: g["DefectsFound"].astype(int).sum() / g["SampleSize"].astype(int).sum(),
                             include_groups=False))

    rows = []
    sub = donor_attr[donor_attr["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] not in BOTTLE_MACHINES:
            continue
        product, mold, new_batch = batch_lookup(info["machine"], row.ProductBatch)
        material = _material_of(product)
        date = pd.to_datetime(row.ProductionDate)
        sample_size = int(row.SampleSize) if str(row.SampleSize).isdigit() else 200
        mult = storyline_a_multiplier(info["machine"], product, date)
        base_p = min(float(char_baseline.get(row.Characteristic, 0.01)), 0.5)
        p = min(base_p * mult, 0.9)
        defects = int(RNG.binomial(sample_size, p))
        rejection_n = int(row.RejectionNumber) if str(row.RejectionNumber).isdigit() else 999
        decision = "Rejected" if defects > rejection_n else "Approved"

        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "MachineId": info["machine"], "MoldId": mold, "BottleId": product, "Material": material,
            "Characteristic": row.Characteristic, "Class": row.Class, "AQL": row.AQL,
            "Standard": row.Standard, "InspectionLevel": row.InspectionLevel, "LotSize": row.LotSize,
            "CodeLetter": row.CodeLetter, "SampleSize": row.SampleSize,
            "AcceptanceNumber": row.AcceptanceNumber, "RejectionNumber": row.RejectionNumber,
            "DefectsFound": defects, "LotDecision": decision, "InspectionDateTime": row.InspectionDateTime,
            "Inspector": row.Inspector,
        })
    cols = ["ProductBatch", "WorkOrder", "ProductionDate", "MachineId", "MoldId", "BottleId", "Material",
            "Characteristic", "Class", "AQL", "Standard", "InspectionLevel", "LotSize", "CodeLetter",
            "SampleSize", "AcceptanceNumber", "RejectionNumber", "DefectsFound", "LotDecision",
            "InspectionDateTime", "Inspector"]
    return pd.DataFrame(rows, columns=cols)


def gen_bottle_disposition(donor_disp, donor_wo_to_new_wo, wo_info, batch_lookup):
    rows = []
    sub = donor_disp[donor_disp["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] not in BOTTLE_MACHINES:
            continue
        product, mold, new_batch = batch_lookup(info["machine"], row.ProductBatch)
        date = pd.to_datetime(row.ProductionDate)
        mult = storyline_a_multiplier(info["machine"], product, date)
        major = max(0, int(RNG.poisson(max(int(row.MajorDefects), 0) * mult)))
        minor = max(0, int(RNG.poisson(max(int(row.MinorDefects), 0) * mult)))
        critical = int(row.CriticalDefects)
        total = critical + major + minor
        rejection_n = int(row.SampleSize) // 10 + 1
        final = "Rejected" if critical > 0 or major > rejection_n else "Approved"

        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": info["machine"], "MoldId": mold, "BottleId": product,
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


def gen_cap_variables(donor_var, donor_wo_to_new_wo, wo_info, batch_lookup):
    rows = []
    sub = donor_var[donor_var["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] not in CAP_MACHINES:
            continue
        product, mold, new_batch = batch_lookup(info["machine"], row.ProductBatch)
        material = _material_of(product)
        cap_type = (CAP_PRODUCTS[product])[5]
        ms = [float(getattr(row, f"M{i}")) for i in range(1, 11)]
        xbar = sum(ms) / len(ms)
        rng_r = max(ms) - min(ms)
        std_s = float(np.std(ms, ddof=1)) if len(ms) > 1 else 0.0
        lsl, usl = float(row.LSL), float(row.USL)
        conforming = all(lsl <= m <= usl for m in ms)
        rec = {
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": info["machine"], "MoldId": mold, "CapId": product,
            "Material": material, "CapType": cap_type, "Characteristic": row.Characteristic,
            "Equipment": row.Equipment, "Standard": row.Standard, "Unit": row.Unit,
            "InspectionDateTime": row.InspectionDateTime, "SampleGroup": row.SampleGroup,
            "LSL": row.LSL, "Nominal": row.Nominal, "USL": row.USL,
        }
        for i, m in enumerate(ms, start=1):
            rec[f"M{i}"] = round(m, 3)
        rec.update({"XBar": round(xbar, 3), "RangeR": round(rng_r, 3), "StdDevS": round(std_s, 3),
                     "GroupResult": "Conforming" if conforming else "Nonconforming", "Inspector": row.Inspector})
        rows.append(rec)
    cols = (["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "CapId",
             "Material", "CapType", "Characteristic", "Equipment", "Standard", "Unit",
             "InspectionDateTime", "SampleGroup", "LSL", "Nominal", "USL"]
            + [f"M{i}" for i in range(1, 11)]
            + ["XBar", "RangeR", "StdDevS", "GroupResult", "Inspector"])
    return pd.DataFrame(rows, columns=cols)


def gen_cap_attributes(donor_attr, donor_wo_to_new_wo, wo_info, batch_lookup, new_production_df):
    rows = []
    sub = donor_attr[donor_attr["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] not in CAP_MACHINES:
            continue
        product, mold, new_batch = batch_lookup(info["machine"], row.ProductBatch)
        material = _material_of(product)
        cap_type = (CAP_PRODUCTS[product])[5]
        sample_size = int(row.SampleSize) if str(row.SampleSize).isdigit() else 315
        donor_defects = int(row.DefectsFound)
        base_p = min(donor_defects / sample_size, 0.5) if sample_size else 0.0
        defects = int(RNG.binomial(sample_size, base_p))
        rejection_n = int(row.RejectionNumber) if str(row.RejectionNumber).isdigit() else 999
        decision = "Rejected" if defects > rejection_n else "Approved"
        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": info["machine"], "MoldId": mold, "CapId": product,
            "Material": material, "CapType": cap_type, "Characteristic": row.Characteristic,
            "Class": row.Class, "AQL": row.AQL, "Standard": row.Standard,
            "InspectionLevel": row.InspectionLevel, "LotSize": row.LotSize, "CodeLetter": row.CodeLetter,
            "SampleSize": row.SampleSize, "AcceptanceNumber": row.AcceptanceNumber,
            "RejectionNumber": row.RejectionNumber, "DefectsFound": defects, "LotDecision": decision,
            "InspectionDateTime": row.InspectionDateTime, "Inspector": row.Inspector,
        })

    # Inject the Storyline-E synthetic characteristic (Tamper Band Separation) for every TE-012 lot.
    te_lots = new_production_df[new_production_df["ProductId"] == "TE-012-PP-PG-24410"]
    te_lots = te_lots.drop_duplicates(subset=["ProductBatch"])
    for r in te_lots.itertuples(index=False):
        date = pd.to_datetime(r.Date)
        mult = storyline_e_multiplier("IM-008", r.ProductId, "Tamper Band Separation", date)
        sample_size = 200
        p = min(0.02 * mult, 0.5)
        defects = int(RNG.binomial(sample_size, p))
        decision = "Rejected" if defects > 1 else "Approved"
        rows.append({
            "ProductBatch": r.ProductBatch, "WorkOrder": r.WorkOrder, "ProductionDate": r.Date,
            "Shift": "Shift 1", "MachineId": "IM-008", "MoldId": r.ToolId, "CapId": r.ProductId,
            "Material": _material_of(r.ProductId), "CapType": "Tamper-Evident Screw Cap",
            "Characteristic": "Tamper Band Separation", "Class": "Critical", "AQL": 0.1,
            "Standard": "21 CFR 211.132", "InspectionLevel": "II", "LotSize": r.ProducedQty,
            "CodeLetter": "L", "SampleSize": sample_size, "AcceptanceNumber": 0, "RejectionNumber": 1,
            "DefectsFound": defects, "LotDecision": decision,
            "InspectionDateTime": f"{r.Date} 10:00:00.000", "Inspector": "Elena Santos",
        })

    cols = ["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "CapId",
            "Material", "CapType", "Characteristic", "Class", "AQL", "Standard", "InspectionLevel",
            "LotSize", "CodeLetter", "SampleSize", "AcceptanceNumber", "RejectionNumber", "DefectsFound",
            "LotDecision", "InspectionDateTime", "Inspector"]
    return pd.DataFrame(rows, columns=cols)


def gen_cap_disposition(donor_disp, donor_wo_to_new_wo, wo_info, batch_lookup):
    rows = []
    sub = donor_disp[donor_disp["WorkOrder"].isin(donor_wo_to_new_wo.keys())]
    for row in sub.itertuples(index=False):
        new_wo = donor_wo_to_new_wo[row.WorkOrder]
        info = wo_info[new_wo]
        if info["machine"] not in CAP_MACHINES:
            continue
        product, mold, new_batch = batch_lookup(info["machine"], row.ProductBatch)
        material = _material_of(product)
        cap_type = (CAP_PRODUCTS[product])[5]
        major = max(0, int(RNG.poisson(max(int(row.MajorDefects), 0))))
        minor = max(0, int(RNG.poisson(max(int(row.MinorDefects), 0))))
        critical = int(row.CriticalDefects)
        total = critical + major + minor
        rejection_n = int(row.SampleSize) // 10 + 1
        final = "Rejected" if critical > 0 or major > rejection_n else "Approved"
        rows.append({
            "ProductBatch": new_batch, "WorkOrder": new_wo, "ProductionDate": row.ProductionDate,
            "Shift": row.Shift, "MachineId": info["machine"], "MoldId": mold, "CapId": product,
            "Material": material, "CapType": cap_type, "LotSize": row.LotSize, "CodeLetter": row.CodeLetter,
            "SampleSize": row.SampleSize, "CriticalDefects": critical, "MajorDefects": major,
            "MinorDefects": minor, "TotalSampleDefects": total, "VariablesDecision": row.VariablesDecision,
            "AttributesDecision": "Approved" if final == "Approved" else "Rejected",
            "FinalLotDecision": final,
            "DispositionDetail": "Approved - First Pass" if final == "Approved" else "Rejected - Segregated",
            "LotDecisionDateTime": row.LotDecisionDateTime, "Remarks": row.Remarks, "Inspector": row.Inspector,
        })
    cols = ["ProductBatch", "WorkOrder", "ProductionDate", "Shift", "MachineId", "MoldId", "CapId",
            "Material", "CapType", "LotSize", "CodeLetter", "SampleSize", "CriticalDefects", "MajorDefects",
            "MinorDefects", "TotalSampleDefects", "VariablesDecision", "AttributesDecision",
            "FinalLotDecision", "DispositionDetail", "LotDecisionDateTime", "Remarks", "Inspector"]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------------------
# 7. Downtime (Storyline B: IM-007 infant mortality)
# ---------------------------------------------------------------------------
ELECTRICAL_COMMISSIONING_REASONS = ["Electrical Fault - Commissioning", "Controller Calibration",
                                     "PLC/HMI Fault", "Sensor Wiring Fault"]


def gen_downtime(downtime):
    rows = []
    for machine, cfg in NEW_MACHINES.items():
        donor = cfg["donor"]
        d = downtime[downtime["MachineId"] == donor].copy()
        d["_date"] = pd.to_datetime(d["Date"])
        d = d[(d["_date"] >= LAUNCH_DATE) & (d["_date"] <= END_DATE)]
        for row in d.itertuples(index=False):
            tech, team = _maintenance_for(machine, row.MaintenanceTeam)
            rows.append({
                "Date": row.Date, "Process": cfg["process"], "MachineId": machine, "Shift": row.Shift,
                "StoppageStartTime": row.StoppageStartTime, "StoppageEndTime": row.StoppageEndTime,
                "PlannedStoppage": row.PlannedStoppage, "StoppageReason": row.StoppageReason,
                "MaintenanceTeam": team, "MaintenanceTechnician": tech,
            })

        if machine == "IM-007":
            start, end = STORYLINE_B_WINDOW
            n_weeks = max(1, (end - start).days // 7)
            donor_unplanned = d[d["PlannedStoppage"] == "No"]
            if donor_unplanned.empty:
                donor_unplanned = d
            # Baseline weekly unplanned-stoppage rate for THIS machine (cloned donor density),
            # so the "~3x baseline, decaying by week 8" story scales to how busy this
            # downtime table actually is, instead of a flat, easily-swamped absolute count.
            baseline_weekly_rate = len(donor_unplanned) / max(1, (END_DATE - LAUNCH_DATE).days / 7.0)
            for week in range(n_weeks):
                week_start = start + pd.Timedelta(days=7 * week)
                decay = max(0.0, 1.0 - week / 8.0)  # falls off sharply after week 8
                n_extra = int(RNG.poisson(2.0 * baseline_weekly_rate * decay))
                for _ in range(n_extra):
                    template = donor_unplanned.sample(1, random_state=int(RNG.integers(0, 1_000_000))).iloc[0]
                    day_offset = int(RNG.integers(0, 7))
                    event_date = week_start + pd.Timedelta(days=day_offset)
                    if event_date > END_DATE:
                        continue
                    tech, team = "Rui Fonseca", "Mechanical"
                    if RNG.random() < 0.6:
                        tech, team = "Marta Nogueira", "Electrical"
                    rows.append({
                        "Date": event_date.strftime("%Y-%m-%d"), "Process": "Injection Molding",
                        "MachineId": "IM-007", "Shift": template["Shift"],
                        "StoppageStartTime": template["StoppageStartTime"],
                        "StoppageEndTime": template["StoppageEndTime"], "PlannedStoppage": "No",
                        "StoppageReason": ELECTRICAL_COMMISSIONING_REASONS[int(RNG.integers(0, 4))],
                        "MaintenanceTeam": team, "MaintenanceTechnician": tech,
                    })
    cols = ["Date", "Process", "MachineId", "Shift", "StoppageStartTime", "StoppageEndTime",
            "PlannedStoppage", "StoppageReason", "MaintenanceTeam", "MaintenanceTechnician"]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------------------
# 8. Incoming raw-material inspection / lot disposition (Storyline C)
# ---------------------------------------------------------------------------
# (Material -> [(Characteristic, Unit, LSL, Nominal, USL), ...]) mirrors the new
# dim_raw_material_control_plan.csv rows (numeric characteristics only).
NEW_MATERIAL_SPECS = {
    "HDPE-FG": [("Melt Flow Index", "g/10min", 0.25, 0.35, 0.45), ("Density", "g/cm3", 0.95, 0.954, 0.958)],
    "PP-FG": [("Melt Flow Index", "g/10min", 2.0, 3.0, 4.5), ("Density", "g/cm3", 0.9, 0.905, 0.91)],
    "PP-PG": [("Melt Flow Index", "g/10min", 2.0, 3.0, 4.5), ("Density", "g/cm3", 0.9, 0.905, 0.91)],
    "PET-PG": [("Intrinsic Viscosity", "dL/g", 0.72, 0.8, 0.86)],
}
MATERIAL_STANDARD = {
    "Melt Flow Index": "ASTM D1238 / ISO 1133-1", "Density": "ASTM D792 / ISO 1183-1",
    "Intrinsic Viscosity": "ASTM D4603 / ISO 1628-5",
}


def gen_raw_material(inspectors):
    insp_rows, disp_rows = [], []
    supplier_materials = {"SUP-009": ["PP-PG", "PET-PG"], "SUP-010": ["HDPE-FG", "PP-FG"]}
    for supplier, materials in supplier_materials.items():
        for material in materials:
            lot_seq = 0
            date = LAUNCH_DATE
            while date <= END_DATE:
                lot_seq += 1
                lot_id = f"RM-{material}-{lot_seq:05d}"
                po_id = f"PO-{next(po_ctr)}"
                received_kg = round(float(RNG.uniform(700, 1300)), 1)
                in_window = supplier == "SUP-009" and STORYLINE_C_WINDOW[0] <= date <= STORYLINE_C_WINDOW[1]
                p_fail = 0.20 if in_window else 0.045
                failed = 0
                for char, unit, lsl, nominal, usl in NEW_MATERIAL_SPECS[material]:
                    off_spec = RNG.random() < p_fail
                    if off_spec:
                        value = usl + abs(usl - nominal) * float(RNG.uniform(0.1, 0.6))
                        result = "Fail"
                        failed += 1
                    else:
                        value = float(RNG.normal(nominal, (usl - lsl) / 8.0))
                        result = "Pass" if lsl <= value <= usl else "Fail"
                        if result == "Fail":
                            failed += 1
                    insp_rows.append({
                        "InspectionId": f"RI-{next(ri_ctr):06d}", "Date": date.strftime("%Y-%m-%d"),
                        "SupplierId": supplier, "Material": material, "MaterialLotId": lot_id,
                        "PurchaseOrderId": po_id, "Characteristic": char, "Standard": MATERIAL_STANDARD[char],
                        "Method": "Melt Indexer" if char == "Melt Flow Index" else ("Density Column" if char == "Density" else "Viscometer"),
                        "Unit": unit, "ResultValue": round(value, 4), "LSL": lsl, "Nominal": nominal,
                        "USL": usl, "Result": result, "Inspector": inspectors[int(RNG.integers(0, len(inspectors)))],
                    })
                final_decision = "Rejected" if failed > 0 else "Accepted"
                disp_rows.append({
                    "MaterialLotId": lot_id, "Date": date.strftime("%Y-%m-%d"), "SupplierId": supplier,
                    "Material": material, "PurchaseOrderId": po_id, "ReceivedQtyKg": received_kg,
                    "CharacteristicsTested": len(NEW_MATERIAL_SPECS[material]), "CharacteristicsFailed": failed,
                    "FinalDecision": final_decision, "SupplierResponseDays": (int(RNG.integers(3, 12)) if failed else ""),
                    "Inspector": inspectors[int(RNG.integers(0, len(inspectors)))],
                })
                date += pd.Timedelta(days=14)
    insp_cols = ["InspectionId", "Date", "SupplierId", "Material", "MaterialLotId", "PurchaseOrderId",
                 "Characteristic", "Standard", "Method", "Unit", "ResultValue", "LSL", "Nominal", "USL",
                 "Result", "Inspector"]
    disp_cols = ["MaterialLotId", "Date", "SupplierId", "Material", "PurchaseOrderId", "ReceivedQtyKg",
                 "CharacteristicsTested", "CharacteristicsFailed", "FinalDecision", "SupplierResponseDays",
                 "Inspector"]
    return pd.DataFrame(insp_rows, columns=insp_cols), pd.DataFrame(disp_rows, columns=disp_cols)


# ---------------------------------------------------------------------------
# 9. Sales, customer complaints, supplier complaints, NC/CAPA (light-touch)
# ---------------------------------------------------------------------------
CUSTOMER_FOR_PRODUCT = {}
for pid in BOTTLE_PRODUCTS:
    if pid.startswith("FA-"):
        CUSTOMER_FOR_PRODUCT[pid] = ["CUST-015", "CUST-016"]
    elif pid.startswith("FP-"):
        CUSTOMER_FOR_PRODUCT[pid] = ["CUST-017", "CUST-018"]
    elif pid.startswith("PT-"):
        CUSTOMER_FOR_PRODUCT[pid] = ["CUST-015", "CUST-017", "CUST-001"]
for pid in CAP_PRODUCTS:
    CUSTOMER_FOR_PRODUCT[pid] = ["CUST-017", "CUST-018"] if pid.startswith("TE-") else ["CUST-015", "CUST-017"]


def gen_sales(new_production_df, donor_sales_prices):
    rows = []
    for r in new_production_df.itertuples(index=False):
        if RNG.random() > 0.55:  # not every lot ships as its own sales order in the sample window
            continue
        customers = CUSTOMER_FOR_PRODUCT.get(r.ProductId, ["CUST-001"])
        customer = customers[int(RNG.integers(0, len(customers)))]
        family = "Bottle" if BOTTLE_PRODUCTS.get(r.ProductId) else "Cap"
        base_price = donor_sales_prices.get(family, 0.20)
        unit_price = round(base_price * float(RNG.uniform(0.85, 1.25)), 4)
        shipped = int(int(r.ProducedQty) * float(RNG.uniform(0.6, 0.95)))
        if shipped <= 0:
            continue
        so_id = f"SO-{next(so_ctr)}"
        lot_prefix = build_lotid_prefix(
            pd.Series([r.Date]), pd.Series([2]), pd.Series([r.Process]), pd.Series([r.MachineId]),
            pd.Series([r.WorkOrder]),
        ).iloc[0]
        rows.append({
            "SalesOrderId": so_id, "Date": r.Date, "CustomerId": customer, "ProductFamily": family,
            "Process": r.Process, "ProductId": r.ProductId, "WorkOrder": r.WorkOrder,
            "LotId": f"{lot_prefix}01", "MachineId": r.MachineId, "ShippedQty": shipped,
            "UnitPriceEUR": unit_price, "TotalValueEUR": round(shipped * unit_price, 2),
        })
    cols = ["SalesOrderId", "Date", "CustomerId", "ProductFamily", "Process", "ProductId", "WorkOrder",
            "LotId", "MachineId", "ShippedQty", "UnitPriceEUR", "TotalValueEUR"]
    return pd.DataFrame(rows, columns=cols)


def gen_narrative_evidence_rows():
    """A handful of hand-authored complaint/supplier-complaint/NC/CAPA rows that give
    Storylines C and E a paper trail, mirroring how the existing storylines each have
    matching evidence in these tables (not a proportional clone -- these are rare events)."""
    complaints = [
        {"ComplaintId": f"CC-{next(cc_ctr)}", "Date": "2026-09-02", "CustomerId": "CUST-017",
         "ProductFamily": "Bottle", "Process": "Blow Molding", "ProductId": "FP-032-PP-PG-100",
         "WorkOrder": "", "DefectType": "Weight Out of Specification", "Severity": "Major",
         "QtyAffected": 40, "Status": "Closed", "ResolutionDate": "2026-09-20", "SalesOrderId": ""},
        {"ComplaintId": f"CC-{next(cc_ctr)}", "Date": "2026-11-18", "CustomerId": "CUST-018",
         "ProductFamily": "Cap", "Process": "Injection Molding", "ProductId": "TE-012-PP-PG-24410",
         "WorkOrder": "", "DefectType": "Tamper Band Separation", "Severity": "Critical",
         "QtyAffected": 15, "Status": "Open", "ResolutionDate": "", "SalesOrderId": ""},
    ]
    cc_cols = ["ComplaintId", "Date", "CustomerId", "ProductFamily", "Process", "ProductId", "WorkOrder",
               "LotId", "DefectType", "Severity", "QtyAffected", "Status", "ResolutionDate", "SalesOrderId"]
    for c in complaints:
        c["LotId"] = ""
    complaints_df = pd.DataFrame(complaints, columns=cc_cols)

    supplier_complaints = [
        {"SupplierComplaintId": f"SC-{next(sc_ctr)}", "Date": "2026-08-05", "SupplierId": "SUP-009",
         "Material": "PP-PG", "MaterialLotId": "RM-PP-PG-00002", "PurchaseOrderId": "",
         "IssueType": "Off-Spec Test Result", "DateSupplierResponded": "2026-08-11",
         "DateResolved": "2026-08-19", "Status": "Closed"},
    ]
    sc_cols = ["SupplierComplaintId", "Date", "SupplierId", "Material", "MaterialLotId", "PurchaseOrderId",
               "IssueType", "DateSupplierResponded", "DateResolved", "Status"]
    supplier_complaints_df = pd.DataFrame(supplier_complaints, columns=sc_cols)

    nc = [
        {"NCId": f"NC-{next(nc_ctr):05d}", "Date": "2026-08-06", "Type": "Internal", "Source": "Incoming Inspection",
         "Area": "Quality", "Process": "Blow Molding", "Category": "Raw Material Deviation", "Severity": "Major",
         "RelatedRecordId": "RM-PP-PG-00002"},
        {"NCId": f"NC-{next(nc_ctr):05d}", "Date": "2026-11-18", "Type": "Internal", "Source": "Customer Complaint",
         "Area": "Production", "Process": "Injection Molding", "Category": "Mold Wear",
         "Severity": "Critical", "RelatedRecordId": "M-INJ-012"},
    ]
    nc_cols = ["NCId", "Date", "Type", "Source", "Area", "Process", "Category", "Severity", "RelatedRecordId"]
    nc_df = pd.DataFrame(nc, columns=nc_cols)

    capa = [
        {"CAPAId": f"CAPA-{next(capa_ctr)}", "OpenDate": "2026-08-07", "DueDate": "2026-09-04",
         "CloseDate": "2026-08-25", "Status": "Closed", "CAPAType": "Corrective", "RelatedNCId": nc[0]["NCId"],
         "Area": "Quality", "Process": "Blow Molding", "Severity": "Major", "RootCauseCategory": "Raw Material",
         "Owner": "Diogo Ferreira", "EffectivenessCheck": "Effective"},
        {"CAPAId": f"CAPA-{next(capa_ctr)}", "OpenDate": "2026-11-19", "DueDate": "2026-12-17",
         "CloseDate": "", "Status": "Open", "CAPAType": "Corrective", "RelatedNCId": nc[1]["NCId"],
         "Area": "Production", "Process": "Injection Molding", "Severity": "Critical",
         "RootCauseCategory": "Tooling / Mold Wear", "Owner": "Rui Fonseca", "EffectivenessCheck": ""},
    ]
    capa_cols = ["CAPAId", "OpenDate", "DueDate", "CloseDate", "Status", "CAPAType", "RelatedNCId", "Area",
                 "Process", "Severity", "RootCauseCategory", "Owner", "EffectivenessCheck"]
    capa_df = pd.DataFrame(capa, columns=capa_cols)

    return complaints_df, supplier_complaints_df, nc_df, capa_df


def _maintenance_for(machine, donor_team):
    if machine in ("ISBM-009", "ISBM-010"):
        pool = BLOW_MOLDING_TECHS
    else:
        pool = INJECTION_TECHS
    team = "Mechanical" if str(donor_team).strip().lower().startswith("mech") else "Electrical"
    candidates = [n for n, t in pool if t == team] or [n for n, _t in pool]
    name = candidates[int(RNG.integers(0, len(candidates)))]
    return name, team


# ---------------------------------------------------------------------------
# 10. Orchestration
# ---------------------------------------------------------------------------

def main():
    dim_targets = [
        DIM / "dim_machine_profile.csv", DIM / "dim_machine_setup.csv", DIM / "dim_masterbatch.csv",
        DIM / "dim_cap.csv", DIM / "dim_customer.csv", DIM / "dim_supplier.csv",
        DIM / "dim_bottle_control_plan_cq.csv", DIM / "dim_cap_control_plan_cq.csv",
        DIM / "dim_raw_material_control_plan.csv",
    ]
    bronze_targets = [
        BRONZE / "fact_production_raw.csv", BRONZE / "fact_production_plan_raw.csv",
        BRONZE / "fact_process_parameters_raw.csv",
        BRONZE / "fact_bottle_inspection_variables_cq_raw.csv",
        BRONZE / "fact_bottle_attribute_inspection_cq_raw.csv",
        BRONZE / "fact_bottle_disposition_lot_cq_raw.csv",
        BRONZE / "fact_cap_inspection_variable_cq_raw.csv",
        BRONZE / "fact_cap_attribute_inspection_cq_raw.csv",
        BRONZE / "fact_cap_disposition_lot_cq_raw.csv",
        BRONZE / "fact_downtime_raw.csv",
        BRONZE / "fact_raw_material_inspection_raw.csv",
        BRONZE / "fact_raw_material_lot_disposition_raw.csv",
        BRONZE / "fact_sales_raw.csv", BRONZE / "fact_customer_complaints_raw.csv",
        BRONZE / "fact_supplier_complaints_raw.csv", BRONZE / "fact_nonconformance_raw.csv",
        BRONZE / "fact_capa_raw.csv",
    ]

    print("Snapshotting current files for the additive-only proof...")
    snap = snapshot(dim_targets + bronze_targets)

    print("Loading source bronze/dim tables...")
    production = read_bronze("fact_production_raw")
    plan = read_bronze("fact_production_plan_raw")
    process_parameters = read_bronze("fact_process_parameters_raw")
    bottle_var = read_bronze("fact_bottle_inspection_variables_cq_raw")
    bottle_attr = read_bronze("fact_bottle_attribute_inspection_cq_raw")
    bottle_disp = read_bronze("fact_bottle_disposition_lot_cq_raw")
    cap_var = read_bronze("fact_cap_inspection_variable_cq_raw")
    cap_attr = read_bronze("fact_cap_attribute_inspection_cq_raw")
    cap_disp = read_bronze("fact_cap_disposition_lot_cq_raw")
    downtime = read_bronze("fact_downtime_raw")
    sales = read_bronze("fact_sales_raw")

    inspectors = sorted(read_bronze("fact_raw_material_inspection_raw")["Inspector"].unique().tolist())
    donor_sales_prices = sales.groupby("ProductFamily")["UnitPriceEUR"].apply(lambda s: s.astype(float).mean()).to_dict()

    print("Building dimension/catalog rows in memory (not written yet)...")
    dim_frames = {
        DIM / "dim_machine_profile.csv": build_dim_machine_profile_rows(),
        DIM / "dim_machine_setup.csv": build_dim_machine_setup_rows(),
        DIM / "dim_masterbatch.csv": build_dim_masterbatch_rows(),
        DIM / "dim_cap.csv": build_dim_cap_rows(),
        DIM / "dim_customer.csv": build_dim_customer_rows(),
        DIM / "dim_supplier.csv": build_dim_supplier_rows(),
        DIM / "dim_bottle_control_plan_cq.csv": build_dim_bottle_control_plan_rows(),
        DIM / "dim_cap_control_plan_cq.csv": build_dim_cap_control_plan_rows(),
        DIM / "dim_raw_material_control_plan.csv": build_dim_raw_material_control_plan_rows(),
    }

    print("Generating production & plan...")
    new_production, new_plan, donor_wo_to_new_wo, wo_info, batch_assign_all = gen_production_and_plan(production, plan)
    print(f"  production rows: {len(new_production)}, plan rows: {len(new_plan)}")

    def batch_lookup(machine, donor_batch):
        return batch_assign_all[(machine, donor_batch)]

    print("Generating process parameters...")
    new_pp = gen_process_parameters(process_parameters, donor_wo_to_new_wo, wo_info)

    print("Generating bottle QC (variables/attributes/disposition)...")
    new_bottle_var = gen_bottle_variables(bottle_var, donor_wo_to_new_wo, wo_info, batch_lookup)
    new_bottle_attr = gen_bottle_attributes(bottle_attr, donor_wo_to_new_wo, wo_info, batch_lookup)
    new_bottle_disp = gen_bottle_disposition(bottle_disp, donor_wo_to_new_wo, wo_info, batch_lookup)

    print("Generating cap QC (variables/attributes/disposition)...")
    new_cap_var = gen_cap_variables(cap_var, donor_wo_to_new_wo, wo_info, batch_lookup)
    new_cap_attr = gen_cap_attributes(cap_attr, donor_wo_to_new_wo, wo_info, batch_lookup, new_production)
    new_cap_disp = gen_cap_disposition(cap_disp, donor_wo_to_new_wo, wo_info, batch_lookup)

    print("Generating downtime (Storyline B on IM-007)...")
    new_downtime = gen_downtime(downtime)

    print("Generating incoming raw-material inspection/disposition (Storyline C)...")
    new_ri, new_rd = gen_raw_material(inspectors)

    print("Generating sales...")
    new_sales = gen_sales(new_production, donor_sales_prices)

    print("Generating narrative evidence rows (complaints/supplier complaints/NC/CAPA)...")
    new_cc, new_sc, new_nc, new_capa = gen_narrative_evidence_rows()

    print("All generation succeeded in memory. Now writing to disk...")
    print("Appending dimension/catalog rows...")
    for path, df in dim_frames.items():
        append_csv(path, df)

    print("Appending to bronze CSVs...")
    append_csv(BRONZE / "fact_production_raw.csv", new_production)
    append_csv(BRONZE / "fact_production_plan_raw.csv", new_plan)
    append_csv(BRONZE / "fact_process_parameters_raw.csv", new_pp)
    append_csv(BRONZE / "fact_bottle_inspection_variables_cq_raw.csv", new_bottle_var)
    append_csv(BRONZE / "fact_bottle_attribute_inspection_cq_raw.csv", new_bottle_attr)
    append_csv(BRONZE / "fact_bottle_disposition_lot_cq_raw.csv", new_bottle_disp)
    append_csv(BRONZE / "fact_cap_inspection_variable_cq_raw.csv", new_cap_var)
    append_csv(BRONZE / "fact_cap_attribute_inspection_cq_raw.csv", new_cap_attr)
    append_csv(BRONZE / "fact_cap_disposition_lot_cq_raw.csv", new_cap_disp)
    append_csv(BRONZE / "fact_downtime_raw.csv", new_downtime)
    append_csv(BRONZE / "fact_raw_material_inspection_raw.csv", new_ri)
    append_csv(BRONZE / "fact_raw_material_lot_disposition_raw.csv", new_rd)
    append_csv(BRONZE / "fact_sales_raw.csv", new_sales)
    append_csv(BRONZE / "fact_customer_complaints_raw.csv", new_cc)
    append_csv(BRONZE / "fact_supplier_complaints_raw.csv", new_sc)
    append_csv(BRONZE / "fact_nonconformance_raw.csv", new_nc)
    append_csv(BRONZE / "fact_capa_raw.csv", new_capa)

    print("\nVerifying additivity (old rows byte-identical, only new rows appended)...")
    ok = verify_additivity(snap)
    print("\nADDITIVITY CHECK:", "PASSED" if ok else "FAILED -- investigate before proceeding")
    return ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
