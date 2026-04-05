"""Phase DLI — Knot: Conf(G,2)=540=non-edges, skein r/s=-1/2."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_knot_invariants_bridge import build_knot_invariants_summary
def test_phase_dli():
    t = build_knot_invariants_summary()["knot_invariants_theorem"]
    assert t["therefore_knot_verified"] is True
