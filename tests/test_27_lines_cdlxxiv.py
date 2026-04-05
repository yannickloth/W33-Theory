"""Phase CDLXXIV — 27 non-neighbors = q³ = dim(E₆ fund)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_27_lines_bridge import build_27_lines_summary

def test_phase_cdlxxiv_27_lines_from_gq() -> None:
    t = build_27_lines_summary()["27_lines_theorem"]
    assert t["therefore_27_lines_from_gq"] is True

def test_phase_cdlxxiv_internal_degree_8() -> None:
    t = build_27_lines_summary()["27_lines_theorem"]
    assert t["internal_degree_8"] is True
