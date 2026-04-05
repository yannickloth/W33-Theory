"""Phase CDLXX — 480-operator algebra: 240⊕240 split, centralizer dim = 3."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_480_operator_algebra_bridge import build_480_operator_algebra_summary

def test_phase_cdlxx_480_algebra_structured() -> None:
    t = build_480_operator_algebra_summary()["480_operator_algebra_theorem"]
    assert t["therefore_480_algebra_structured"] is True

def test_phase_cdlxx_centralizer_3() -> None:
    t = build_480_operator_algebra_summary()["480_operator_algebra_theorem"]
    assert t["centralizer_dim_3"] is True
