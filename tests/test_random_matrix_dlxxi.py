"""Phase DLXXI — RMT: mean=0, var=k, m₃=f, kurtosis=4/3=C₂(SU3)."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_random_matrix_bridge import build_random_matrix_summary
def test_phase_dlxxi():
    assert build_random_matrix_summary()["random_matrix_theorem"]["therefore_rmt_verified"]
