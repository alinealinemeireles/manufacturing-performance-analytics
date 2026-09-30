"""Documentation drift tests: generated facts must be current, and the README must agree with them."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import dataset_facts  # noqa: E402

FACTS = dataset_facts.compute_facts()
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_generated_facts_file_is_up_to_date():
    committed = (ROOT / "docs" / "dataset_facts.md").read_text(encoding="utf-8")
    assert committed == dataset_facts.render(FACTS), "rode: python scripts/dataset_facts.py"


def test_readme_machine_and_table_counts_match_the_data():
    assert f"{FACTS['machines']} máquinas" in README
    assert f"{FACTS['fact_tables']} tabelas fato brutas" in README
    assert f"{FACTS['dimensions_total']} dimensões" in README
    assert f"{FACTS['processes']} processos" in README


def test_readme_period_matches_the_data():
    assert f"{FACTS['production_start']} a {FACTS['production_end']}" in README


def test_readme_does_not_quote_a_stale_machine_count():
    quoted = {int(n) for n in re.findall(r"(\d+) máquinas", README)}
    # 18 (original Versão 00 fleet) and 4 (expansion) are quoted on purpose as history.
    assert quoted <= {FACTS["machines"], 18, 4}
