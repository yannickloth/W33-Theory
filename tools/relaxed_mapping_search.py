#!/usr/bin/env python3
"""
Greedy multi-restart relaxed mapping search.
Maximizes: weight_matched * matched_triads + weight_ordered * ordered_satisfied + sign_bonus if sign solvable.
Saves `artifacts/relaxed_best_mapping.json` with diagnostics and mapping.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument(
    "--restarts", type=int, default=120, help="number of random restarts"
)
parser.add_argument(
    "--iter", type=int, default=2000, help="max iterations (swaps) per restart"
)
parser.add_argument("--weight-matched", type=float, default=10.0)
parser.add_argument("--weight-ordered", type=float, default=20.0)
parser.add_argument("--sign-bonus", type=float, default=1000.0)
parser.add_argument(
    "--global-color",
    action="store_true",
    default=True,
    help="enforce a global color perm when counting ordered satisfaction",
)
parser.add_argument(
    "--no-global-color",
    dest="global_color",
    action="store_false",
    help="allow per-triad color choice (looser)",
)
args = parser.parse_args()

# load artifacts
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
with open(
    ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8"
) as f:
    sdata = json.load(f)
with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered_coups = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]

# sign->heis perm might be available
try:
    with open(
        ROOT / "artifacts" / "e6_sign_to_heis_perm.json", "r", encoding="utf-8"
    ) as f:
        sign2heis = json.load(f)["perm"]
        sign2heis = {int(k): int(v) for k, v in sign2heis.items()}
except Exception:
    sign2heis = None

# build d_bits (mapping of unordered E6 triples -> bit)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
if sign2heis is not None:
    d_map_heis = {
        tuple(sorted((sign2heis[a], sign2heis[b], sign2heis[c]))): s
        for (a, b, c), s in d_map_sign.items()
    }
else:
    # fallback: assume triple ids already in heis labeling
    d_map_heis = d_map_sign
# bits: +1->0, -1->1
d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_heis.items()}

# E6 triads (affine_u_lines)
e6_triads = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
E6_TRIS = set(e6_triads)

# reconstruct coset triads (deterministic kernel choice used across repo)
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
# pick canonical W basis as other scripts did
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
W_basis = basis[:3]
W = set()
for a, b, c in product(range(3), repeat=3):
    W.add(
        tuple(
            (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
            for i in range(6)
        )
    )

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

# ORDERED map
ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered_coups}
COLOR_PERMS = list(permutations([0, 1, 2]))

# helpers


def solvable_sign_system(mapped_tri_set):
    # mapped_tri_set is set of sorted E6 triads
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
        rhs = d_bits.get(tri, 0)
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


def best_color_perm_and_ordered_count(perm, matched_coset_tris, global_color=True):
    # perm: list mapping coset node -> e6 id
    if not matched_coset_tris:
        return 0, None
    if global_color:
        best = (0, None)
        for col_perm in COLOR_PERMS:
            cnt = 0
            for u1, u2, u3 in matched_coset_tris:
                ok = False
                for perm_ct in permutations((u1, u2, u3)):
                    a, b, c = perm_ct
                    new_colors = {
                        col_perm[coset_colors[a]]: perm[a],
                        col_perm[coset_colors[b]]: perm[b],
                        col_perm[coset_colors[c]]: perm[c],
                    }
                    if set(new_colors.keys()) != {0, 1, 2}:
                        continue
                    if (new_colors[0], new_colors[1]) in ORDERED and ORDERED[
                        (new_colors[0], new_colors[1])
                    ][0] == new_colors[2]:
                        ok = True
                        break
                if ok:
                    cnt += 1
            if cnt > best[0]:
                best = (cnt, col_perm)
        return best
    else:
        # per-triad permissive: count triads that have any orientation/col_perm satisfying ORDERED
        cnt = 0
        for u1, u2, u3 in matched_coset_tris:
            ok = False
            for col_perm in COLOR_PERMS:
                for perm_ct in permutations((u1, u2, u3)):
                    a, b, c = perm_ct
                    new_colors = {
                        col_perm[coset_colors[a]]: perm[a],
                        col_perm[coset_colors[b]]: perm[b],
                        col_perm[coset_colors[c]]: perm[c],
                    }
                    if set(new_colors.keys()) != {0, 1, 2}:
                        continue
                    if (new_colors[0], new_colors[1]) in ORDERED and ORDERED[
                        (new_colors[0], new_colors[1])
                    ][0] == new_colors[2]:
                        ok = True
                        break
                if ok:
                    break
            if ok:
                cnt += 1
        return cnt, None


def score_perm(perm):
    mapped_triads = [
        tuple(sorted((perm[a], perm[b], perm[c]))) for (a, b, c) in coset_triads
    ]
    matched = set(mapped_triads) & E6_TRIS
    matched_count = len(matched)
    # matched_coset_tris collect the coset triads whose sorted mapped triple is an E6 triad
    matched_coset_tris = [
        ct
        for ct in coset_triads
        if tuple(sorted((perm[ct[0]], perm[ct[1]], perm[ct[2]]))) in E6_TRIS
    ]
    ordered_count, best_col = best_color_perm_and_ordered_count(
        perm, matched_coset_tris, args.global_color
    )
    sign_solvable = solvable_sign_system(matched)
    score = (
        matched_count * args.weight_matched
        + ordered_count * args.weight_ordered
        + (args.sign_bonus if sign_solvable else 0.0)
    )
    return score, matched_count, ordered_count, sign_solvable, best_col


# main loop
best_global = {"score": -1e9}
seed = None
try:
    with open(
        ROOT / "artifacts" / "best_sign_constrained_mapping_multi.json", "r"
    ) as f:
        seed = json.load(f)["perm"]
except Exception:
    try:
        with open(ROOT / "artifacts" / "best_sign_constrained_mapping.json", "r") as f:
            seed = json.load(f)["perm"]
    except Exception:
        seed = list(range(27))

for restart in range(args.restarts):
    if restart == 0:
        perm = seed.copy()
    else:
        perm = list(range(27))
        random.shuffle(perm)
    cur_score, cur_matched, cur_ordered, cur_solved, cur_col = score_perm(perm)
    improved = True
    iters = 0
    while improved and iters < args.iter:
        improved = False
        iters += 1
        # try pairwise swaps
        for i in range(27):
            for j in range(i + 1, 27):
                p2 = perm.copy()
                p2[i], p2[j] = p2[j], p2[i]
                s, mc, oc, sv, bc = score_perm(p2)
                if s > cur_score:
                    perm = p2
                    cur_score = s
                    cur_matched = mc
                    cur_ordered = oc
                    cur_solved = sv
                    cur_col = bc
                    improved = True
                    break
            if improved:
                break
    print(
        f"restart {restart} best_score {cur_score:.1f} matched {cur_matched} ordered {cur_ordered} solved {cur_solved}"
    )
    if cur_score > best_global.get("score", -1e9):
        best_global = {
            "score": cur_score,
            "perm": perm.copy(),
            "matched": cur_matched,
            "ordered": cur_ordered,
            "solved": cur_solved,
            "col_perm": cur_col,
        }
        with open(ROOT / "artifacts" / "relaxed_best_mapping.json", "w") as f:
            json.dump(best_global, f, indent=2, default=str)

print("Done. Best so far:")
print(best_global)
