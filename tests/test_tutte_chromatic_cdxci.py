"""Phase CDXCI — Tutte/chromatic: ω=4, α=10, ωα=v, θ=ω (tight)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_tutte_chromatic_bridge import build_tutte_chromatic_summary

def test_phase_cdxci_tutte_chromatic() -> None:
    t = build_tutte_chromatic_summary()["tutte_chromatic_theorem"]
    assert t["therefore_tutte_tight"] is True
