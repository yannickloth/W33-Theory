"""Phase CDLVII — Cabibbo/Weinberg angles from eigenvalue ratio."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_cabibbo_angle_bridge import build_cabibbo_angle_summary

def test_phase_cdlvii_mixing_angles_from_eigenvalue_ratio() -> None:
    t = build_cabibbo_angle_summary()["cabibbo_angle_theorem"]
    assert t["therefore_mixing_angles_from_eigenvalue_ratio"] is True

def test_phase_cdlvii_weinberg_30_degrees() -> None:
    t = build_cabibbo_angle_summary()["cabibbo_angle_theorem"]
    assert t["weinberg_angle_is_30_degrees"] is True

def test_phase_cdlvii_sin2_deviation_small() -> None:
    t = build_cabibbo_angle_summary()["cabibbo_angle_theorem"]
    assert t["sin2_deviation_under_9_percent"] is True
