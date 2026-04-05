"""Phase DXXX — Quantum walk: integer eigenvalues, all even, gcd=2, phases (1,-1,1)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_quantum_walk_bridge import build_quantum_walk_summary

def test_phase_dxxx_quantum_walk() -> None:
    t = build_quantum_walk_summary()["quantum_walk_theorem"]
    assert t["therefore_quantum_walk_verified"] is True
