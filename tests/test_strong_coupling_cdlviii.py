"""Phase CDLVIII — Strong coupling α_s = λ/(k-1) = 2/11 from SRG."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_strong_coupling_bridge import build_strong_coupling_summary

def test_phase_cdlviii_strong_coupling_from_srg() -> None:
    t = build_strong_coupling_summary()["strong_coupling_theorem"]
    assert t["therefore_strong_coupling_from_srg"] is True

def test_phase_cdlviii_alpha_equals_2_over_11() -> None:
    t = build_strong_coupling_summary()["strong_coupling_theorem"]
    assert t["alpha_equals_lambda_over_nb"] is True
