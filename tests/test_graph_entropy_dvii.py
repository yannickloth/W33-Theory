"""Phase DVII — Graph entropy: S_vN ≈ 5.25 bits, near-maximal (99.3%)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_graph_entropy_bridge import build_graph_entropy_summary

def test_phase_dvii_entropy() -> None:
    t = build_graph_entropy_summary()["graph_entropy_theorem"]
    assert t["therefore_entropy_verified"] is True
