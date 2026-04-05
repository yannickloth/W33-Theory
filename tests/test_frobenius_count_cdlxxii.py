"""Phase CDLXXII — q⁵−q = 240 = edge count, Frobenius field structure."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_frobenius_count_bridge import build_frobenius_count_summary

def test_phase_cdlxxii_frobenius_encodes_edges() -> None:
    t = build_frobenius_count_summary()["frobenius_count_theorem"]
    assert t["therefore_frobenius_encodes_edges"] is True

def test_phase_cdlxxii_two_s5() -> None:
    t = build_frobenius_count_summary()["frobenius_count_theorem"]
    assert t["two_s5_equals_240"] is True
