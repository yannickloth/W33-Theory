"""
Multi-restart version to try to improve best mapping found by sign_constrained_mapping_search.py
Runs many random restarts and greedy local swaps, keeps the best result.
"""

import json
import random
from collections import Counter
from itertools import combinations

import numpy as np

# load artifacts
with open(
    "artifacts/e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
with open("artifacts/e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
with open("artifacts/e6_sign_to_heis_perm.json", "r", encoding="utf-8") as f:
    sign2heis = json.load(f)["perm"]
    sign2heis = {int(k): int(v) for k, v in sign2heis.items()}

# compute d_bits in heis labeling
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
d_map_heis = {
    tuple(sorted((sign2heis[a], sign2heis[b], sign2heis[c]))): s
    for (a, b, c), s in d_map_sign.items()
}
d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_heis.items()}

# build coset triads (same as previous script)
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

# find kernel basis
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
# d bits exist for all 45 triads, but we will reference only those in matched sets

# helper functions


def solvable_sign_system(mapped_tri_set):
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
        rhs = d_bits[tri]
        rows.append((mask, rhs))
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


E6_TRIS_ALL = set(
    [tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]]
    + [tuple(sorted(tri)) for tri in heis["fiber_triads_e6id"]]
)

# load ordered couplings and coset coloring for stronger constraints
with open("artifacts/e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered_couplings = json.load(f)
ORDERED_MAP = {
    (it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered_couplings
}
with open("artifacts/coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]
from itertools import permutations

COLOR_PERMS = list(permutations([0, 1, 2]))

# scoring helpers


def ordered_consistent_for_perm(perm):
    matched_coset_triads = [
        t
        for t in coset_triads
        if tuple(sorted((perm[t[0]], perm[t[1]], perm[t[2]]))) in E6_TRIS
    ]
    if not matched_coset_triads:
        return True
    for col_perm in COLOR_PERMS:
        ok_all = True
        for a, b, c in matched_coset_triads:
            new_colors = {
                col_perm[coset_colors[a]]: a,
                col_perm[coset_colors[b]]: b,
                col_perm[coset_colors[c]]: c,
            }
            if set(new_colors.keys()) != {0, 1, 2}:
                ok_all = False
                break
            v0 = new_colors[0]
            v1 = new_colors[1]
            v2 = new_colors[2]
            i = perm[v0]
            j = perm[v1]
            k = perm[v2]
            pair = (i, j)
            if pair not in ORDERED_MAP:
                ok_all = False
                break
            k_expect, raw = ORDERED_MAP[pair]
            if k_expect != k:
                ok_all = False
                break
        if ok_all:
            return True
    return False


# scoring as before


def score_perm(perm):
    mapped = [tuple(sorted((perm[a], perm[b], perm[c]))) for (a, b, c) in coset_triads]
    matched = set(mapped) & E6_TRIS
    matched_count = len(matched)
    solv = solvable_sign_system(matched) if matched_count > 0 else False
    ordered_ok = ordered_consistent_for_perm(perm) if matched_count > 0 else True
    if not ordered_ok:
        return -9999, matched_count, False
    score = matched_count * 10 + (500 if solv else 0)
    return score, matched_count, solv


# random-restart greedy
best_global = {"score": -1}
for restart in range(200):
    if restart == 0:
        try:
            with open("artifacts/best_sign_constrained_mapping.json", "r") as f:
                seed = json.load(f)["perm"]
        except Exception:
            seed = list(range(27))
    else:
        seed = list(range(27))
        random.shuffle(seed)
    best_perm = seed.copy()
    best_score, best_matched, best_solved = score_perm(best_perm)
    improved = True
    iters = 0
    while improved and iters < 2000:
        improved = False
        iters += 1
        for i in range(27):
            for j in range(i + 1, 27):
                p = best_perm.copy()
                p[i], p[j] = p[j], p[i]
                s, mc, sv = score_perm(p)
                if s > best_score:
                    best_score = s
                    best_perm = p
                    best_matched = mc
                    best_solved = sv
                    improved = True
                    break
            if improved:
                break
    print("restart", restart, "best", best_score, best_matched, best_solved)
    if best_score > best_global["score"]:
        best_global = {
            "score": best_score,
            "perm": best_perm.copy(),
            "matched": best_matched,
            "solvable": best_solved,
        }
        with open("artifacts/best_sign_constrained_mapping_multi.json", "w") as f:
            json.dump(best_global, f, indent=2, default=str)

print("done, best_global:", best_global)
