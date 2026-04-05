"""Phase CDLXXX — Complete number glossary: all 20 fundamental integers verified."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_number_glossary_bridge import build_number_glossary_summary

def test_phase_cdlxxx_glossary_complete() -> None:
    t = build_number_glossary_summary()["number_glossary_theorem"]
    assert t["therefore_glossary_complete"] is True

def test_phase_cdlxxx_all_20() -> None:
    t = build_number_glossary_summary()["number_glossary_theorem"]
    assert t["count_verified"] == 20
