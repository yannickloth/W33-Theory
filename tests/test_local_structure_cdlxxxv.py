"""Phase CDLXXXV — Local structure: 4 lines × 3 pts = k = 12 neighbors."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_local_structure_bridge import build_local_structure_summary

def test_phase_cdlxxxv_local_structure() -> None:
    t = build_local_structure_summary()["local_structure_theorem"]
    assert t["therefore_local_structure_verified"] is True
