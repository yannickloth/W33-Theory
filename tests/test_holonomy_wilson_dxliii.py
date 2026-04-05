"""Phase DXLIII — Holonomy: T=160, λ tri/edge, dim SU(3)=8, DOF/v=48=|GL(2,3)|."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_holonomy_wilson_bridge import build_holonomy_wilson_summary
def test_phase_dxliii():
    t = build_holonomy_wilson_summary()["holonomy_wilson_theorem"]
    assert t["therefore_holonomy_verified"] is True
