"""Phase DXXXIV — Conway: 51840|Co.0, 196560/48=4095=2¹²-1."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_conway_lattice_bridge import build_conway_lattice_summary
def test_phase_dxxxiv():
    t = build_conway_lattice_summary()["conway_lattice_theorem"]
    assert t["therefore_conway_linked"] is True
