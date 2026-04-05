"""Phase DLV — Dim reduction: SU(5)=f=24, SM=k=12, internal=36=Σexp."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_dimensional_reduction_bridge import build_dimensional_reduction_summary
def test_phase_dlv():
    t = build_dimensional_reduction_summary()["dimensional_reduction_theorem"]
    assert t["therefore_reduction_verified"] is True
