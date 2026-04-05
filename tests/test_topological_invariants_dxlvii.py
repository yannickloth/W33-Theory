"""Phase DXLVII — Topology: χ₂=-v=-40, χ₃=-2v=-80, β₁=201, tet=v=40."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_topological_invariants_bridge import build_topological_invariants_summary
def test_phase_dxlvii():
    t = build_topological_invariants_summary()["topological_invariants_theorem"]
    assert t["therefore_topo_verified"] is True
