"""Phase CDLXXI — Simplicial topology: f-vector (40,240,160,40), χ = −80."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_simplicial_topology_bridge import build_simplicial_topology_summary

def test_phase_cdlxxi_simplicial_consistent() -> None:
    t = build_simplicial_topology_summary()["simplicial_topology_theorem"]
    assert t["therefore_simplicial_topology_consistent"] is True

def test_phase_cdlxxi_palindromic() -> None:
    t = build_simplicial_topology_summary()["simplicial_topology_theorem"]
    assert t["f_vector_palindromic"] is True
