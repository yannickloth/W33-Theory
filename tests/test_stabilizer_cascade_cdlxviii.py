"""Phase CDLXVIII — Stabilizer cascade W(E₆)→…→N, indices 27, 5/3, 3, 2."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_stabilizer_cascade_bridge import build_stabilizer_cascade_summary

def test_phase_cdlxviii_cascade_verified() -> None:
    t = build_stabilizer_cascade_summary()["stabilizer_cascade_theorem"]
    assert t["therefore_cascade_verified"] is True

def test_phase_cdlxviii_total_270() -> None:
    t = build_stabilizer_cascade_summary()["stabilizer_cascade_theorem"]
    assert t["total_270"] is True

def test_phase_cdlxviii_n192_aut() -> None:
    t = build_stabilizer_cascade_summary()["stabilizer_cascade_theorem"]
    assert t["n192_is_aut_c2_q8"] is True
