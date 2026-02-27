#!/usr/bin/env python3
"""Utilities for interpreting permutations as quantum channels/unitaries.

This module can load a permutation (list of integers) from JSON and produce a
corresponding permutation matrix, which is a unitary matrix representing a
quantum channel that simply permutes computational basis states.  We include a
function to check whether a collection of such permutations closes under
matrix multiplication (i.e. forms a subgroup of the unitary group), which may
be useful when the permutations come from a finite group like the Monster.

Usage:
    python tools/quantum_channel_symmetry.py --perm_file path/to/perm.json

The permutation file should contain an array of integers [0..N-1] representing
an N-element permutation.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import List
import numpy as np


def load_permutation(path: Path) -> List[int]:
    return json.loads(path.read_text())


def permutation_matrix(perm: List[int]) -> np.ndarray:
    n = len(perm)
    M = np.zeros((n, n), dtype=int)
    for i, j in enumerate(perm):
        M[j, i] = 1
    return M


def is_unitary(M: np.ndarray) -> bool:
    return np.allclose(M.conj().T @ M, np.eye(M.shape[0]))


def closure_check(perms: List[List[int]]) -> bool:
    """Return True if the corresponding permutation matrices are closed."""
    mats = [permutation_matrix(p) for p in perms]
    n = len(mats)
    for i in range(n):
        for j in range(n):
            prod = mats[i] @ mats[j]
            if not any(np.array_equal(prod, m) for m in mats):
                return False
    return True


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm_file", required=True, help="JSON permutation file")
    args = ap.parse_args()
    perm = load_permutation(Path(args.perm_file))
    M = permutation_matrix(perm)
    print(f"Loaded permutation of length {len(perm)}")
    print("unitary?", is_unitary(M))

if __name__ == "__main__":
    main()
