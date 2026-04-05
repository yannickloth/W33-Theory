"""Phase DXXXIX — Vertex algebra: c=6=rank, Z(E₆)=3=q, c'=26=bosonic dim."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_vertex_algebra_bridge import build_vertex_algebra_summary
def test_phase_dxxxix():
    t = build_vertex_algebra_summary()["vertex_algebra_theorem"]
    assert t["therefore_vertex_algebra_verified"] is True
