"""Phase DXL — Vacuum hierarchy: E/v=6=rank, E/2=120 (cosmological power)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_vacuum_hierarchy_bridge import build_vacuum_hierarchy_summary
def test_phase_dxl():
    t = build_vacuum_hierarchy_summary()["vacuum_hierarchy_theorem"]
    assert t["therefore_hierarchy_verified"] is True
