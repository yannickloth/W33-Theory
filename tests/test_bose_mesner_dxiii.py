"""Phase DXIII — Bose-Mesner: dim=3, P-matrix verified, A²=kI+λA+μĀ."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_bose_mesner_bridge import build_bose_mesner_summary

def test_phase_dxiii_bose_mesner() -> None:
    t = build_bose_mesner_summary()["bose_mesner_theorem"]
    assert t["therefore_bose_mesner_verified"] is True
