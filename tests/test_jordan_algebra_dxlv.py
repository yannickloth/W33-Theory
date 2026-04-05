"""Phase DXLV — Jordan: J₃(O)=27, F₄=52=v+k, E₆=78, E₇=133, Freudenthal=56."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_jordan_algebra_bridge import build_jordan_algebra_summary
def test_phase_dxlv():
    t = build_jordan_algebra_summary()["jordan_algebra_theorem"]
    assert t["therefore_jordan_verified"] is True
