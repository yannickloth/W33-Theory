"""Phase DXXXVIII — Yang-Baxter: integral eigenvalues, Boltzmann (1/6,-1/3), Σ=7/3."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_yang_baxter_bridge import build_yang_baxter_summary
def test_phase_dxxxviii():
    t = build_yang_baxter_summary()["yang_baxter_theorem"]
    assert t["therefore_yb_verified"] is True
