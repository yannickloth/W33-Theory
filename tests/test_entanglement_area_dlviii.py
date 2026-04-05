"""Phase DLVIII — Entanglement: κ=k=12, constant boundary, Page entropy=v."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_entanglement_area_bridge import build_entanglement_area_summary
def test_phase_dlviii():
    t = build_entanglement_area_summary()["entanglement_area_theorem"]
    assert t["therefore_entanglement_verified"] is True
