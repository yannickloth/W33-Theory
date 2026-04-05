"""Phase CDLXV — Euler characteristic and Gauss-Bonnet: E×κ₁ = v."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_euler_gauss_bonnet_bridge import build_euler_gauss_bonnet_summary

def test_phase_cdlxv_euler_gb_holds() -> None:
    t = build_euler_gauss_bonnet_summary()["euler_gauss_bonnet_theorem"]
    assert t["therefore_euler_gb_holds"] is True

def test_phase_cdlxv_chi_neg_v() -> None:
    t = build_euler_gauss_bonnet_summary()["euler_gauss_bonnet_theorem"]
    assert t["chi_trunc_equals_neg_v"] is True

def test_phase_cdlxv_gauss_bonnet() -> None:
    t = build_euler_gauss_bonnet_summary()["euler_gauss_bonnet_theorem"]
    assert t["gauss_bonnet_E_kappa_v"] is True
