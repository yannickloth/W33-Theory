"""Phase CDLXXXI — Krein conditions: abs bound 324 = Delsarte, ratio num = b₁."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_krein_conditions_bridge import build_krein_conditions_summary

def test_phase_cdlxxxi_krein_verified() -> None:
    t = build_krein_conditions_summary()["krein_conditions_theorem"]
    assert t["therefore_krein_verified"] is True

def test_phase_cdlxxxi_abs_bound_324() -> None:
    t = build_krein_conditions_summary()["krein_conditions_theorem"]
    assert t["abs_bound_f_324"] is True
