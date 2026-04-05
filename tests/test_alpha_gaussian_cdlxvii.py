"""Phase CDLXVII — α⁻¹ = 137 from Gaussian spectral invariants of W(3,3)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_alpha_gaussian_bridge import build_alpha_gaussian_summary

def test_phase_cdlxvii_alpha_from_gaussian() -> None:
    t = build_alpha_gaussian_summary()["alpha_gaussian_theorem"]
    assert t["therefore_alpha_from_gaussian_spectral"] is True

def test_phase_cdlxvii_alpha_137() -> None:
    t = build_alpha_gaussian_summary()["alpha_gaussian_theorem"]
    assert t["alpha_inv_137"] is True

def test_phase_cdlxvii_primes_to_E() -> None:
    t = build_alpha_gaussian_summary()["alpha_gaussian_theorem"]
    assert t["primes_to_E_equals_v_plus_k"] is True
