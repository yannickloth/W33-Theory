"""Phase DXXVII — SUSY: f-g=q²=9, Witten=α=10, f²-g²=351=C(27,2)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_susy_balance_bridge import build_susy_balance_summary

def test_phase_dxxvii_susy() -> None:
    t = build_susy_balance_summary()["susy_balance_theorem"]
    assert t["therefore_susy_encoded"] is True
