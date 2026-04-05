"""Phase DXLI — Matroid: rank=39=3×13, corank=201=3×67, regular."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_matroid_cycle_bridge import build_matroid_cycle_summary
def test_phase_dxli():
    t = build_matroid_cycle_summary()["matroid_cycle_theorem"]
    assert t["therefore_matroid_verified"] is True
