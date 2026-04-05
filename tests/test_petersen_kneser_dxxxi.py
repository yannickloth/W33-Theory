"""Phase DXXXI — Petersen/Kneser: ovoid=10, v/pv=q+1."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_petersen_kneser_bridge import build_petersen_kneser_summary
def test_phase_dxxxi():
    t = build_petersen_kneser_summary()["petersen_kneser_theorem"]
    assert t["therefore_petersen_embedded"] is True
