"""Phase DXXII — Duality: self-dual GQ, 160 incidences, ovoid=10."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_duality_bridge import build_duality_summary

def test_phase_dxxii_duality() -> None:
    t = build_duality_summary()["duality_theorem"]
    assert t["therefore_duality_verified"] is True
