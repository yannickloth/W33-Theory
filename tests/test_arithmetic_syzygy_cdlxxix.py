"""Phase CDLXXIX — SRG arithmetic syzygy: all identities close."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_arithmetic_syzygy_bridge import build_arithmetic_syzygy_summary

def test_phase_cdlxxix_syzygy_closed() -> None:
    t = build_arithmetic_syzygy_summary()["arithmetic_syzygy_theorem"]
    assert t["therefore_syzygy_closed"] is True

def test_phase_cdlxxix_trace_neg_k() -> None:
    t = build_arithmetic_syzygy_summary()["arithmetic_syzygy_theorem"]
    assert t["trace_neg_k"] is True
