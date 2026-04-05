"""Phase DVIII — Hadamard/Seidel: energy=240, s₀=g=15, |s₁|×|s₂|=35."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_hadamard_seidel_bridge import build_hadamard_seidel_summary

def test_phase_dviii_hadamard_seidel() -> None:
    t = build_hadamard_seidel_summary()["hadamard_seidel_theorem"]
    assert t["therefore_seidel_verified"] is True
