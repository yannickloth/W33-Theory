"""Phase DLIX — Modular q-series: a₃=960=6T, poles product=-1/96."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_modular_qseries_bridge import build_modular_qseries_summary
def test_phase_dlix():
    t = build_modular_qseries_summary()["modular_qseries_theorem"]
    assert t["therefore_qseries_verified"] is True
