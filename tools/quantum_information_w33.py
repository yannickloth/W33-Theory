#!/usr/bin/env python3
"""
Quantum-information facts from W33.

This script prioritizes **certificate-grade** statements that are reproducible from
repo artifacts, and keeps more ambitious “physics-as-information” interpretations
clearly separated.

Certificates (see artifacts):
  - W33 is the commutation geometry of the **2-qutrit** Pauli group (dim 9),
    with 40 Pauli classes, 40 maximal commuting classes (lines), and 36 spreads.
  - The point-line incidence matrix has rank 25 over GF(2) and GF(3), and the
    GF(2) code has d_min = 8 (exact enumeration).

Regenerate artifacts with:
  - python3 tools/verify_w33_two_qutrit_pauli_geometry.py
  - python3 tools/compute_w33_incidence_code_ranks.py
"""

from __future__ import annotations

import json
from math import log2
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    print("=" * 72)
    print("W33 — Quantum Information (certificate-grade summary)")
    print("=" * 72)

    geom_path = ROOT / "artifacts" / "w33_two_qutrit_pauli_geometry.json"
    code_path = ROOT / "artifacts" / "w33_incidence_code_ranks.json"

    if not geom_path.exists():
        print(f"\nMissing: {geom_path}")
        print("Run: python3 tools/verify_w33_two_qutrit_pauli_geometry.py")
        return 2
    if not code_path.exists():
        print(f"\nMissing: {code_path}")
        print("Run: python3 tools/compute_w33_incidence_code_ranks.py")
        return 2

    geom = _load(geom_path)
    code = _load(code_path)

    srg = geom["w33_srg"]

    print("\n**Pauli/Clifford geometry (2 qutrits, dim 9)**")
    print(f"  Points (Pauli classes): {geom['points_count']}")
    print(f"  Lines (max commuting classes): {geom['lines_count']} (size 4 each)")
    print(f"  Spreads (10 disjoint lines): {geom['spreads_count']}")
    print(
        f"  Collinearity graph: SRG({srg['n']},{srg['k']},{srg['lambda']},{srg['mu']})"
    )
    print(
        "  MUB check (spread 0) max | |<ψ|φ>|^2 - 1/9 |:"
        f" {geom['mub_check']['max_overlap_dev']:.2e}"
    )

    print("\n**Incidence-code invariants (classical)**")
    gf2 = code["gf2"]
    gf3 = code["gf3"]
    print(f"  GF(2): rank={gf2['rank']}  k={gf2['k']}  d_min={gf2['d_min']}")
    print(f"  GF(3): rank={gf3['rank']}  k={gf3['k']}")

    print("\n**What this actually means (minimal claims)**")
    print(
        "  - The W33/W(3,3) object is literally the projective phase space of 2 qutrits."
    )
    print("  - Spreads correspond to complete stabilizer MUB sets in dimension 9.")
    print(
        "  - Any stronger “universe as N-qutrit computer” claim needs an extra model layer."
    )

    print("\n**Info content sanity check**")
    bits_per_qutrit = log2(3)
    print(f"  log2(3) = {bits_per_qutrit:.4f} bits/qutrit")
    print("  Two-qutrit Hilbert space dimension: 3^2 = 9")

    print("\nSee: QUANTUM_INFORMATION_EXTENSION.md for certificates vs hypotheses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
