"""Phase DLXIV — Hopf: Σsimplices=480=vk, flag orbit=480."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_hopf_algebra_bridge import build_hopf_algebra_summary
def test_phase_dlxiv():
    assert build_hopf_algebra_summary()["hopf_algebra_theorem"]["therefore_hopf_verified"]
