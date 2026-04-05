"""Phase DXIV — Terwilliger: subconstituents {1,12,27}, local λ-regular."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_terwilliger_bridge import build_terwilliger_summary

def test_phase_dxiv_terwilliger() -> None:
    t = build_terwilliger_summary()["terwilliger_theorem"]
    assert t["therefore_terwilliger_verified"] is True
