"""Phase CDXCVI — Weyl: 27=v-k-1, 78=2(v-1), C(27,2)=351, C(27,3)=2925, E₈=248."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_weyl_formula_bridge import build_weyl_formula_summary

def test_phase_cdxcvi_weyl_formula() -> None:
    t = build_weyl_formula_summary()["weyl_formula_theorem"]
    assert t["therefore_weyl_encoded"] is True
