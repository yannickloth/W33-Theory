#!/usr/bin/env python3
"""Brute-force assign the three Yukawa Gram matrices to physical sectors.

We have three 27x27 Gram matrices coming from the H1 decomposition.  The
physical interpretation could be {up quark, down quark, charged lepton} in
some order.  This script tries all six permutations and scores each assignment
based on how well the CKM matrix from the first two matches experiment and how
close the Koide parameter of the third is to 2/3.

Usage::

    python scripts/yukawa_sector_assignment.py

Results are printed and the best assignment saved to
``data/yukawa_sector_assignment.json``.
"""

from __future__ import annotations

import json
import itertools
import sys
from pathlib import Path

import numpy as np

# ensure repo root on path
import os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from MASS_PREDICTIONS import masses_GeV, koide_parameter
from scripts.ckm_from_grams import compute_ckm,V_CKM_exp
from scripts.yukawa_analysis import load_gram_list

sectors = ["up", "down", "lepton"]


def ckmlike_error(Gup: np.ndarray, Gdown: np.ndarray) -> float:
    CKM = compute_ckm(Gup, Gdown)
    # simple Frobenius norm of difference
    return np.linalg.norm(CKM - V_CKM_exp)


def koide_error(Glep: np.ndarray) -> float:
    eigs = np.linalg.eigvalsh(np.array(Glep, dtype=float))
    eigs.sort()
    sqrt_eigs = np.sqrt(eigs)
    top3 = sqrt_eigs[-3:]
    Q = koide_parameter(top3[0], top3[1], top3[2])
    return abs(Q - 2 / 3)


def main():
    grams = load_gram_list()
    if len(grams) < 3:
        print("need three Gram matrices, run cycle_space_decompose.py first")
        sys.exit(1)

    best = None
    results = []
    for perm in itertools.permutations(range(3)):
        Gup = np.array(grams[perm[0]], dtype=float)
        Gdown = np.array(grams[perm[1]], dtype=float)
        Glep = np.array(grams[perm[2]], dtype=float)
        score = ckmlike_error(Gup, Gdown) + koide_error(Glep)
        entry = {
            "perm": perm,
            "sectors": [sectors[i] for i in perm],
            "ckm_error": ckmlike_error(Gup, Gdown),
            "koide_error": koide_error(Glep),
            "score": score,
        }
        results.append(entry)
        if best is None or score < best["score"]:
            best = entry

    print("Assignment results (lower score better):")
    for r in sorted(results, key=lambda x: x["score"]):
        print(r)

    print("\nBest assignment:", best)
    Path("data").mkdir(exist_ok=True)
    json.dump({"results": results, "best": best}, open("data/yukawa_sector_assignment.json", "w"), indent=2)
    print("saved data/yukawa_sector_assignment.json")


if __name__ == "__main__":
    main()
