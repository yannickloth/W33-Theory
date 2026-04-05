"""Phase CDXCIII — Ramanujan: |r|,|s| ≤ 2√(k-1), spectral gap = 8."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_ramanujan_bridge import build_ramanujan_summary

def test_phase_cdxciii_ramanujan() -> None:
    t = build_ramanujan_summary()["ramanujan_theorem"]
    assert t["therefore_ramanujan_expander"] is True
