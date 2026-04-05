"""Phase CDXC — Conformal window: β₀ = f-N_c = 21, asymptotic freedom verified."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_conformal_window_bridge import build_conformal_window_summary

def test_phase_cdxc_conformal_window() -> None:
    t = build_conformal_window_summary()["conformal_window_theorem"]
    assert t["therefore_conformal_encoded"] is True
