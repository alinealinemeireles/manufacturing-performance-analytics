"""
aql.py

ISO 2859-1 single sampling plans, normal inspection -- the two tables the project's attribute
inspections claim to follow (`Standard = ISO 2859-1`), so the data can be checked against the
standard instead of against itself:

- Table I: sample size code letter by lot size and general inspection level (I, II, III);
- Table II-A: sample size and acceptance/rejection numbers (Ac/Re) by code letter and AQL.

Only the AQL columns the control plans use (0.10, 0.65, 1.5 %) are transcribed. Where the table
has an arrow instead of a plan, the standard says to use the first plan below it (sample size
changes with it); `single_normal_plan` resolves the arrow and reports that it did.

Audit 2026-09-30 (decision D3): the committed data used the Ac/Re of the NEXT code letter (L /
AQL 0.65 -> Ac 5 instead of 3; L / 1.5 -> 10 instead of 7; M / 0.65 -> 7 instead of 5; M / 1.5 ->
14 instead of 10) -- plans one step more lenient than the standard, i.e. a higher consumer's risk.
"""
from __future__ import annotations

LETTERS = "ABCDEFGHJKLMNPQR"
SAMPLE_SIZE = dict(zip(LETTERS, [2, 3, 5, 8, 13, 20, 32, 50, 80, 125, 200, 315, 500, 800, 1250, 2000]))

# Table I -- upper lot-size bound of each row, and the code letter for levels I, II, III.
_TABLE_I = [
    (8, "AAB"), (15, "ABC"), (25, "BCD"), (50, "CDE"), (90, "CEF"), (150, "DFG"), (280, "EGH"),
    (500, "FHJ"), (1200, "GJK"), (3200, "HKL"), (10000, "JLM"), (35000, "KMN"), (150000, "LNP"),
    (500000, "MPQ"), (float("inf"), "NQR"),
]
LEVELS = ("I", "II", "III")

# Table II-A, single sampling, normal inspection: for each AQL, the letter carrying the first
# Ac=0/Re=1 plan (letters above it point DOWN to it) and the Ac of the following letters. Letters
# beyond the listed ones point UP to the last plan of the column.
_TABLE_II_A = {
    0.10: ("M", [0, 1, 2, 3, 5]),               # M 0/1, N 1/2, P 2/3, Q 3/4, R 5/6
    0.65: ("H", [0, 1, 2, 3, 5, 7, 10, 14, 21]),  # H 0/1 ... R 21/22
    1.5: ("F", [0, 1, 2, 3, 5, 7, 10, 14, 21]),   # F 0/1 ... P 21/22
}


def code_letter(lot_size: int, level: str = "II") -> str:
    """Table I: code letter for a lot size at a general inspection level."""
    column = LEVELS.index(level)
    for upper_bound, letters in _TABLE_I:
        if lot_size <= upper_bound:
            return letters[column]
    raise ValueError(lot_size)


def inspection_level_used(lot_size: int, letter: str) -> str | None:
    """Which general inspection level(s) a (lot size, code letter) pair corresponds to, e.g. "II",
    or None when the letter matches no general level for that lot size (a non-normative plan)."""
    matches = [level for level in LEVELS if code_letter(lot_size, level) == letter]
    return "/".join(matches) if matches else None


def single_normal_plan(letter: str, aql: float) -> tuple[int, int, int, bool]:
    """Table II-A: (sample size n, Ac, Re, arrow_followed) for a code letter and AQL.
    `arrow_followed` is True when the table points to another letter's plan -- then n is that
    letter's sample size, not the one the original letter would suggest."""
    first_letter, acceptance_numbers = _TABLE_II_A[round(float(aql), 2)]
    first = LETTERS.index(first_letter)
    last = first + len(acceptance_numbers) - 1
    position = LETTERS.index(letter)
    used = min(max(position, first), last)
    ac = acceptance_numbers[used - first]
    return SAMPLE_SIZE[LETTERS[used]], ac, ac + 1, used != position
