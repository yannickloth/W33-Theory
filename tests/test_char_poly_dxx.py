"""Phase DXX — Char poly: χ=(x-12)(x-2)²⁴(x+4)¹⁵, min poly degree 3."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_char_poly_bridge import build_char_poly_summary

def test_phase_dxx_char_poly() -> None:
    t = build_char_poly_summary()["char_poly_theorem"]
    assert t["therefore_char_poly_verified"] is True
