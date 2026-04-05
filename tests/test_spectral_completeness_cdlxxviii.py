"""Phase CDLXXVIII — Spectral completeness: Hoffman tight, α tight, gap=10."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_spectral_completeness_bridge import build_spectral_completeness_summary

def test_phase_cdlxxviii_spectral_completeness() -> None:
    t = build_spectral_completeness_summary()["spectral_completeness_theorem"]
    assert t["therefore_spectral_completeness"] is True

def test_phase_cdlxxviii_hoffman_tight() -> None:
    t = build_spectral_completeness_summary()["spectral_completeness_theorem"]
    assert t["hoffman_tight"] is True

def test_phase_cdlxxviii_alpha_tight() -> None:
    t = build_spectral_completeness_summary()["spectral_completeness_theorem"]
    assert t["alpha_tight"] is True
