"""Phase CDLXXXII — Dark sector: g=15=dim(SU(4) adj)=q(q+2)=|F₁₆*|."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_dark_sector_bridge import build_dark_sector_summary

def test_phase_cdlxxxii_dark_sector() -> None:
    t = build_dark_sector_summary()["dark_sector_theorem"]
    assert t["therefore_dark_sector_identified"] is True
