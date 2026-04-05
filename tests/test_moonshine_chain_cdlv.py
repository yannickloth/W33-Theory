"""Phase CDLV — Moonshine chain: Monster→Baby→Fi₂₂→Conway→M₂₄→W(3,3)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_moonshine_chain_bridge import build_moonshine_chain_summary

def test_phase_cdlv_moonshine_chain_connects_monster_to_w33() -> None:
    t = build_moonshine_chain_summary()["moonshine_chain_theorem"]
    assert t["therefore_moonshine_chain_connects_monster_to_w33"] is True

def test_phase_cdlv_thompson_prime() -> None:
    t = build_moonshine_chain_summary()["moonshine_chain_theorem"]
    assert t["thompson_rep_is_monster_j_minus_1"] is True

def test_phase_cdlv_fi22_e6() -> None:
    t = build_moonshine_chain_summary()["moonshine_chain_theorem"]
    assert t["fi22_encodes_e6_adjoint"] is True
