"""Phase CDLXXV — Curvature pair κ₁=1/6, κ₂=2/3: sum=5/6, ratio=μ."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_curvature_pair_bridge import build_curvature_pair_summary

def test_phase_cdlxxv_curvature_consistent() -> None:
    t = build_curvature_pair_summary()["curvature_pair_theorem"]
    assert t["therefore_curvature_pair_consistent"] is True

def test_phase_cdlxxv_ratio_mu() -> None:
    t = build_curvature_pair_summary()["curvature_pair_theorem"]
    assert t["ratio_equals_mu"] is True

def test_phase_cdlxxv_gb_v() -> None:
    t = build_curvature_pair_summary()["curvature_pair_theorem"]
    assert t["gb_equals_v"] is True
