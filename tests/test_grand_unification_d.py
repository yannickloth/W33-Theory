"""Phase D (500) — Grand unification milestone: all SRG + GQ + physics verified."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_grand_unification_bridge import build_grand_unification_summary

def test_phase_d_grand_unification() -> None:
    s = build_grand_unification_summary()
    assert s["status"] == "phase_d_complete"
    t = s["grand_unification_theorem"]
    assert t["therefore_grand_unified"] is True

def test_phase_d_all_srg_identities() -> None:
    t = build_grand_unification_summary()["grand_unification_theorem"]
    assert t["srg_identity_1"] is True
    assert t["srg_identity_2"] is True
    assert t["srg_identity_3"] is True
    assert t["srg_identity_4"] is True

def test_phase_d_physics_dimensions() -> None:
    t = build_grand_unification_summary()["grand_unification_theorem"]
    assert t["physics_240_roots"] is True
    assert t["physics_27_fund"] is True
    assert t["physics_78_adj"] is True
    assert t["anomaly_cancels"] is True
