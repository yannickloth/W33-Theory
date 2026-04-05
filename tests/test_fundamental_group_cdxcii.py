"""Phase CDXCII — Fundamental group: β₁=201=3×67, E-V=v(k-2)/2=200."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_fundamental_group_bridge import build_fundamental_group_summary

def test_phase_cdxcii_fundamental_group() -> None:
    t = build_fundamental_group_summary()["fundamental_group_theorem"]
    assert t["therefore_topology_consistent"] is True
