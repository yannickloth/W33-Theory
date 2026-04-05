"""Phase DIX — Interlacing: Cauchy, Hoffman χ≥4, inertia bound α≤v-g."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_interlacing_bridge import build_interlacing_summary

def test_phase_dix_interlacing() -> None:
    t = build_interlacing_summary()["interlacing_theorem"]
    assert t["therefore_interlacing_verified"] is True
