"""Phase CDLX — GQ(3,3) axiomatics: incidence, BN-pair, opposition."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_gq33_axiomatics_bridge import build_gq33_axiomatics_summary

def test_phase_cdlx_gq33_axioms_verified() -> None:
    t = build_gq33_axiomatics_summary()["gq33_axiomatics_theorem"]
    assert t["therefore_gq33_axioms_verified"] is True

def test_phase_cdlx_borel_324() -> None:
    t = build_gq33_axiomatics_summary()["gq33_axiomatics_theorem"]
    assert t["borel_order_324"] is True

def test_phase_cdlx_opposition_540() -> None:
    t = build_gq33_axiomatics_summary()["gq33_axiomatics_theorem"]
    assert t["opposition_540"] is True
