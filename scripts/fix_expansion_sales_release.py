"""
fix_expansion_sales_release.py

Fourth fix-up pass on the portfolio expansion (generate_expansion_v01.py), found by
the 2026-09-29 audit when the new data contract (contracts/data_contract.yaml) was
first run against silver. `gen_sales` in the expansion generator created a sales
order for ~55% of the new machines' work orders WITHOUT looking at the lot
disposition, which broke three product-release rules the original Versão 00 data
respects 100%:

1. **Rejected lots shipped** -- 30 expansion work orders with
   `FinalLotDecision = Rejected` ("Rejected - Segregated") had a sales order.
   A segregated lot cannot be released to a customer (ISO 9001 8.6 / 8.7).
2. **Shipped before the lot decision** -- `Date` was set to the production date
   itself, so 294 of 315 inspected expansion lots "shipped" before QC released
   them. In Versão 00 the gap production -> shipment is 1-12 days (median 7) and
   no lot ships before its decision.
3. **LotId prefix did not match production** -- the shift digit was hard-coded to 2,
   so only 209 of 591 expansion sales rows carried the same 14-character LotId prefix
   as the work order they came from (Versão 00: 8007 of 8007).

The fix, restricted to the expansion's own sales rows (MachineId in the 4 new
machines -- verified that no Versão 00 row is touched):
- drop every sales row whose work order has a Rejected lot decision;
- ship date = max(production date + lag, lot decision date + 1 day), where the lag is
  drawn from the empirical Versão 00 production->shipment lag distribution;
- drop rows whose corrected ship date falls after the dataset window (2026-12-30),
  the same "not every lot ships inside the sample window" rule gen_sales already used;
- rebuild the 14-character LotId prefix from the order's real shift (suffix kept).

Run: python scripts/fix_expansion_sales_release.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.etl_lib import build_lotid_prefix, compute_shift_number  # noqa: E402

BRONZE = ROOT / "datasets" / "bronze"
NEW_MACHINES = {"IM-007", "IM-008", "ISBM-009", "ISBM-010"}
WINDOW_END = pd.Timestamp("2026-12-30")
RNG = np.random.default_rng(20260929)


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(BRONZE / f"{name}.csv", encoding="utf-8-sig", dtype={"LotId": str})


def main() -> None:
    sales = read("fact_sales_raw")
    production = read("fact_production_raw").drop_duplicates("WorkOrder")
    production["Process"] = production["Process"].str.strip().str.title()
    production["_date"] = pd.to_datetime(production["Date"])

    dispositions = pd.concat([
        read(name)[["WorkOrder", "FinalLotDecision", "LotDecisionDateTime"]]
        for name in ("fact_bottle_disposition_lot_cq_raw", "fact_cap_disposition_lot_cq_raw",
                     "fact_ink_disposition_lot_cq_raw")
    ], ignore_index=True)
    dispositions["FinalLotDecision"] = dispositions["FinalLotDecision"].astype(str).str.strip().str.title()
    dispositions["_decision_dt"] = pd.to_datetime(dispositions["LotDecisionDateTime"], format="mixed", errors="coerce")
    rejected_orders = set(dispositions.loc[dispositions["FinalLotDecision"] == "Rejected", "WorkOrder"])
    decision_date = dispositions.groupby("WorkOrder")["_decision_dt"].max().dt.normalize()

    is_expansion = sales["MachineId"].isin(NEW_MACHINES)
    original = sales.loc[~is_expansion]
    expansion = sales.loc[is_expansion].copy()
    print(f"Sales rows: {len(sales):,} total, {len(expansion):,} from the expansion machines")

    # Empirical Versão 00 production -> shipment lag, in days.
    original_lag = (pd.to_datetime(original["Date"])
                    - original["WorkOrder"].map(production.set_index("WorkOrder")["_date"])).dt.days.dropna()
    assert original_lag.min() >= 1, "Versão 00 should never ship on the production day"

    n_rejected = expansion["WorkOrder"].isin(rejected_orders).sum()
    expansion = expansion.loc[~expansion["WorkOrder"].isin(rejected_orders)].copy()

    prod_info = production.set_index("WorkOrder")
    prod_date = expansion["WorkOrder"].map(prod_info["_date"])
    lag_days = RNG.choice(original_lag.to_numpy(), size=len(expansion))
    earliest_by_lag = prod_date + pd.to_timedelta(lag_days, unit="D")
    earliest_by_release = expansion["WorkOrder"].map(decision_date) + pd.Timedelta(days=1)
    ship_date = pd.concat([earliest_by_lag, earliest_by_release], axis=1).max(axis=1)
    inside_window = ship_date <= WINDOW_END
    n_outside = int((~inside_window).sum())
    expansion = expansion.loc[inside_window].copy()
    expansion["Date"] = ship_date.loc[inside_window].dt.strftime("%Y-%m-%d")

    order_rows = prod_info.loc[expansion["WorkOrder"]].reset_index()
    shift = compute_shift_number(order_rows["StartTime"])
    prefix = build_lotid_prefix(order_rows["_date"], shift, order_rows["Process"],
                                order_rows["MachineId"], order_rows["WorkOrder"])
    expansion["LotId"] = prefix.to_numpy() + expansion["LotId"].str[-2:].to_numpy()

    fixed = pd.concat([original, expansion], ignore_index=True)
    fixed = fixed.sort_values("SalesOrderId", key=lambda s: s.str.extract(r"(\d+)")[0].astype(int)).reset_index(drop=True)
    assert fixed.loc[~fixed["MachineId"].isin(NEW_MACHINES)].sort_values("SalesOrderId").reset_index(drop=True).equals(
        original.sort_values("SalesOrderId").reset_index(drop=True)), "a Versão 00 row changed"

    fixed.to_csv(BRONZE / "fact_sales_raw.csv", index=False, encoding="utf-8-sig")
    print(f"Removed {n_rejected} rejected-lot sales rows and {n_outside} rows shipping after {WINDOW_END.date()}")
    print(f"Re-dated {len(expansion):,} expansion sales rows; fact_sales_raw.csv now has {len(fixed):,} rows")


if __name__ == "__main__":
    main()
