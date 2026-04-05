"""Phase CDLXXXIII — Gauge chain: SM=k=12, SU(5)=f=24, E₆=2(v-1)=78, E₈=E+8=248."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_gauge_embedding_bridge import build_gauge_embedding_summary

def test_phase_cdlxxxiii_gauge_chain() -> None:
    t = build_gauge_embedding_summary()["gauge_embedding_theorem"]
    assert t["therefore_gauge_chain_from_srg"] is True
