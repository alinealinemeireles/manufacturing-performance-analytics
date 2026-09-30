"""
dataset_facts.py

Generates docs/dataset_facts.md -- the dataset's headline numbers (tables, rows, machines,
products, customers, suppliers, work orders, date window), computed from the committed
bronze CSVs and engineering dimensions instead of typed by hand into the README.

Why: the README once said "140 grupos" when the data had 190, and every portfolio expansion
changed several counts at once. A number that is generated cannot drift; a number that is
typed eventually does. tests/test_dataset_facts.py fails if docs/dataset_facts.md is stale
or if the README quotes a count that disagrees with it.

Run: python scripts/dataset_facts.py          (rewrites docs/dataset_facts.md)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BRONZE = ROOT / "datasets" / "bronze"
DIM = ROOT / "datasets" / "dim"
OUTPUT = ROOT / "docs" / "dataset_facts.md"
# Dimensions the notebook derives in Parte 2 from the cleaned facts (not shipped as files).
DERIVED_DIMENSIONS = ["dim_machine", "dim_mold", "dim_operator", "dim_bottle", "dim_ink"]


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def compute_facts() -> dict:
    fact_files = sorted(BRONZE.glob("fact_*_raw.csv"))
    dim_files = sorted(DIM.glob("dim_*.csv"))
    production = _read(BRONZE / "fact_production_raw.csv").drop_duplicates()
    production["Process"] = production["Process"].str.strip().str.title()
    dates = pd.to_datetime(production["Date"])
    machines = _read(DIM / "dim_machine_profile.csv")
    return {
        "fact_tables": len(fact_files),
        "dimension_files": len(dim_files),
        "dimensions_total": len({p.stem for p in dim_files} | set(DERIVED_DIMENSIONS)),
        "machines": machines["MachineId"].nunique(),
        "machines_by_process": production.groupby("Process")["MachineId"].nunique().to_dict(),
        "processes": production["Process"].nunique(),
        "work_orders": production["WorkOrder"].nunique(),
        "products_bottle_jar": _read(DIM / "dim_masterbatch.csv")["ProductId"].nunique(),
        "products_cap": _read(DIM / "dim_cap.csv")["CapId"].nunique(),
        "customers": _read(DIM / "dim_customer.csv")["CustomerId"].nunique(),
        "suppliers": _read(DIM / "dim_supplier.csv")["SupplierId"].nunique(),
        "production_start": dates.min().date().isoformat(),
        "production_end": dates.max().date().isoformat(),
        "rows_by_table": {p.stem: sum(1 for _ in open(p, encoding="utf-8-sig")) - 1 for p in fact_files},
    }


def render(facts: dict) -> str:
    lines = [
        "# Dataset facts (gerado automaticamente)",
        "",
        "> **Não editar à mão.** Gerado por `python scripts/dataset_facts.py` a partir de `datasets/bronze/` e",
        "> `datasets/dim/`. `tests/test_dataset_facts.py` falha se este arquivo ficar desatualizado ou se o",
        "> README citar uma contagem diferente destas.",
        "",
        "| Fato | Valor |",
        "|---|---|",
        f"| Tabelas fato brutas (bronze) | {facts['fact_tables']} |",
        f"| Dimensões (arquivos em `datasets/dim/` + derivadas na Parte 2) | {facts['dimensions_total']} "
        f"({facts['dimension_files']} arquivos + {facts['dimensions_total'] - facts['dimension_files']} derivadas) |",
        f"| Processos | {facts['processes']} |",
        f"| Máquinas | {facts['machines']} |",
        f"| Ordens de produção (únicas, bronze) | {facts['work_orders']:,} |",
        f"| Produtos — frascos/potes | {facts['products_bottle_jar']} |",
        f"| Produtos — tampas | {facts['products_cap']} |",
        f"| Clientes | {facts['customers']} |",
        f"| Fornecedores | {facts['suppliers']} |",
        f"| Janela de produção | {facts['production_start']} a {facts['production_end']} |",
        "",
        "## Máquinas por processo",
        "",
        "| Processo | Máquinas |",
        "|---|---|",
        *[f"| {process} | {n} |" for process, n in sorted(facts["machines_by_process"].items())],
        "",
        "## Linhas por tabela bronze",
        "",
        "| Tabela | Linhas (brutas, com duplicatas deliberadas) |",
        "|---|---|",
        *[f"| `{name}` | {rows:,} |" for name, rows in facts["rows_by_table"].items()],
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    OUTPUT.write_text(render(compute_facts()), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
