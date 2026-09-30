"""lib/aql.py against values read directly from ISO 2859-1 Tables I and II-A."""
import pytest

from lib import aql


@pytest.mark.parametrize("lot_size, level, letter", [
    (2951, "II", "K"), (2951, "III", "L"), (8000, "II", "L"), (12163, "II", "M"), (12163, "III", "N"),
    (46969, "II", "N"), (46969, "I", "L"), (203, "II", "G"), (500, "II", "H"), (501, "II", "J"),
])
def test_table_i_code_letters(lot_size, level, letter):
    assert aql.code_letter(lot_size, level) == letter


@pytest.mark.parametrize("letter, aql_value, plan", [
    ("L", 0.65, (200, 3, 4, False)), ("L", 1.5, (200, 7, 8, False)),
    ("M", 0.65, (315, 5, 6, False)), ("M", 1.5, (315, 10, 11, False)), ("M", 0.10, (315, 0, 1, False)),
    ("N", 0.10, (500, 1, 2, False)), ("N", 0.65, (500, 7, 8, False)), ("N", 1.5, (500, 14, 15, False)),
    ("H", 0.65, (50, 0, 1, False)), ("F", 1.5, (20, 0, 1, False)),
    ("L", 0.10, (315, 0, 1, True)),   # arrow down to M
    ("C", 0.65, (50, 0, 1, True)),    # arrow down to H
    ("R", 1.5, (800, 21, 22, True)),  # arrow up to P
])
def test_table_ii_a_single_normal(letter, aql_value, plan):
    assert aql.single_normal_plan(letter, aql_value) == plan


def test_inspection_level_used():
    assert aql.inspection_level_used(8000, "L") == "II"
    assert aql.inspection_level_used(2951, "L") == "III"
    assert aql.inspection_level_used(46969, "M") is None  # no general level gives M for 35 001-150 000
