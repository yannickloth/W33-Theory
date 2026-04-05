"""Phase DXVIII — Symplectic: |Sp(4,3)|=51840=|W(E₆)|, v=(q+1)(q²+1)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_symplectic_structure_bridge import build_symplectic_structure_summary

def test_phase_dxviii_symplectic() -> None:
    t = build_symplectic_structure_summary()["symplectic_structure_theorem"]
    assert t["therefore_symplectic_verified"] is True
