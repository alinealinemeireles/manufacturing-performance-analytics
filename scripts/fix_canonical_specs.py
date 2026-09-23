"""
fix_canonical_specs.py

Third fix-up pass, from a spec-accuracy audit: every new product's cloned QC
rows inherited whatever donor batch they were cloned from, so a SINGLE
ProductId ended up with a different LSL/Nominal/USL on almost every row (e.g.
FA-030-HDPE-FG-1000's "Weight" spec ranged from Nominal=11.5g to Nominal=135g
across its ~1000 rows). In the real, original data every SKU has exactly ONE
LSL/Nominal/USL per characteristic (verified: FR-007-PP-350's Weight Nominal
is 8.8g on every single row). This script assigns ONE realistic, engineered
spec per (ProductId, Characteristic) -- derived from real reference ratios in
the original data (weight/volume ratio for blow-molded bottles, weight range
already declared in dim_cap.csv for caps, thread size = neck/cap diameter,
overflow = +5% of nominal volume, etc.) -- and RESCALES every existing
measurement (M1..M10) to the new spec via a z-score-preserving affine
transform, so the storyline-driven deviations/spreads already baked into
those rows (Storylines C and D specifically) survive the correction exactly,
just expressed against the right absolute numbers. XBar/RangeR/StdDevS/
GroupResult are recomputed from the transformed measurements.

This is a targeted UPDATE of rows this expansion already added (filtered
strictly by the 17 new ProductId/CapId values) -- it verifies zero rows
outside that set are touched, so no Versão 00 original row is affected.

Run: python scripts/fix_canonical_specs.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_expansion_v01 as g  # noqa: E402

# (ProductId, Characteristic) -> (LSL, Nominal, USL, Unit)
BOTTLE_SPECS = {
    # FA-030 -- Frasco Alimentício Redondo, 1000 ml, thread 28/410
    ("FA-030-HDPE-FG-1000", "Weight"): (26.3, 28.0, 29.7, "g"),
    ("FA-030-PP-FG-1000", "Weight"): (26.3, 28.0, 29.7, "g"),
    ("FA-030-HDPE-FG-1000", "Height"): (147.8, 149.0, 150.2, "mm"),
    ("FA-030-PP-FG-1000", "Height"): (147.8, 149.0, 150.2, "mm"),
    ("FA-030-HDPE-FG-1000", "Neck Diameter"): (27.6, 28.0, 28.4, "mm"),
    ("FA-030-PP-FG-1000", "Neck Diameter"): (27.6, 28.0, 28.4, "mm"),
    ("FA-030-HDPE-FG-1000", "Thickness"): (0.5, 0.7, 0.9, "mm"),
    ("FA-030-PP-FG-1000", "Thickness"): (0.5, 0.7, 0.9, "mm"),
    ("FA-030-HDPE-FG-1000", "Overflow Volume"): (1030.0, 1050.0, 1070.0, "ml"),
    ("FA-030-PP-FG-1000", "Overflow Volume"): (1030.0, 1050.0, 1070.0, "ml"),
    # FA-031 -- Frasco Alimentício Oval, 500 ml, thread 28/410
    ("FA-031-HDPE-FG-500", "Weight"): (12.8, 13.6, 14.4, "g"),
    ("FA-031-PP-FG-500", "Weight"): (12.8, 13.6, 14.4, "g"),
    ("FA-031-HDPE-FG-500", "Height"): (119.8, 121.0, 122.2, "mm"),
    ("FA-031-PP-FG-500", "Height"): (119.8, 121.0, 122.2, "mm"),
    ("FA-031-HDPE-FG-500", "Neck Diameter"): (27.6, 28.0, 28.4, "mm"),
    ("FA-031-PP-FG-500", "Neck Diameter"): (27.6, 28.0, 28.4, "mm"),
    ("FA-031-HDPE-FG-500", "Thickness"): (0.5, 0.7, 0.9, "mm"),
    ("FA-031-PP-FG-500", "Thickness"): (0.5, 0.7, 0.9, "mm"),
    ("FA-031-HDPE-FG-500", "Overflow Volume"): (515.0, 525.0, 535.0, "ml"),
    ("FA-031-PP-FG-500", "Overflow Volume"): (515.0, 525.0, 535.0, "ml"),
    # FP-032 -- Frasco Farma Redondo, 100 ml, thread 24/410
    ("FP-032-PP-PG-100", "Weight"): (5.6, 6.0, 6.4, "g"),
    ("FP-032-PET-PG-100", "Weight"): (5.6, 6.0, 6.4, "g"),
    ("FP-032-PP-PG-100", "Height"): (77.0, 78.0, 79.0, "mm"),
    ("FP-032-PET-PG-100", "Height"): (77.0, 78.0, 79.0, "mm"),
    ("FP-032-PP-PG-100", "Neck Diameter"): (23.6, 24.0, 24.4, "mm"),
    ("FP-032-PET-PG-100", "Neck Diameter"): (23.6, 24.0, 24.4, "mm"),
    ("FP-032-PP-PG-100", "Thickness"): (0.6, 0.8, 1.0, "mm"),
    ("FP-032-PET-PG-100", "Thickness"): (0.6, 0.8, 1.0, "mm"),
    ("FP-032-PP-PG-100", "Overflow Volume"): (103.0, 105.0, 107.0, "ml"),
    ("FP-032-PET-PG-100", "Overflow Volume"): (103.0, 105.0, 107.0, "ml"),
    # FP-033 -- Frasco Farma Redondo, 250 ml, thread 24/410
    ("FP-033-PP-PG-250", "Weight"): (10.3, 11.0, 11.7, "g"),
    ("FP-033-PET-PG-250", "Weight"): (10.3, 11.0, 11.7, "g"),
    ("FP-033-PP-PG-250", "Height"): (117.0, 118.0, 119.0, "mm"),
    ("FP-033-PET-PG-250", "Height"): (117.0, 118.0, 119.0, "mm"),
    ("FP-033-PP-PG-250", "Neck Diameter"): (23.6, 24.0, 24.4, "mm"),
    ("FP-033-PET-PG-250", "Neck Diameter"): (23.6, 24.0, 24.4, "mm"),
    ("FP-033-PP-PG-250", "Thickness"): (0.6, 0.8, 1.0, "mm"),
    ("FP-033-PET-PG-250", "Thickness"): (0.6, 0.8, 1.0, "mm"),
    ("FP-033-PP-PG-250", "Overflow Volume"): (260.5, 262.5, 264.5, "ml"),
    ("FP-033-PET-PG-250", "Overflow Volume"): (260.5, 262.5, 264.5, "ml"),
    # PT-010 -- Pote Creme, 50 g, mouth matches TP-013 (70mm)
    ("PT-010-PP-050", "Weight"): (8.0, 10.0, 12.0, "g"),
    ("PT-010-PP-PG-050", "Weight"): (8.0, 10.0, 12.0, "g"),
    ("PT-010-PP-050", "Height"): (34.0, 36.0, 38.0, "mm"),
    ("PT-010-PP-PG-050", "Height"): (34.0, 36.0, 38.0, "mm"),
    ("PT-010-PP-050", "Mouth Diameter"): (69.5, 70.0, 70.5, "mm"),
    ("PT-010-PP-PG-050", "Mouth Diameter"): (69.5, 70.0, 70.5, "mm"),
    ("PT-010-PP-050", "Stack Load"): (15.0, 20.0, 25.0, "kgf"),
    ("PT-010-PP-PG-050", "Stack Load"): (15.0, 20.0, 25.0, "kgf"),
    # PT-011 -- Pote Creme, 100 g, mouth matches TP-013 (70mm)
    ("PT-011-PP-100", "Weight"): (15.0, 17.0, 19.0, "g"),
    ("PT-011-PP-PG-100", "Weight"): (15.0, 17.0, 19.0, "g"),
    ("PT-011-PP-100", "Height"): (48.0, 50.0, 52.0, "mm"),
    ("PT-011-PP-PG-100", "Height"): (48.0, 50.0, 52.0, "mm"),
    ("PT-011-PP-100", "Mouth Diameter"): (69.5, 70.0, 70.5, "mm"),
    ("PT-011-PP-PG-100", "Mouth Diameter"): (69.5, 70.0, 70.5, "mm"),
    ("PT-011-PP-100", "Stack Load"): (18.0, 24.0, 30.0, "kgf"),
    ("PT-011-PP-PG-100", "Stack Load"): (18.0, 24.0, 30.0, "kgf"),
}

# Cap specs: reuse dim_cap.csv's own MinWeightG/MaxWeightG/OuterDiameterMm/HeightMm
# (that file already carries one coherent spec per SKU) plus thread-matched Torque.
CAP_SPECS = {
    ("TE-012-PP-PG-24410", "Weight"): (9.5, 11.5, 13.5, "g"),
    ("TE-012-PP-PG-24410", "Height"): (21.5, 22.0, 22.5, "mm"),
    ("TE-012-PP-PG-24410", "Diameter"): (28.7, 29.0, 29.3, "mm"),
    ("TE-012-PP-PG-24410", "Torque"): (10.08, 14.0, 17.92, "N.cm"),
    ("TP-013-PP-070", "Weight"): (14.0, 16.5, 19.0, "g"),
    ("TP-013-PP-PG-070", "Weight"): (14.0, 16.5, 19.0, "g"),
    ("TP-013-PP-070", "Height"): (11.5, 12.0, 12.5, "mm"),
    ("TP-013-PP-PG-070", "Height"): (11.5, 12.0, 12.5, "mm"),
    ("TP-013-PP-070", "Diameter"): (69.5, 70.0, 70.5, "mm"),
    ("TP-013-PP-PG-070", "Diameter"): (69.5, 70.0, 70.5, "mm"),
    # TP-013 is a Snap Lid (no thread) -- "Torque" doesn't apply; renamed to
    # "Removal Force" (the real QC test for a snap-fit lid) as part of this fix.
    ("TP-013-PP-070", "Removal Force"): (1.5, 2.5, 3.5, "kgf"),
    ("TP-013-PP-PG-070", "Removal Force"): (1.5, 2.5, 3.5, "kgf"),
    ("TA-014-HDPE-FG-28410", "Weight"): (13.5, 15.9, 18.3, "g"),
    ("TA-014-PP-FG-28410", "Weight"): (13.5, 15.9, 18.3, "g"),
    ("TA-014-HDPE-FG-28410", "Height"): (19.5, 20.0, 20.5, "mm"),
    ("TA-014-PP-FG-28410", "Height"): (19.5, 20.0, 20.5, "mm"),
    ("TA-014-HDPE-FG-28410", "Diameter"): (32.7, 33.0, 33.3, "mm"),
    ("TA-014-PP-FG-28410", "Diameter"): (32.7, 33.0, 33.3, "mm"),
    ("TA-014-HDPE-FG-28410", "Torque"): (10.8, 15.0, 19.2, "N.cm"),
    ("TA-014-PP-FG-28410", "Torque"): (10.8, 15.0, 19.2, "N.cm"),
}
# TP-013 has no Diameter/Torque rows (Snap Lid, not screwed) and no Mouth Diameter --
# its "Diameter"-equivalent lives on the bottle side (PT- Mouth Diameter above).


def rescale_row(row, new_lsl, new_nom, new_usl, n_measurements):
    old_lsl, old_nom, old_usl = float(row["LSL"]), float(row["Nominal"]), float(row["USL"])
    old_half_range = max((old_usl - old_lsl) / 2.0, 1e-9)
    new_half_range = (new_usl - new_lsl) / 2.0
    ms = []
    for i in range(1, n_measurements + 1):
        old_m = float(row[f"M{i}"])
        z = (old_m - old_nom) / old_half_range
        new_m = new_nom + z * new_half_range
        ms.append(new_m)
    return ms


CHARACTERISTIC_RENAME = {
    # (ProductId, old_characteristic) -> new_characteristic
    ("TP-013-PP-070", "Torque"): "Removal Force",
    ("TP-013-PP-PG-070", "Torque"): "Removal Force",
}


def fix_table(path, id_col, specs, n_measurements):
    df = g.read_bronze(path.stem)
    new_ids = {pid for pid, _ch in specs}
    mask = df[id_col].isin(new_ids)
    touched = 0
    for idx in df.index[mask]:
        row = df.loc[idx]
        characteristic = row["Characteristic"]
        rename_key = (row[id_col], characteristic)
        if rename_key in CHARACTERISTIC_RENAME:
            characteristic = CHARACTERISTIC_RENAME[rename_key]
            df.at[idx, "Characteristic"] = characteristic
        key = (row[id_col], characteristic)
        if key not in specs:
            continue  # a characteristic we didn't spec (shouldn't happen, but stay safe)
        new_lsl, new_nom, new_usl, new_unit = specs[key]
        ms = rescale_row(row, new_lsl, new_nom, new_usl, n_measurements)
        for i, m in enumerate(ms, start=1):
            df.at[idx, f"M{i}"] = str(round(m, 3))
        xbar = sum(ms) / len(ms)
        rng_r = max(ms) - min(ms)
        std_s = float(np.std(ms, ddof=1)) if len(ms) > 1 else 0.0
        conforming = all(new_lsl <= m <= new_usl for m in ms)
        df.at[idx, "LSL"] = str(new_lsl)
        df.at[idx, "Nominal"] = str(new_nom)
        df.at[idx, "USL"] = str(new_usl)
        df.at[idx, "Unit"] = str(new_unit)
        df.at[idx, "XBar"] = str(round(xbar, 3))
        df.at[idx, "RangeR"] = str(round(rng_r, 3))
        df.at[idx, "StdDevS"] = str(round(std_s, 3))
        df.at[idx, "GroupResult"] = "Conforming" if conforming else "Nonconforming"
        touched += 1
    return df, touched, new_ids


def main():
    bottle_path = g.BRONZE / "fact_bottle_inspection_variables_cq_raw.csv"
    cap_path = g.BRONZE / "fact_cap_inspection_variable_cq_raw.csv"

    print("Snapshotting current files...")
    snap = g.snapshot([bottle_path, cap_path])
    b = snap[bottle_path]
    old_bottle_bytes = bottle_path.read_bytes()
    old_cap_bytes = cap_path.read_bytes()

    print("Fixing bottle variable specs (Weight/Height/Neck Diameter/Thickness/Overflow Volume/Mouth Diameter/Stack Load)...")
    bottle_df, n_bottle, bottle_ids = fix_table(bottle_path, "BottleId", BOTTLE_SPECS, 5)
    print(f"  rows corrected: {n_bottle}")

    print("Fixing cap variable specs (Weight/Height/Diameter/Torque)...")
    cap_df, n_cap, cap_ids = fix_table(cap_path, "CapId", CAP_SPECS, 10)
    print(f"  rows corrected: {n_cap}")

    print("\nVerifying only the 17 new SKUs were touched (diffing full old vs new content)...")
    import io
    old_bottle_df = pd.read_csv(io.BytesIO(old_bottle_bytes), encoding="utf-8-sig", dtype=str, keep_default_na=False)
    changed_bottle_rows = (old_bottle_df.astype(str).values != bottle_df.astype(str).values).any(axis=1)
    changed_bottle_ids = set(bottle_df.loc[changed_bottle_rows, "BottleId"].unique())
    assert changed_bottle_ids <= bottle_ids, f"Touched rows outside the new-SKU set! {changed_bottle_ids - bottle_ids}"
    print(f"  bottle: {changed_bottle_rows.sum()} rows changed, all within {sorted(changed_bottle_ids)}")

    old_cap_df = pd.read_csv(io.BytesIO(old_cap_bytes), encoding="utf-8-sig", dtype=str, keep_default_na=False)
    changed_cap_rows = (old_cap_df.astype(str).values != cap_df.astype(str).values).any(axis=1)
    changed_cap_ids = set(cap_df.loc[changed_cap_rows, "CapId"].unique())
    assert changed_cap_ids <= cap_ids, f"Touched rows outside the new-SKU set! {changed_cap_ids - cap_ids}"
    print(f"  cap: {changed_cap_rows.sum()} rows changed, all within {sorted(changed_cap_ids)}")

    print("\nWriting corrected files (full rewrite, in place)...")
    bottle_df.to_csv(bottle_path, index=False, lineterminator="\n", encoding="utf-8-sig")
    cap_df.to_csv(cap_path, index=False, lineterminator="\n", encoding="utf-8-sig")

    print("\nSpot check -- Nominal now constant per SKU:")
    check = pd.read_csv(bottle_path, encoding="utf-8-sig")
    print(check[check.BottleId == "FA-030-HDPE-FG-1000"][check.Characteristic == "Weight"].Nominal.unique()
          if False else check[(check.BottleId == "FA-030-HDPE-FG-1000") & (check.Characteristic == "Weight")].Nominal.unique())

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
