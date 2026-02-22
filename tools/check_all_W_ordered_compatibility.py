#!/usr/bin/env python3
"""
Check all 3-dim subspaces W ⊂ ker(M) (the 40 canonical choices) and for each
color permutation test whether all E6 triads have at least one allowed coset
triple under ordered-couplings constraints. Print summary.
"""
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load artifacts
with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]
from collections import Counter

ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered}

# E6 triads
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
triads = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]

# Setup code/CW matrix and M
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

# find kernel basis (same deterministic method as before)
basis = []
for m in kernel:
    if all(x == 0 for x in m):
        continue
    if not basis:
        basis.append(m)
        continue

    def in_span(m, basis):
        if len(basis) == 1:
            for a in range(3):
                if tuple((a * basis[0][i]) % 3 for i in range(6)) == m:
                    return True
            return False
        if len(basis) == 2:
            for a in range(3):
                for b in range(3):
                    if (
                        tuple(
                            ((a * basis[0][i] + b * basis[1][i]) % 3) for i in range(6)
                        )
                        == m
                    ):
                        return True
            return False
        if len(basis) == 3:
            for a in range(3):
                for b in range(3):
                    for c in range(3):
                        if (
                            tuple(
                                (
                                    (
                                        a * basis[0][i]
                                        + b * basis[1][i]
                                        + c * basis[2][i]
                                    )
                                    % 3
                                )
                                for i in range(6)
                            )
                            == m
                        ):
                            return True
            return False
        return False

    if not in_span(m, basis):
        basis.append(m)
    if len(basis) == 4:
        break
# enumerate all distinct 3-dim subspaces by spanning combinations of kernel vectors
subspaces = set()
subspace_list = []
for a, b, c in combinations(kernel, 3):
    # compute span
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

print("Found", len(subspace_list), "distinct 3-dim subspaces (expected 40)")
W_choices = subspace_list


solutions = []
for wi, Wb in enumerate(W_choices):
    if wi % 5 == 0:
        print("Checking W idx", wi)
    # build W
    Wset = set()
    for a, b, c in product(range(3), repeat=3):
        w = tuple((a * Wb[0][i] + b * Wb[1][i] + c * Wb[2][i]) % 3 for i in range(6))
        Wset.add(w)
    # cosets
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in Wset:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    # coset triads
    from itertools import combinations as comb

    coset_triads = []
    for i, j, k in comb(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
            and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
            and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
        ):
            coset_triads.append((i, j, k))
    coset_triads_set = set(tuple(sorted(t)) for t in coset_triads)
    if len(coset_triads) != 36:
        print("W", wi, "has", len(coset_triads), "triads (expected 36); skipping")
        continue
    ok_for_some_perm = False
    detailed = {}
    for col_perm in permutations([0, 1, 2]):
        zero_tris = []
        for tri in triads:
            i, j, k = tri
            allowed = 0
            for ct in coset_triads:
                for perm_ct in permutations(ct):
                    u1, u2, u3 = perm_ct
                    new_colors = {
                        col_perm[coset_colors[u1]]: i,
                        col_perm[coset_colors[u2]]: j,
                        col_perm[coset_colors[u3]]: k,
                    }
                    if set(new_colors.keys()) != {0, 1, 2}:
                        continue
                    v0 = new_colors[0]
                    v1 = new_colors[1]
                    v2 = new_colors[2]
                    pair = (v0, v1)
                    if pair in ORDERED and ORDERED[pair][0] == v2:
                        allowed += 1
            if allowed == 0:
                zero_tris.append(tri)
        detailed[col_perm] = zero_tris
        if not zero_tris:
            ok_for_some_perm = True
            break
    if ok_for_some_perm:
        solutions.append((wi, Wb, col_perm))
    else:
        # store minimal counts for reporting
        counts = [len(detailed[p]) for p in detailed]
        detailed_counts = {"min_zero": min(counts), "max_zero": max(counts)}
    print(
        "W", wi, "min zero triads across perms", min(len(detailed[p]) for p in detailed)
    )

print("\nSummary:")
if solutions:
    print("Some W choices allow full coverage under a color perm:")
    for s in solutions:
        print("W idx", s[0], "color perm", s[2])
else:
    print(
        "No W choice out of",
        len(W_choices),
        "allowed mapping of all triads under any color perm",
    )

PY
