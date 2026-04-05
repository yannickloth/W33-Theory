"""Phase CDLXIX — Q₈→E₆→Q₈ self-referential loop closes exactly."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_q8_e6_loop_bridge import build_q8_e6_loop_summary

def test_phase_cdlxix_loop_closes() -> None:
    t = build_q8_e6_loop_summary()["q8_e6_loop_theorem"]
    assert t["therefore_loop_closes"] is True

def test_phase_cdlxix_j3o_27() -> None:
    t = build_q8_e6_loop_summary()["q8_e6_loop_theorem"]
    assert t["j3o_dim_27"] is True

def test_phase_cdlxix_stab_2b1() -> None:
    t = build_q8_e6_loop_summary()["q8_e6_loop_theorem"]
    assert t["stab_over_q8_is_2b1"] is True
