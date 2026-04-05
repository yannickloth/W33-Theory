"""Phase CDXCIV — Distance-regular: {12,9;1,4}, k₂=27=q³."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_distance_regular_bridge import build_distance_regular_summary

def test_phase_cdxciv_distance_regular() -> None:
    t = build_distance_regular_summary()["distance_regular_theorem"]
    assert t["therefore_distance_regular"] is True
