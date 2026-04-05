"""Phase DIII — Normalized Laplacian: gap=5/6, nl₂=4/3, frustrated."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_normalized_laplacian_bridge import build_normalized_laplacian_summary

def test_phase_diii_normalized_laplacian() -> None:
    t = build_normalized_laplacian_summary()["normalized_laplacian_theorem"]
    assert t["therefore_normalized_verified"] is True
