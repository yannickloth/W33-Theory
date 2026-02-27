#!/usr/bin/env python3
"""Heuristic search for improved edge->root bijections with larger lift.

Given an initial JSON map, randomly propose swaps of root assignments and
measure the resulting lift subgroup size using the same machinery as
compute_phi_lift_subgroup.py.  Stops after a fixed number of trials or when
an improvement is found.

This is a lightweight utility; it does *not* perform exhaustive search, but
serves as a driver for Option B described in the conversation summary.
"""
from __future__ import annotations

import json, random
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
import sys
# make repo root importable when script run from tools/ directory
sys.path.insert(0, str(ROOT))

# reuse lift computation helper from compute_phi_lift_subgroup
from tools.compute_phi_lift_subgroup import compute_lift_for_roots, edge_index
from tools.compute_phi_lift_subgroup import dot  # used for equivalence

INPUT = ROOT / "artifacts" / "edge_to_e8_root.json"
OUTPUT = ROOT / "artifacts" / "edge_to_e8_root_candidate.json"

# load existing map
orig = json.loads(INPUT.read_text())
# store as list of edges ordered lexicographically
edges = sorted([tuple(int(x.strip()) for x in k.strip()[1:-1].split(",")) for k in orig.keys() if k.startswith("(")])

# convert to root vectors list
root_list = [tuple(int(x) for x in orig[str(e)]) for e in edges]

# lift size helper delegates to compute_phi_lift_subgroup

from tools.compute_phi_sign_gauge import compute_sign_gauge  # type: ignore

def compute_lift_size(root_list: List[Tuple[int, ...]]) -> int:
    # raw lift only (faster)
    return compute_lift_for_roots(root_list)

# parse optional CLI args
import argparse
parser = argparse.ArgumentParser(description="Random search for improved phi")
parser.add_argument("--trials", type=int, default=1000,
                    help="number of random swaps to try")
args = parser.parse_args()

best_raw = compute_lift_size(root_list)
# also track best gauged size (may equal raw initially)
best_gauged = best_raw
print('initial lift size', best_raw)
trials = args.trials
for t in range(trials):
    i,j = random.sample(range(len(root_list)),2)
    root_list[i], root_list[j] = root_list[j], root_list[i]
    sz = compute_lift_size(root_list)
    if sz > best_raw:
        # raw improvement; check gauge to see if it really pays off
        signvec, signed_roots, gauged = compute_sign_gauge(root_list)
        if gauged > best_gauged:
            print('found gauged improvement', best_gauged, '->', gauged, 'at trial', t)
            best_gauged = gauged
            # write candidate mapping (ungauged) and gauge
            newmap={str(edges[k]): list(root_list[k]) for k in range(len(edges))}
            OUTPUT.write_text(json.dumps(newmap,indent=2))
            (ROOT / 'artifacts' / 'sign_gauge_candidate.json').write_text(json.dumps(signvec, indent=2))
        best_raw = sz
    # revert
    root_list[i], root_list[j] = root_list[j], root_list[i]

print('search complete, best_raw', best_raw, 'best_gauged', best_gauged)
