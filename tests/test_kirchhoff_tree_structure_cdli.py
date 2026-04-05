"""Phase CDLI — Kirchhoff tree 2-adic/5-adic structure: τ = 2⁸¹ · 5²³."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_kirchhoff_tree_structure_bridge import build_kirchhoff_tree_structure_summary

def test_phase_cdli_tau_equals_2_81_times_5_23() -> None:
    t = build_kirchhoff_tree_structure_summary()["kirchhoff_tree_structure_theorem"]
    assert t["therefore_tau_equals_2_to_81_times_5_to_23"] is True

def test_phase_cdli_2_adic_equals_b1() -> None:
    t = build_kirchhoff_tree_structure_summary()["kirchhoff_tree_structure_theorem"]
    assert t["the_2_adic_valuation_equals_b1_equals_81"] is True

def test_phase_cdli_5_adic_equals_f_minus_1() -> None:
    t = build_kirchhoff_tree_structure_summary()["kirchhoff_tree_structure_theorem"]
    assert t["the_5_adic_valuation_equals_f_minus_1_equals_23"] is True
