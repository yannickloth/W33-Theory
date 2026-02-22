#!/usr/bin/env python3
import sys
from pathlib import Path

import numpy as np

# ensure repo root on sys.path when invoked as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.ddmin_z3_candidate import make_test_function

p = Path("committed_artifacts") / "PART_CVII_z3_candidate_1770606880_01.npz"
print("Loading", p)
with np.load(p) as f:
    c0 = f["cluster_0"]
    c1 = f["cluster_1"]
    c2 = f["cluster_2"]

print("shapes:", c0.shape, c1.shape, c2.shape)
func = make_test_function([c0, c1, c2], [c0.shape[1], c1.shape[1], c2.shape[1]])
S = list(range(c0.shape[1] + c1.shape[1] + c2.shape[1]))
print("Full S size", len(S))
print("Test(full):", func(S))
for k, c in enumerate([c0, c1, c2]):
    rk = np.linalg.matrix_rank(c, tol=1e-8)
    print("Rank cluster", k, rk)
