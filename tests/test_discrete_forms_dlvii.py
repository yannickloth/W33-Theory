"""Phase DLVII — Discrete forms: χ=-v, β₁=201, β₂=T=160."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_discrete_forms_bridge import build_discrete_forms_summary
def test_phase_dlvii():
    t = build_discrete_forms_summary()["discrete_forms_theorem"]
    assert t["therefore_forms_verified"] is True
