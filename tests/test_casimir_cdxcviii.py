"""Phase CDXCVIII — Casimir: C₂(SU3)=μ/q=4/3, C₂(SU2)=q/μ=3/4, product=1."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_casimir_bridge import build_casimir_summary

def test_phase_cdxcviii_casimir() -> None:
    t = build_casimir_summary()["casimir_theorem"]
    assert t["therefore_casimir_encoded"] is True
