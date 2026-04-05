"""Phase DLII — K-theory: K₀=ℤ⁴⁰, K₁=ℤ²⁰¹, K₀+K₁=241 prime."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_k_theory_bridge import build_k_theory_summary
def test_phase_dlii():
    t = build_k_theory_summary()["k_theory_theorem"]
    assert t["therefore_k_theory_verified"] is True
