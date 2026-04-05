"""Phase DLXI — Cayley/group: Stab=6⁴=1296, arc_stab=108=μ×27, dist-transitive."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_cayley_group_bridge import build_cayley_group_summary
def test_phase_dlxi():
    assert build_cayley_group_summary()["cayley_group_theorem"]["therefore_cayley_verified"]
