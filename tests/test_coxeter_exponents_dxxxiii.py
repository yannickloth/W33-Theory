"""Phase DXXXIII — Coxeter: h=k=12, exp_sum=36=v-μ, ∏(e+1)=51840=|W(E₆)|."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_coxeter_exponents_bridge import build_coxeter_exponents_summary
def test_phase_dxxxiii():
    t = build_coxeter_exponents_summary()["coxeter_exponents_theorem"]
    assert t["therefore_coxeter_verified"] is True
