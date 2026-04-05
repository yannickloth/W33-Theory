"""Phase DXXIX — Tensor decomp: Sym²(24)=300, Alt²(24)=276, f⊗g=360."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_tensor_decomp_bridge import build_tensor_decomp_summary

def test_phase_dxxix_tensor() -> None:
    t = build_tensor_decomp_summary()["tensor_decomp_theorem"]
    assert t["therefore_tensor_verified"] is True
