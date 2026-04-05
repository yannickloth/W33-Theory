"""Phase CDLXXXVI — Cayley-Dickson: ℂ=λ, ℍ=μ, 𝕆=8, product=μ³, sum=g."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_cayley_dickson_bridge import build_cayley_dickson_summary

def test_phase_cdlxxxvi_cayley_dickson() -> None:
    t = build_cayley_dickson_summary()["cayley_dickson_theorem"]
    assert t["therefore_cayley_dickson_encoded"] is True
