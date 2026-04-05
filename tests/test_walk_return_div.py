"""Phase DIV — Walk return: p₀=1, p₁=0, p₂=1/k=1/12."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_walk_return_bridge import build_walk_return_summary

def test_phase_div_walk_return() -> None:
    t = build_walk_return_summary()["walk_return_theorem"]
    assert t["therefore_walk_exact"] is True
