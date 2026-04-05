"""Phase DLXV — Tropical: radius=k, rank=3, canonical=10v=400."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_tropical_geometry_bridge import build_tropical_geometry_summary
def test_phase_dlxv():
    assert build_tropical_geometry_summary()["tropical_geometry_theorem"]["therefore_tropical_verified"]
