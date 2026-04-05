"""Phase DLIV — Twistor: CP³ dim=6=rank E₆, photon→s=-4, scalar→-r=-2."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_twistor_geometry_bridge import build_twistor_geometry_summary
def test_phase_dliv():
    t = build_twistor_geometry_summary()["twistor_geometry_theorem"]
    assert t["therefore_twistor_verified"] is True
