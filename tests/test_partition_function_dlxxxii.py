"""Phase DLXXXII — Partition: E₀=-E, 2^v states, order=q², χ⁻¹=α."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_partition_function_bridge import build_partition_function_summary
def test_phase_dlxxxii():
    assert build_partition_function_summary()["partition_function_theorem"]["therefore_partition_verified"]
