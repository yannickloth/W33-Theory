#!/usr/bin/env python3
"""
Attempt to convert W0 mapping to the canonical 19-triad set (from W4) via constrained
local swap + SA. Anchors the 10-core triads (if present) and tries to maximize the
number of canonical triads matched on W0.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from itertools import combinations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--sa-iters", type=int, default=20000)
parser.add_argument("--seed", type=int, default=1)
parser.add_argument("--enforce-signs", action="store_true")
args = parser.parse_args()
random.seed(args.seed)

# load canonical set from W4
with open(
    ROOT / "artifacts" / "local_swap_W4_results.json", "r", encoding="utf-8"
) as f:
    w4 = json.load(f)
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]

# code to find matched triads given mapping and W
G_matrix = np.array(
    [
        [1, 0, 0, 0, 0, 0, 1, 1, 2, 2, 1, 2],
        [0, 1, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 2, 1, 1, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 2, 2, 1, 1, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 1, 2],
        [0, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1, 1],
    ]
)
M = np.array([[2, 2, 1, 2, 1, 2], [0, 2, 2, 0, 2, 1]], dtype=int)
messages = list(product(range(3), repeat=6))
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]

# build subspace list
subspaces = set()
subspace_list = []
for a, b, c in combinations(kernel, 3):
    S = set()
    for coeffs in product(range(3), repeat=3):
        v = tuple(
            (coeffs[0] * a[i] + coeffs[1] * b[i] + coeffs[2] * c[i]) % 3
            for i in range(6)
        )
        S.add(v)
    if len(S) == 27:
        key = tuple(sorted(S))
        if key not in subspaces:
            subspaces.add(key)
            subspace_list.append(S)

# find W0 and W4
W0_idx = 0
W4_idx = 4
W0 = subspace_list[W0_idx]
W4 = subspace_list[W4_idx]

# coset triads function
from itertools import combinations as comb


def coset_triads(W):
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    triads = []
    for u1, u2, u3 in comb(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            triads.append((u1, u2, u3))
    return {tuple(sorted(t)) for t in triads}


coset0 = coset_triads(W0)
coset4 = coset_triads(W4)

# canonical 19 is matched set for W4 from its best_mapping
with open(
    ROOT / "artifacts" / "local_swap_W4_results.json", "r", encoding="utf-8"
) as f:
    w4r = json.load(f)
best4 = w4r["best_mapping"]
canon = set()
for tri in E6_TRIADS:
    i, j, k = tri
    ct = tuple(sorted((best4[i], best4[j], best4[k])))
    if ct in coset4:
        canon.add(tri)
print("Canonical set size (W4):", len(canon))

# core from overlap
with open(ROOT / "artifacts" / "19_triad_overlap.json", "r", encoding="utf-8") as f:
    overlap = json.load(f)
core = {tuple(tri) for tri in overlap["intersection_all"]}
print("Core size:", len(core))

# load W0 mapping
with open(
    ROOT / "artifacts" / "sign_consistent_mapping_W0.json", "r", encoding="utf-8"
) as f:
    w0map = json.load(f)["mapping"]


# helper functions
def matched_set(mapping, coset_set):
    s = set()
    for tri in E6_TRIADS:
        i, j, k = tri
        if tuple(sorted((mapping[i], mapping[j], mapping[k]))) in coset_set:
            s.add(tri)
    return s


initial = matched_set(w0map, coset0)
init_common = len(initial & core)
init_canon_matched = len(initial & canon)
print(
    "W0 initial matched",
    len(initial),
    "core matched",
    init_common,
    "canonical matched",
    init_canon_matched,
)

# goal: maximize |matched ∩ canon| while preserving core (i.e., core subset always present)

# solvability function
try:
    with open(
        ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8"
    ) as f:
        sdata = json.load(f)
    d_map_sign = {
        tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
    }
except Exception:
    d_map_sign = {}
D_BITS = {t: (0 if s == 1 else 1) for t, s in d_map_sign.items()}


def solvable(mapped_tri_set):
    nodes = set()
    rows = []
    for tri in mapped_tri_set:
        nodes.update(tri)
    nodes_list = sorted(nodes)
    idx_map = {v: i for i, v in enumerate(nodes_list)}
    for tri in mapped_tri_set:
        mask = 0
        for v in tri:
            mask |= 1 << idx_map[v]
        rows.append((mask, D_BITS.get(tuple(sorted(tri)), 0)))
    pivots = {}
    for mask, rhs in rows:
        m = mask
        r = rhs
        while m:
            p = m.bit_length() - 1
            if p in pivots:
                pm, pr = pivots[p]
                m ^= pm
                r ^= pr
            else:
                pivots[p] = (m, r)
                break
        if m == 0 and r == 1:
            return False
    return True


# constrained SA on W0 mapping
perm = w0map.copy()
best_perm = perm.copy()
best_score = (
    len(matched_set(perm, coset0) & canon)
    if solvable(matched_set(perm, coset0))
    else -1
)
print("start best_score", best_score)
T0 = 1.0
T_min = 1e-4
iters = args.sa_iters
alpha = math.exp(math.log(T_min / T0) / max(iters, 1))
T = T0
for it in range(iters):
    i, j = random.sample(range(27), 2)
    perm2 = perm.copy()
    perm2[i], perm2[j] = perm2[j], perm2[i]
    # must keep core triads present
    if not core.issubset(matched_set(perm2, coset0)):
        continue
    matched_canon = len(matched_set(perm2, coset0) & canon)
    solv = solvable(matched_set(perm2, coset0))
    score = matched_canon - (0 if solv else 1000)
    # compute current
    curr_canon = len(matched_set(perm, coset0) & canon)
    curr_solv = solvable(matched_set(perm, coset0))
    curr_score = curr_canon - (0 if curr_solv else 1000)
    delta = score - curr_score
    if delta > 0 or random.random() < math.exp(delta / max(T, 1e-12)):
        perm = perm2
        if solv and matched_canon > best_score:
            best_perm = perm.copy()
            best_score = matched_canon
            print(" new best at it", it, "best_score", best_score)
    T = max(T * alpha, T_min)

final_matched = matched_set(best_perm, coset0)
print(
    "Done. best canonical matched on W0:",
    best_score,
    "final matched count",
    len(final_matched),
)
with open(
    ROOT / "artifacts" / "convert_W0_to_canonical_result.json", "w", encoding="utf-8"
) as f:
    json.dump(
        {
            "best_canon_matched": best_score,
            "final_matched_count": len(final_matched),
            "final_mapping": best_perm,
            "final_matched_tris": [list(t) for t in sorted(final_matched)],
        },
        f,
        indent=2,
    )
print("Wrote artifacts/convert_W0_to_canonical_result.json")
