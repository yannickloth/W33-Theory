"""Phase DVI — Resistance distance: Kf=267/2, Σm/μ=267/80."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_resistance_distance_bridge import build_resistance_distance_summary

def test_phase_dvi_resistance() -> None:
    t = build_resistance_distance_summary()["resistance_distance_theorem"]
    assert t["therefore_resistance_verified"] is True
