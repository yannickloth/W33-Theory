"""Phase DLXXVI — Dirac: √16=4, H=280=v+E, Witten=-5v, η=0."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_dirac_operator_bridge import build_dirac_operator_summary
def test_phase_dlxxvi():
    assert build_dirac_operator_summary()["dirac_operator_theorem"]["therefore_dirac_verified"]
