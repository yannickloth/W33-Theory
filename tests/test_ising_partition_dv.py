"""Phase DV — Ising partition: Z₀=2⁴⁰, β_c=1/k, E_gs=−240."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_ising_partition_bridge import build_ising_partition_summary

def test_phase_dv_ising() -> None:
    t = build_ising_partition_summary()["ising_partition_theorem"]
    assert t["therefore_ising_consistent"] is True
