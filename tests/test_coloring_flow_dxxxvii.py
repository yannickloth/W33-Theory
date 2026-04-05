"""Phase DXXXVII — Coloring/flow: χ=4, cycle_rank=201=3×67, NZ 5-flow."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_coloring_flow_bridge import build_coloring_flow_summary
def test_phase_dxxxvii():
    t = build_coloring_flow_summary()["coloring_flow_theorem"]
    assert t["therefore_coloring_flow_verified"] is True
