"""Phase CDLXI — Seidel energy = 240 = |Roots(E₈)| = edge count."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_seidel_e8_energy_bridge import build_seidel_e8_energy_summary

def test_phase_cdlxi_seidel_encodes_e8() -> None:
    t = build_seidel_e8_energy_summary()["seidel_e8_energy_theorem"]
    assert t["therefore_seidel_encodes_e8"] is True

def test_phase_cdlxi_disc_diff_neg_f() -> None:
    t = build_seidel_e8_energy_summary()["seidel_e8_energy_theorem"]
    assert t["disc_diff_equals_neg_f"] is True
