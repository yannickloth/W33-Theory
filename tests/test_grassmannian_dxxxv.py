"""Phase DXXXV — Grassmannian: Plücker=6, Gr dim=μ=4, 40/130=4/13=μ/Φ₃."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_grassmannian_bridge import build_grassmannian_summary
def test_phase_dxxxv():
    t = build_grassmannian_summary()["grassmannian_theorem"]
    assert t["therefore_grassmannian_verified"] is True
