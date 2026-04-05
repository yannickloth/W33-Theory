"""Phase CDLXIV — Electroweak shells (8,12,12,8) palindromic, sum = v = 40."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_electroweak_shells_bridge import build_electroweak_shells_summary

def test_phase_cdlxiv_ew_shells_from_gq() -> None:
    t = build_electroweak_shells_summary()["electroweak_shells_theorem"]
    assert t["therefore_ew_shells_from_gq"] is True

def test_phase_cdlxiv_d2_e6_fundamental() -> None:
    t = build_electroweak_shells_summary()["electroweak_shells_theorem"]
    assert t["distance_d2_equals_27_e6_fund"] is True

def test_phase_cdlxiv_palindromic() -> None:
    t = build_electroweak_shells_summary()["electroweak_shells_theorem"]
    assert t["palindromic_symmetry"] is True
