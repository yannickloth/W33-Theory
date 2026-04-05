"""Phase CDLVI — Selection principle: only q=3 passes all 5 conditions."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_selection_principle_bridge import build_selection_principle_summary

def test_phase_cdlvi_only_q3_passes() -> None:
    t = build_selection_principle_summary()["selection_principle_theorem"]
    assert t["only_q3_passes_all_five"] is True

def test_phase_cdlvi_q3_unique() -> None:
    t = build_selection_principle_summary()["selection_principle_theorem"]
    assert t["therefore_q3_unique"] is True
