"""
sign_constrained_mapping_search.py

Heuristic local-search that starts from a seed permutation (coset -> e6) and tries to
improve the number of mapped triads (coset Hamming=6 triads -> E6 triads). As a
secondary (hard) constraint it attempts to solve for per-node sign bits s_i (in GF(2))
so that for every mapped triad t we have s_i + s_j + s_k = d_t (bits). If the sign
system is solvable on the matched triads, that mapping is strongly preferred.

Saves results to artifacts/best_sign_constrained_mapping.json
"""

import json
import random
from collections import Counter
from itertools import combinations

# Load data
with open(
    "artifacts/e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
with open("artifacts/e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)

# map sign ids -> heis ids permutation
with open("artifacts/e6_sign_to_heis_perm.json", "r", encoding="utf-8") as f:
    sign2heis = json.load(f)["perm"]
sign2heis = {int(k): int(v) for k, v in sign2heis.items()}

# e6 triads (all 45)
e6_triads = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
] + [tuple(sorted(tri)) for tri in heis["fiber_triads_e6id"]]
e6_triads_set = set(e6_triads)

# d_triples mapped to heis labels
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
d_map_heis = {
    tuple(sorted((sign2heis[a], sign2heis[b], sign2heis[c]))): s
    for (a, b, c), s in d_map_sign.items()
}
# d bits
d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_heis.items()}  # +1->0, -1->1

# coset triads (we reconstruct the same W & cosets used earlier by GOLAY_27_REPRESENTATION)
# We use the W and G used in repo scripts
import numpy as np

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

# pick the same W as used in GOLAY_27_REPRESENTATION.py (the script used first ker basis 3 vectors)
# For robustness, we reconstruct the W that produced cosets used earlier by using the same basis selection
# (the repository's default W_basis in GOLAY_27_REPRESENTATION.py is obtained from the kernel basis)
# To avoid re-deriving kernel basis logic here, we'll load the coset triads produced earlier in MATCH_E6_TRIADS_TO_COSETS.py if present

# Fall back: recompute the canonical W used earlier by taking the first subspace detected in SEARCH_3D_SUBSPACES_FOR_SCHLAFLI.py
# We'll reuse the same W_basis as GOLAY_27_REPRESENTATION used via ker_basis[:3] by reconstructing kernel and picking basis

kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]


# find a kernel basis (4 vectors)
def find_kernel_basis(kernel):
    basis = []
    for m in kernel:
        if all(x == 0 for x in m):
            continue
        if not basis:
            basis.append(m)
            continue

        # check in span
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
                                ((a * basis[0][i] + b * basis[1][i]) % 3)
                                for i in range(6)
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
    return basis


ker_basis = find_kernel_basis(kernel)
W_basis = ker_basis[:3]
# build W
W = set()
for a, b, c in __import__("itertools").product(range(3), repeat=3):
    w = tuple(
        (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
        for i in range(6)
    )
    W.add(w)
# cosets
used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
# coset codewords
cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
# coset triads
coset_triads = []
for i, j, k in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
        and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
        and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
    ):
        coset_triads.append((i, j, k))
assert len(coset_triads) == 36

# Load seed permutation
try:
    with open("artifacts/best_coset_to_e6_perm.json", "r") as f:
        seed = json.load(f)["perm"]
    seed = [int(x) for x in seed]
except Exception:
    seed = list(range(27))

# load ordered couplings and coset coloring for stronger constraints
with open("artifacts/e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered_couplings = json.load(f)
# map (i,j) -> (k, raw)
ORDERED_MAP = {
    (it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered_couplings
}

with open("artifacts/coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]

from itertools import permutations

COLOR_PERMS = list(permutations([0, 1, 2]))


# helper: solve per-node sign system for a set of mapped triples (returns True if solvable)
def solvable_sign_system(mapped_tri_set):
    # nodes involved
    nodes = set()
    for tri in mapped_tri_set:
        nodes.update(tri)
    nodes_list = sorted(nodes)
    idx_map = {v: i for i, v in enumerate(nodes_list)}
    nvars = len(nodes_list)
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


# scoring function
D_BITS = d_bits
E6_TRIADS_SET = set(e6_triads)


def ordered_consistent_for_perm(perm):
    # collect coset triads whose mapped sorted triple is an e6 triad
    matched_coset_triads = [
        t
        for t in coset_triads
        if tuple(sorted((perm[t[0]], perm[t[1]], perm[t[2]]))) in E6_TRIADS_SET
    ]
    if not matched_coset_triads:
        return True
    # try all color permutations to align coset coloring with e6 ordered (0,1,2)
    for col_perm in COLOR_PERMS:
        ok_all = True
        for a, b, c in matched_coset_triads:
            # map node colors through col_perm
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


def score_perm(perm):
    mapped_triads = [
        tuple(sorted((perm[a], perm[b], perm[c]))) for (a, b, c) in coset_triads
    ]
    matched = set(mapped_triads) & E6_TRIADS_SET
    matched_count = len(matched)
    sign_solvable = solvable_sign_system(matched) if matched_count > 0 else False
    ordered_ok = ordered_consistent_for_perm(perm) if matched_count > 0 else True
    # score: prioritize matched_count, then reward solvable, require ordered_ok as strong constraint
    if not ordered_ok:
        return -9999, matched_count, False
    score = (
        matched_count * 10 + (500 if sign_solvable else 0) + (1000 if ordered_ok else 0)
    )
    return score, matched_count, sign_solvable


# local search: greedy pairwise swaps
best_perm = seed.copy()
best_score, best_matched_count, best_solved = score_perm(best_perm)
print("seed score", best_score, best_matched_count, best_solved)
improved = True
iters = 0
while improved and iters < 10000:
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
                best_matched_count = mc
                best_solved = sv
                improved = True
                print(
                    "improved to",
                    best_score,
                    best_matched_count,
                    best_solved,
                    "swap",
                    i,
                    j,
                )
                break
        if improved:
            break

print("final best", best_score, best_matched_count, best_solved)
# Save result
out = {
    "perm": best_perm,
    "score": best_score,
    "matched": best_matched_count,
    "solvable_sign_system": best_solved,
}
with open("artifacts/best_sign_constrained_mapping.json", "w") as f:
    json.dump(out, f, indent=2)
print("wrote artifacts/best_sign_constrained_mapping.json")
