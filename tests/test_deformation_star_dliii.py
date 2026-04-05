"""Phase DLIII — Deformation: ℏ=1/12, sum=5/6, prod=-1/18."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_deformation_star_bridge import build_deformation_star_summary
def test_phase_dliii():
    t = build_deformation_star_summary()["deformation_star_theorem"]
    assert t["therefore_deformation_verified"] is True
