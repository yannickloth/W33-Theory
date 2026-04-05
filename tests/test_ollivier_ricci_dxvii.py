"""Phase DXVII — Ollivier-Ricci: κ=1/3, scalar curvature=T=160."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_ollivier_ricci_bridge import build_ollivier_ricci_summary

def test_phase_dxvii_ricci() -> None:
    t = build_ollivier_ricci_summary()["ollivier_ricci_theorem"]
    assert t["therefore_ricci_verified"] is True
