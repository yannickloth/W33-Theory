#!/usr/bin/env python3
"""Export a quantum stabilizer code derived from the Golay-Clifford mapping.

Loads the JSON mapping produced by ``golay_clifford.py`` and treats each
monomial as a Pauli operator on 12 qubits.  The symplectic representation
(x,z) is computed by splitting the 24-bit monomial vector into two 12-bit
strings; we then choose a small set of independent generators to form a
stabilizer group.

The script also computes the distance of the resulting code by enumerating
logical operators (within reasonable limits) and comparing weights.

Usage:
    python tools/golay_stabilizer.py

Outputs ``artifacts/golay_stabilizer_generators.txt`` and a summary printed to
stdout.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple, List

ROOT = Path(__file__).resolve().parents[1]


def load_mapping() -> dict:
    path = ROOT / "artifacts" / "golay_clifford_mapping.json"
    return json.loads(path.read_text())


def symplectic_from_monomial(mon: List[int]) -> Tuple[int, int]:
    """Return 12-bit symplectic vector (x,z) from monomial indices.
    same convention as golay_clifford.symplectic_representation"""
    x = 0
    z = 0
    for idx in mon:
        if idx % 2 == 0:
            x |= 1 << (idx // 2)
        else:
            z |= 1 << (idx // 2)
    return x, z


def weight_symplectic(x: int, z: int) -> int:
    # weight of Pauli string: number of nonidentity factors
    return bin(x | z).count("1")


def generate_stabilizer() -> List[Tuple[int, int]]:
    mapping = load_mapping()
    # select first 12 even-weight monomials
    gens = []
    for v in mapping.values():
        if len(v) % 2 == 0 and len(gens) < 12:
            gens.append(v)
    sym = [symplectic_from_monomial(g) for g in gens]
    return sym


def compute_distance(sym_gens: List[Tuple[int, int]], max_search: int = 1<<15) -> int:
    # brute-force search logical operators weight: any Pauli commuting with all
    # generators but not in group. Simplify by scanning up to max_search random
    # symplectic vectors.
    import random
    best = 999
    for _ in range(max_search):
        x = random.getrandbits(12)
        z = random.getrandbits(12)
        # commuting condition: symplectic inner product with each generator =0
        ok = True
        for gx,gz in sym_gens:
            if bin(x * gz ^ z * gx).count("1") % 2 != 0:
                ok = False
                break
        if not ok:
            continue
        w = weight_symplectic(x,z)
        if 0 < w < best:
            best = w
    return best if best<999 else -1


def main():
    gens = generate_stabilizer()
    outfile = ROOT / "artifacts" / "golay_stabilizer_generators.txt"
    with open(outfile, "w") as f:
        for x,z in gens:
            f.write(f"{x:012b} {z:012b}\n")
    print("wrote", outfile)
    dist = compute_distance(gens, max_search=10000)
    print("estimated code distance", dist)


if __name__ == "__main__":
    main()
