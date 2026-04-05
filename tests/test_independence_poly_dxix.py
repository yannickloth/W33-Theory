"""Phase DXIX — Independence poly: i₂=540, α=10, χ_f=4."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_independence_poly_bridge import build_independence_poly_summary

def test_phase_dxix_independence() -> None:
    t = build_independence_poly_summary()["independence_poly_theorem"]
    assert t["therefore_independence_verified"] is True
