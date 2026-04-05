"""Phase DII — Signless Laplacian: Q eigenvalues 24,14,8; trace=vk."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_signless_laplacian_bridge import build_signless_laplacian_summary

def test_phase_dii_signless_laplacian() -> None:
    t = build_signless_laplacian_summary()["signless_laplacian_theorem"]
    assert t["therefore_signless_verified"] is True
