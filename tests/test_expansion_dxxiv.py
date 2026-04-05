"""Phase DXXIV — Expansion: spectral gap=10, Cheeger≥5, min-cut≥100."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_expansion_bridge import build_expansion_summary

def test_phase_dxxiv_expansion() -> None:
    t = build_expansion_summary()["expansion_theorem"]
    assert t["therefore_expansion_verified"] is True
