"""Phase DXXXVI — Ramsey/clique: cover=ω=4, min_cliques=α=10, χ_f=4."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_ramsey_clique_bridge import build_ramsey_clique_summary
def test_phase_dxxxvi():
    t = build_ramsey_clique_summary()["ramsey_clique_theorem"]
    assert t["therefore_ramsey_verified"] is True
