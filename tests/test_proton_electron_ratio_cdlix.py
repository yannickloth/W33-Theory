"""Phase CDLIX — Proton-electron mass ratio: 6π⁵ ≈ 1836."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_proton_electron_ratio_bridge import build_proton_electron_ratio_summary

def test_phase_cdlix_proton_electron_from_gq() -> None:
    t = build_proton_electron_ratio_summary()["proton_electron_ratio_theorem"]
    assert t["therefore_proton_electron_ratio_from_gq"] is True

def test_phase_cdlix_within_20ppm() -> None:
    t = build_proton_electron_ratio_summary()["proton_electron_ratio_theorem"]
    assert t["six_pi5_matches_within_20ppm"] is True
