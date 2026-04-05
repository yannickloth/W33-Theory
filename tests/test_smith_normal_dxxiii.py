"""Phase DXXIII — Smith normal: det(A) = -3×2⁵⁶, ν₂=56, ν₃=1."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_smith_normal_bridge import build_smith_normal_summary

def test_phase_dxxiii_smith() -> None:
    t = build_smith_normal_summary()["smith_normal_theorem"]
    assert t["therefore_smith_verified"] is True
