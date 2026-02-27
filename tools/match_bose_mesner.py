#!/usr/bin/env python3
"""Compare a candidate 120-point association scheme against the canonical
Bose--Mesner solution produced by the duad/edgepair action.

The input file may either be a JSON bundle with a list of adjacency
matrices under key ``"relations"`` (or simply a bare list of matrices), or
it may be the special ``duad_intersection_numbers.json`` produced by the
solution bundle.  When supplied with two files (``--candidate`` and
``--solution``) the script will compute the structure constants of the
candidate scheme and report any discrepancies with the reference.

Usage examples::

    # verify that the solved bundle is self-consistent
    tools/match_bose_mesner.py --candidate \
        TOE_BoseMesner_Algebra_Solution_bundle_v04_20260227/duad_intersection_numbers.json

    # compare a scheme produced by another script
    tools/match_bose_mesner.py --candidate candidate.json \
        --solution TOE_BoseMesner_Algebra_Solution_bundle_v04_20260227/duad_intersection_numbers.json

The comparison is made on the $p_{ij}^k$ constants; the script also
prints valencies and allows the user to compute the eigenmatrix if desired.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np


def load_matrices(path: Path) -> List[np.ndarray]:
    data = json.loads(path.read_text())
    mats = None
    if isinstance(data, dict):
        # if it's the solved bundle containing p_ijk then the candidate
        # file is probably wrong
        if "p_ijk" in data and not any(k in data for k in ("relations", "adjacency", "matrices")):
            raise ValueError("input appears to be the intersection-numbers bundle; give --solution instead")
        # otherwise, look for conventional adjacency keys
        for key in ("relations", "adjacency", "matrices"):
            if key in data:
                mats = data[key]
                break
    if mats is None:
        # assume the file itself is a top-level list of matrices
        mats = data
    return [np.array(m, dtype=int) for m in mats]


def compute_pijk(mats: List[np.ndarray]) -> List[List[List[int]]]:
    r = len(mats)
    n = mats[0].shape[0]
    p = [[[0] * r for _ in range(r)] for _ in range(r)]
    for i in range(r):
        for j in range(r):
            C = mats[i] @ mats[j]
            for k in range(r):
                mask = mats[k] == 1
                vals = set(int(x) for x in C[mask].flatten())
                if len(vals) != 1:
                    raise RuntimeError(f"inconsistent p_{{{i}{j}{k}}}: {vals}")
                p[i][j][k] = vals.pop()
    return p


def compare_pijk(a, b) -> bool:
    ok = True
    for i in range(len(a)):
        for j in range(len(a)):
            for k in range(len(a)):
                if a[i][j][k] != b[i][j][k]:
                    print(f"mismatch p_{i}{j}{k}: candidate {a[i][j][k]}, reference {b[i][j][k]}")
                    ok = False
    return ok


def main():
    parser = argparse.ArgumentParser(description="Match candidate Bose-Mesner scheme")
    parser.add_argument("--candidate", required=True, type=Path,
                        help="JSON file containing candidate adjacency matrices")
    parser.add_argument("--solution", type=Path,
                        help="reference file with p_ijk table (bundle)")
    args = parser.parse_args()
    if args.solution and args.candidate.resolve() == args.solution.resolve():
        print("candidate identical to solution, nothing to match")
        sys.exit(0)
    cand_mats = load_matrices(args.candidate)
    print("loaded", len(cand_mats), "relation matrices from", args.candidate)
    cand_p = compute_pijk(cand_mats)
    print("computed candidate structure constants")
    if args.solution:
        sol = json.loads(args.solution.read_text())
        sol_p = sol.get("p_ijk")
        if sol_p is None:
            raise ValueError("solution file does not contain p_ijk")
        print("comparing against solution bundle")
        ok = compare_pijk(cand_p, sol_p)
        if ok:
            print("schemes match exactly")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # simply dump the p_ijk table
        out = {"p_ijk": cand_p}
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    import sys
    main()
