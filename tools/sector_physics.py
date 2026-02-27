#!/usr/bin/env python3
"""Compute simple physics quantities with sector tagging.

This tool demonstrates how the E6×A2 sector decomposition of the W33->E8
bijection can be used alongside existing CKM routines.  It prints the sector
counts, builds toy Yukawa matrices (either random or user-specified), and
computes the resulting CKM matrix and Jarlskog invariant.

The purpose is to "connect to physical models" by showing how sector data
can accompany physics predictions.
"""
from __future__ import annotations

import json, random
from pathlib import Path
import numpy as np

# compute repository root before adjusting path
ROOT = Path(__file__).resolve().parents[1]

# import CKM routine
import sys
# ensure repo root + scripts folder on path for importing internal modules
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from scripts.w33_ckm_from_vev import compute_ckm_and_jarlskog


def load_sector_counts():
    path = ROOT / "artifacts" / "w33_edges_by_rootclass_counts.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def random_yukawa():
    # small random integers mod 10 to mimic hierarchy
    return np.random.randint(-5,6,size=(3,3)).astype(float)


def main():
    print("=== Sector counts ===")
    counts = load_sector_counts()
    total = sum(counts.values())
    for k,v in counts.items():
        print(f"{k}: {v} ({v/total:.2%})")

    # build toy Yukawas
    Yu = random_yukawa()
    Yd = random_yukawa()
    V, J = compute_ckm_and_jarlskog(Yu, Yd)
    print("\n=== CKM matrix (random toy Yukawas) ===")
    print(np.round(np.abs(V),4))
    print("Jarlskog invariant", J)

    # note: in a full model Yu,Yd would be constructed from sector-dependent
    # data.  Here we just illustrate using the CKM routine after tagging.

if __name__ == "__main__":
    main()
