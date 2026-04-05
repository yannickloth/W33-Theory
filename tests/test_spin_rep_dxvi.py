"""Phase DXVI — Spin rep: SO(10)→s²=16, triality→f=24, 27=16+10+1."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_spin_rep_bridge import build_spin_rep_summary

def test_phase_dxvi_spin_rep() -> None:
    t = build_spin_rep_summary()["spin_rep_theorem"]
    assert t["therefore_spin_encoded"] is True
