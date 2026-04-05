"""Phase DXXVI — Aut orbits: stab_v=1296=6⁴, stab_e=216=6³, stab_T=324=18²."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_automorphism_orbits_bridge import build_automorphism_orbits_summary

def test_phase_dxxvi_orbits() -> None:
    t = build_automorphism_orbits_summary()["automorphism_orbits_theorem"]
    assert t["therefore_orbits_verified"] is True
