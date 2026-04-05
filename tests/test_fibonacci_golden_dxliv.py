"""Phase DXLIV — Fibonacci: f/g=8/5=F₆/F₅, f=qF₆, g=qF₅, k-1=L₅=11."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_fibonacci_golden_bridge import build_fibonacci_golden_summary
def test_phase_dxliv():
    t = build_fibonacci_golden_summary()["fibonacci_golden_theorem"]
    assert t["therefore_fibonacci_verified"] is True
