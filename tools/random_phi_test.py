#!/usr/bin/env python3
"""Brute-force random sampling of edge->root bijections looking for nontrivial lift.

This is a straightforward Monte Carlo: take the canonical mapping and apply a
random permutation of the 240 roots, then evaluate the lift size (with and
without gauge).  If we ever encounter a map with lift>1, we dump it to
artifacts/random_phi_candidate.json and exit.

Usage:
    python tools/random_phi_test.py --samples 1000

"""
from __future__ import annotations

import json, random
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from tools.compute_phi_lift_subgroup import compute_lift_for_roots, edges
from tools.compute_phi_sign_gauge import compute_sign_gauge, load_root_list  # type: ignore

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--samples", type=int, default=1000)
args = parser.parse_args()

# load canonical list
edges_sorted, root_list0 = load_root_list(ROOT / "artifacts" / "edge_to_e8_root.json")

m = len(root_list0)
assert m == 240

for i in range(args.samples):
    perm = list(range(m))
    random.shuffle(perm)
    # apply permutation to roots
    candidate = [root_list0[j] for j in perm]
    raw = compute_lift_for_roots(candidate)
    if raw > 1:
        signvec, signed, gauged = compute_sign_gauge(candidate)
        print(f"found raw lift {raw} gauged {gauged} at sample {i}")
        out = {str(edges_sorted[k]): list(candidate[k]) for k in range(m)}
        (ROOT / "artifacts" / "random_phi_candidate.json").write_text(json.dumps(out, indent=2))
        (ROOT / "artifacts" / "sign_gauge_candidate.json").write_text(json.dumps(signvec, indent=2))
        break
    if i % 100 == 0:
        print(f"sample {i}: raw lift 1")

print("done")
