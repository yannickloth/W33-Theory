"""Phase CDLXXXIX — Parameter uniqueness: (40,12,2,4) unique from v=40, r=2, s=-4."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_parameter_uniqueness_bridge import build_parameter_uniqueness_summary

def test_phase_cdlxxxix_uniqueness() -> None:
    t = build_parameter_uniqueness_summary()["parameter_uniqueness_theorem"]
    assert t["therefore_parameters_unique"] is True
