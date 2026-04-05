"""Phase CDLXVI — Three generations from 7 independent routes, all = 3."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_three_generations_bridge import build_three_generations_summary

def test_phase_cdlxvi_3_gen_from_7_routes() -> None:
    t = build_three_generations_summary()["three_generations_theorem"]
    assert t["therefore_3_generations_from_7_routes"] is True

def test_phase_cdlxvi_eigenvalue_gap() -> None:
    t = build_three_generations_summary()["three_generations_theorem"]
    assert t["eigenvalue_gap_gives_3"] is True

def test_phase_cdlxvi_b1_gen4() -> None:
    t = build_three_generations_summary()["three_generations_theorem"]
    assert t["b1_is_gen_to_4"] is True
