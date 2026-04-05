"""Phase CDLIII — complement duality: energy ratio = curvature sum = 5/6."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_complement_duality_bridge import build_complement_duality_summary

def test_phase_cdliii_complement_encodes_curvature_and_cp() -> None:
    t = build_complement_duality_summary()["complement_duality_theorem"]
    assert t["therefore_complement_duality_encodes_curvature_and_cp"] is True

def test_phase_cdliii_energy_ratio_5_6() -> None:
    t = build_complement_duality_summary()["complement_duality_theorem"]
    assert t["ratio_equals_5_over_6_equals_curvature_sum"] is True

def test_phase_cdliii_balanced_spectrum() -> None:
    t = build_complement_duality_summary()["complement_duality_theorem"]
    assert t["complement_spectrum_balanced"] is True
