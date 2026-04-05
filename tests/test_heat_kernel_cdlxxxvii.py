"""Phase CDLXXXVII — Heat kernel: tr(A⁰)=v, tr(A¹)=0, tr(A²)=2E, tr(A³)=6T."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_heat_kernel_bridge import build_heat_kernel_summary

def test_phase_cdlxxxvii_heat_kernel() -> None:
    t = build_heat_kernel_summary()["heat_kernel_theorem"]
    assert t["therefore_heat_kernel_consistent"] is True
