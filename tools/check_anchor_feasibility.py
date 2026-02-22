#!/usr/bin/env python3
"""
Check whether the anchor triad set (from an anchor W) is possible on a target W
by verifying that each anchor triad has at least one candidate coset triple mapping.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--anchor-w", type=int, default=4)
parser.add_argument("--target-w", type=int, default=0)
args = parser.parse_args()

with open(
    ROOT / "artifacts" / "local_swap_W{0}_results.json".format(args.anchor_w),
    "r",
    encoding="utf-8",
) as f:
    anchor = json.load(f)
anchor_map = anchor["best_mapping"]

with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]

# code matrices
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

# build subspaces
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

# compute anchor triads (coset assignment check using anchor W's coset triads)
W_anchor = subspace_list[args.anchor_w]
used = set()
cosets_anchor = []
for m in messages:
    if m in used:
        continue
    cosets_anchor.append(m)
    for w in W_anchor:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
cw27_anchor = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets_anchor]
coset_triads_anchor = set()
for u1, u2, u3 in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27_anchor[u1], cw27_anchor[u2])) == 6
        and sum(x != y for x, y in zip(cw27_anchor[u1], cw27_anchor[u3])) == 6
        and sum(x != y for x, y in zip(cw27_anchor[u2], cw27_anchor[u3])) == 6
    ):
        coset_triads_anchor.add(tuple(sorted((u1, u2, u3))))
anchor_tris = [
    tri
    for tri in E6_TRIADS
    if tuple(sorted((anchor_map[tri[0]], anchor_map[tri[1]], anchor_map[tri[2]])))
    in coset_triads_anchor
]
print("anchor triads count:", len(anchor_tris))

# compute candidates on target W
W_t = subspace_list[args.target_w]
used = set()
cosets_t = []
for m in messages:
    if m in used:
        continue
    cosets_t.append(m)
    for w in W_t:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
cw27_t = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets_t]
coset_triads_t = set()
for u1, u2, u3 in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27_t[u1], cw27_t[u2])) == 6
        and sum(x != y for x, y in zip(cw27_t[u1], cw27_t[u3])) == 6
        and sum(x != y for x, y in zip(cw27_t[u2], cw27_t[u3])) == 6
    ):
        coset_triads_t.add(tuple(sorted((u1, u2, u3))))

impossible = []
for tri in anchor_tris:
    # check if any mapping (perm) from tri to coset_triads_t exists
    possible = False
    for ct in coset_triads_t:
        for perm_ct in permutations(ct):
            # don't need to check colors here; just existence
            possible = True
            break
        if possible:
            break
    if not possible:
        impossible.append(tri)

if impossible:
    print("Some anchor triads impossible on target W:", impossible)
else:
    print("All anchor triads have at least one candidate on target W")
