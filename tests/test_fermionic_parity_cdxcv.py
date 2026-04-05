"""Phase CDXCV — Fermionic parity Z₂: complement SRG(40,27,18,18), E+Ē=780."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_fermionic_parity_bridge import build_fermionic_parity_summary

def test_phase_cdxcv_fermionic_parity() -> None:
    t = build_fermionic_parity_summary()["fermionic_parity_theorem"]
    assert t["therefore_z2_grading"] is True
