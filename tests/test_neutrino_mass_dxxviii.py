"""Phase DXXVIII — Neutrino: democratic mixing, sin²θ₁₂=1/3, sin²θ₂₃=1/2."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_neutrino_mass_bridge import build_neutrino_mass_summary

def test_phase_dxxviii_neutrino() -> None:
    t = build_neutrino_mass_summary()["neutrino_mass_theorem"]
    assert t["therefore_neutrino_encoded"] is True
