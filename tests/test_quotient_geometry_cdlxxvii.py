"""Phase CDLXXVII — Quotient: 10 orbits, 45 tritangents, 270+720=990 edges."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_quotient_geometry_bridge import build_quotient_geometry_summary

def test_phase_cdlxxvii_quotient_consistent() -> None:
    t = build_quotient_geometry_summary()["quotient_geometry_theorem"]
    assert t["therefore_quotient_geometry_consistent"] is True

def test_phase_cdlxxvii_270_edges() -> None:
    t = build_quotient_geometry_summary()["quotient_geometry_theorem"]
    assert t["tritangent_edges_270"] is True
