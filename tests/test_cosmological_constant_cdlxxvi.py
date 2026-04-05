"""Phase CDLXXVI — Cosmological ratio T/E = 2/3, v² = 1600."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_cosmological_constant_bridge import build_cosmological_constant_summary

def test_phase_cdlxxvi_cosmological_scales() -> None:
    t = build_cosmological_constant_summary()["cosmological_theorem"]
    assert t["therefore_cosmological_scales_set"] is True
