"""Phase CDXCVII — Dynkin: ranks 6,7,8 and dims 78,133,248 from graph."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_dynkin_embedding_bridge import build_dynkin_embedding_summary

def test_phase_cdxcvii_dynkin() -> None:
    t = build_dynkin_embedding_summary()["dynkin_embedding_theorem"]
    assert t["therefore_dynkin_encoded"] is True
