#!/usr/bin/env python3
"""
Analyze existing mapping outputs and compute maximal sign-consistent subset of matched triads.
For each mapping file 'opt_mapping_W*_status_*.json' compute matched triads and
search for the largest subset that is solvable (GF(2) parity constraints).
Writes artifacts/sign_satisfiable_analysis.json
"""
import json
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

# load e6 triads and d_bits
with open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8") as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
with open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    s = json.load(f)
d_map_sign = {tuple(sorted(t["triple"])): t["sign"] for t in s["solution"]["d_triples"]}
# sign bits: +1->0, -1->1
D_BITS = {t: (0 if sgn == 1 else 1) for t, sgn in d_map_sign.items()}

# reconstruct kernel -> subspaces (same logic)
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

# kernel basis
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
subspace_list = []
from itertools import combinations

subspaces = set()
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

# find mapping files
import glob

files = list(ART.glob("opt_mapping_W*_status_*.json"))
files = sorted(files)


def compute_coset_triads(W):
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
    for i in range(27):
        for j in range(i + 1, 27):
            for k in range(j + 1, 27):
                if (
                    sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
                    and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
                    and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
                ):
                    triads.append((i, j, k))
    return set(tuple(sorted(t)) for t in triads), cosets, cw27


# GF(2) solve


def is_solvable(tris):
    # tris: list of unordered E6 tri tuples (e6 ids)
    nodes = sorted({v for t in tris for v in t})
    idx = {v: i for i, v in enumerate(nodes)}
    rows = []
    for t in tris:
        m = 0
        for v in t:
            m |= 1 << idx[v]
        rhs = D_BITS.get(t, 0)
        rows.append((m, rhs))
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


# brute force subset search of matched triads by descending size
from itertools import combinations as combs

out = []
for f in files:
    data = json.load(open(f, "r", encoding="utf-8"))
    W_idx = data["W_idx"]
    W = subspace_list[W_idx]
    coset_triads_set, cosets, cw27 = compute_coset_triads(W)
    mapping = data["mapping"]
    # matched triads
    matched = []
    for t in E6_TRIADS:
        # check if images form a coset triad
        u = tuple(sorted((mapping[t[0]], mapping[t[1]], mapping[t[2]])))
        if u in coset_triads_set:
            matched.append(t)
    matched = sorted(set(matched))
    m_count = len(matched)
    # try subsets size m_count..0
    max_sign = 0
    best_subset = []
    for r in range(m_count, 0, -1):
        found = False
        for subset in combs(matched, r):
            if is_solvable(subset):
                max_sign = r
                best_subset = list(subset)
                found = True
                break
        if found:
            break
    out.append(
        {
            "file": str(f.name),
            "W_idx": W_idx,
            "matched": m_count,
            "max_sign_subset": max_sign,
            "best_subset": [list(t) for t in best_subset],
        }
    )

(Path(ART) / "sign_satisfiable_analysis.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote artifacts/sign_satisfiable_analysis.json")
