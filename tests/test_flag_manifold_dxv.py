"""Phase DXV — Flag manifold: 160 flags=T, 1440 anti-flags, 36 pos roots."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_flag_manifold_bridge import build_flag_manifold_summary

def test_phase_dxv_flag_manifold() -> None:
    t = build_flag_manifold_summary()["flag_manifold_theorem"]
    assert t["therefore_flag_verified"] is True
