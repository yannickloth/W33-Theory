"""Phase CDLXXIII — Cyclotomic Φ₃=13, Φ₆=7: sum=v/2, diff=2q, Φ₃q=v−1."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_cyclotomic_coincidences_bridge import build_cyclotomic_coincidences_summary

def test_phase_cdlxxiii_cyclotomic_verified() -> None:
    t = build_cyclotomic_coincidences_summary()["cyclotomic_coincidences_theorem"]
    assert t["therefore_cyclotomic_structure_verified"] is True

def test_phase_cdlxxiii_product_91() -> None:
    t = build_cyclotomic_coincidences_summary()["cyclotomic_coincidences_theorem"]
    assert t["product_91"] is True
