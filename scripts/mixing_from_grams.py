#!/usr/bin/env python3
"""Compute 3x3 overlap matrices for every ordered pair of Yukawa Gram matrices.

This general tool can be used to explore CKM-like or PMNS-like mixing
patterns between any two of the Gram matrices coming from the three
27-dimensional H1 subspaces.  The script prints the overlap matrices and
saves the results to ``data/mixing_from_grams.json``.

Usage::

    python scripts/mixing_from_grams.py

The output includes the principal eigenvalue ratios for each Gram as an aid in
selecting which matrices might correspond to up/down, lepton/neutrino, etc.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import itertools

import numpy as np

# ensure repository root on path for imports
import os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from scripts.ckm_from_grams import load_gram_list, compute_ckm, principal_ratios, V_CKM_exp
from scripts.experimental_data import fetch_ckm_from_wikipedia, fetch_pmns_from_wikipedia

# fetch live data where possible
_live_ckm = fetch_ckm_from_wikipedia()
if _live_ckm is not None:
    print("mixing_from_grams: using live CKM values from Wikipedia")
    V_CKM_exp = _live_ckm

V_PMNS_exp = np.array([
    [0.822, 0.547, 0.155],
    [0.451, 0.648, 0.614],
    [0.347, 0.529, 0.774],
])
_live_pmns = fetch_pmns_from_wikipedia()
if _live_pmns is not None:
    print("mixing_from_grams: using live PMNS values from Wikipedia")
    V_PMNS_exp = _live_pmns


def main():
    grams = load_gram_list()
    n = len(grams)
    if n < 2:
        print("need at least two Gram matrices")
        sys.exit(1)

    ratios = [principal_ratios(G)[1] for G in grams]
    print("principal sqrt-eigenvalue ratios:", ratios)

    results = []
    for i, j in itertools.permutations(range(n), 2):
        G1 = np.array(grams[i], dtype=float)
        G2 = np.array(grams[j], dtype=float)
        ov = compute_ckm(G1, G2)
        # compute errors relative to CKM and PMNS experimental magnitudes
        from scripts.ckm_from_grams import V_CKM_exp
        ckm_err = np.linalg.norm(ov - V_CKM_exp)
        pmns_err = np.linalg.norm(ov - V_PMNS_exp)
        entry = {"pair": (i, j), "overlap": ov.tolist(), "ckm_error": float(ckm_err), "pmns_error": float(pmns_err)}
        results.append(entry)
        print(f"Overlap {i} -> {j} (CKM_err={ckm_err:.3f}, PMNS_err={pmns_err:.3f}):")
        print(ov)
        print()

    # identify best matches
    best_ckm = min(results, key=lambda e: e["ckm_error"])
    best_pmns = min(results, key=lambda e: e["pmns_error"])
    print("Best CKM-like pair:", best_ckm)
    print("Best PMNS-like pair:", best_pmns)

    Path("data").mkdir(exist_ok=True)
    json.dump({"ratios": ratios, "results": results, "best_ckm": best_ckm, "best_pmns": best_pmns}, open("data/mixing_from_grams.json", "w"), indent=2)
    print("results saved to data/mixing_from_grams.json")


if __name__ == "__main__":
    main()
