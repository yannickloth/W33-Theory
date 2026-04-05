"""Phase CDLXXXVIII — Vertex propagator: G_vv(0) = -5/f = -5/24."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_vertex_propagator_bridge import build_vertex_propagator_summary

def test_phase_cdlxxxviii_propagator() -> None:
    t = build_vertex_propagator_summary()["vertex_propagator_theorem"]
    assert t["therefore_propagator_exact"] is True
