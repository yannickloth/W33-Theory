"""Phase DI — Laplacian: eigenvalues 0,10,16; trace=vk; Fiedler=10."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_laplacian_spectrum_bridge import build_laplacian_spectrum_summary

def test_phase_di_laplacian() -> None:
    t = build_laplacian_spectrum_summary()["laplacian_spectrum_theorem"]
    assert t["therefore_laplacian_verified"] is True
