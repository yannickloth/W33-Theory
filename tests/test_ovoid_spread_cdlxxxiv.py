"""Phase CDLXXXIV — Ovoid α=10, Hoffman tight, 4 spreads partition V."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_ovoid_spread_bridge import build_ovoid_spread_summary

def test_phase_cdlxxxiv_ovoid_spread() -> None:
    t = build_ovoid_spread_summary()["ovoid_spread_theorem"]
    assert t["therefore_ovoid_spread_consistent"] is True
