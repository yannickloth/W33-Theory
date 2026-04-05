"""Phase DXI — Ihara det: cycle rank=200, Δ₂=-v, Δ₃=-(v-k)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_ihara_det_bridge import build_ihara_det_summary

def test_phase_dxi_ihara_det() -> None:
    t = build_ihara_det_summary()["ihara_det_theorem"]
    assert t["therefore_ihara_det_verified"] is True
