"""Phase DLX — Magic square: F₄=52, E₆=78, E₇=133, E₈=248, Σ=511=2⁹-1."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_magic_square_bridge import build_magic_square_summary
def test_phase_dlx():
    t = build_magic_square_summary()["magic_square_theorem"]
    assert t["therefore_magic_square_verified"] is True
