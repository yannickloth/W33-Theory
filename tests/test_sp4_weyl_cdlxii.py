"""Phase CDLXII — |Sp(4,3)| = |W(E₆)| = 51840 from graph invariants."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_sp4_weyl_bridge import build_sp4_weyl_summary

def test_phase_cdlxii_sp4_weyl_from_graph() -> None:
    t = build_sp4_weyl_summary()["sp4_weyl_theorem"]
    assert t["therefore_sp4_weyl_from_graph"] is True

def test_phase_cdlxii_over_T_delsarte() -> None:
    t = build_sp4_weyl_summary()["sp4_weyl_theorem"]
    assert t["over_T_is_delsarte_324"] is True
