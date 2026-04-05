"""Phase DLXVI — Calabi-Yau: h¹¹=f=24, χ=v/2=20, h¹¹+h²¹=v-2, mirror."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_calabi_yau_bridge import build_calabi_yau_summary
def test_phase_dlxvi():
    assert build_calabi_yau_summary()["calabi_yau_theorem"]["therefore_cy_verified"]
