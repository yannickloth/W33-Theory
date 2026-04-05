"""Phase DXXV — Graph energy: E=120, E/v=q=3, E/|edges|=1/2."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_graph_energy_bridge import build_graph_energy_summary

def test_phase_dxxv_energy() -> None:
    t = build_graph_energy_summary()["graph_energy_theorem"]
    assert t["therefore_energy_verified"] is True
