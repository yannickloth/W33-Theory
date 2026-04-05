"""Phase DXXXII — Shannon capacity: ϑ=α=10, ϑ̄=ω=4, αω=v."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_shannon_capacity_bridge import build_shannon_capacity_summary
def test_phase_dxxxii():
    t = build_shannon_capacity_summary()["shannon_capacity_theorem"]
    assert t["therefore_shannon_determined"] is True
