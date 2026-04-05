"""Phase DLVI — Spectral action: a₁=vk=480, a₂=v(k²+k)=6240, a₂/a₁=Φ₃=13."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_spectral_action_bridge import build_spectral_action_summary
def test_phase_dlvi():
    t = build_spectral_action_summary()["spectral_action_theorem"]
    assert t["therefore_spectral_action_verified"] is True
