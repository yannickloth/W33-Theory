"""Phase CDLIV — Hodge firewall blocks exactly 6 = 2×gen Yukawa slots."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_hodge_firewall_bridge import build_hodge_firewall_summary

def test_phase_cdliv_firewall_encodes_yukawa() -> None:
    t = build_hodge_firewall_summary()["hodge_firewall_theorem"]
    assert t["therefore_firewall_encodes_yukawa"] is True

def test_phase_cdliv_exactly_6_blocked() -> None:
    t = build_hodge_firewall_summary()["hodge_firewall_theorem"]
    assert t["exactly_6_blocked"] is True

def test_phase_cdliv_passed_3_times_25() -> None:
    t = build_hodge_firewall_summary()["hodge_firewall_theorem"]
    assert t["passed_equals_3_times_25"] is True
