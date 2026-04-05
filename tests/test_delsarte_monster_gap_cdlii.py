"""Phase CDLII — Delsarte absolute bound = Monster–Leech gap = 324."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_delsarte_monster_gap_bridge import build_delsarte_monster_gap_summary

def test_phase_cdlii_triple_coincidence_holds() -> None:
    t = build_delsarte_monster_gap_summary()["delsarte_monster_gap_theorem"]
    assert t["therefore_the_triple_coincidence_holds"] is True

def test_phase_cdlii_thompson_decomposition() -> None:
    t = build_delsarte_monster_gap_summary()["delsarte_monster_gap_theorem"]
    assert t["thompson_decomposition_holds"] is True
