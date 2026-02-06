"""
sign_mapping_simanneal.py

Simulated-annealing improvement of permutation mapping (coset->e6) to increase
number of matched triads and solvability under sign constraints.
"""

import json
import math
import random
from itertools import combinations

import numpy as np

# load data
with open(
    "artifacts/e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
with open("artifacts/e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
with open("artifacts/e6_sign_to_heis_perm.json", "r", encoding="utf-8") as f:
    sign2heis = json.load(f)["perm"]
    sign2heis = {int(k): int(v) for k, v in sign2heis.items()}

# d_bits in heis labeling
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
d_map_heis = {
    tuple(sorted((sign2heis[a], sign2heis[b], sign2heis[c]))): s
    for (a, b, c), s in d_map_sign.items()
}
d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_heis.items()}

# build coset triads same as before
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
messages = list(tuple(m) for m in __import__("itertools").product(range(3), repeat=6))
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]
# kernel basis and W
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

    if not in_span(m, basis):
        basis.append(m)
    if len(basis) == 4:
        break
W_basis = basis[:3]
W = set()
for a, b, c in __import__("itertools").product(range(3), repeat=3):
    w = tuple(
        (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
        for i in range(6)
    )
    W.add(w)
used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
coset_triads = []
for i, j, k in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
        and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
        and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
    ):
        coset_triads.append((i, j, k))
assert len(coset_triads) == 36
E6_TRIS = set(
    [tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]]
)


# helper solvability
def solvable(mapped_tri_set):
    nodes = set()
    for tri in mapped_tri_set:
        nodes.update(tri)
    nodes_list = sorted(nodes)
    idx_map = {v: i for i, v in enumerate(nodes_list)}
    rows = []
    for tri in mapped_tri_set:
        mask = 0
        for v in tri:
            mask |= 1 << idx_map[v]
        rows.append((mask, d_bits[tri]))
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


# seed
try:
    with open("artifacts/best_sign_constrained_mapping_multi.json", "r") as f:
        best = json.load(f)
        best_perm = best["perm"]
        best_score = best["score"]
except Exception:
    best_perm = list(range(27))
    best_score = -1

print("starting with score", best_score)


# Score function
def score(perm):
    mapped = [tuple(sorted((perm[a], perm[b], perm[c]))) for (a, b, c) in coset_triads]
    matched = set(mapped) & E6_TRIS
    s = len(matched) * 10 + (500 if solvable(matched) and len(matched) > 0 else 0)
    return s, len(matched), solvable(matched) if len(matched) > 0 else False


# Simulated annealing parameters
T0 = 1.0
T_min = 1e-4
alpha = 0.995
perm = best_perm.copy()
score_curr, matched_curr, solv_curr = score(perm)
best_overall = {
    "perm": perm.copy(),
    "score": score_curr,
    "matched": matched_curr,
    "solv": solv_curr,
}
print("initial", score_curr, matched_curr, solv_curr)

# run iterations
iters = 50000
T = T0
for it in range(iters):
    # propose move: swap two positions
    i, j = random.sample(range(27), 2)
    perm2 = perm.copy()
    perm2[i], perm2[j] = perm2[j], perm2[i]
    s2, m2, solv2 = score(perm2)
    delta = s2 - score_curr
    if delta > 0 or random.random() < math.exp(delta / max(T, 1e-12)):
        perm = perm2
        score_curr = s2
        matched_curr = m2
        solv_curr = solv2
        if s2 > best_overall["score"]:
            best_overall = {
                "perm": perm.copy(),
                "score": s2,
                "matched": m2,
                "solv": solv2,
            }
            print("new best", best_overall)
    T = max(T * alpha, T_min)
    if it % 5000 == 0:
        print(
            "iter",
            it,
            "T",
            T,
            "current score",
            score_curr,
            "best",
            best_overall["score"],
        )

print("done SA, best", best_overall)
with open("artifacts/best_sign_constrained_mapping_sa.json", "w") as f:
    json.dump(best_overall, f, indent=2, default=str)
print("wrote artifacts/best_sign_constrained_mapping_sa.json")
