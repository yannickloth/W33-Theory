#!/usr/bin/env python3
"""
Intense local search across selected W indices.
Moves: swap (2-cycle), double-swap (two disjoint swaps), 3-cycle.
Scoring: maximize matched triads; preserve sign solvability if requested.
Writes per-W artifacts: artifacts/intense_local_W{widx}_results.json and a summary.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--w-list", type=str, default="from_summary", help='comma list or "from_summary"'
)
parser.add_argument("--iters", type=int, default=100000, help="SA iterations per W")
parser.add_argument(
    "--workers", type=int, default=4, help="parallel workers for W jobs"
)
parser.add_argument(
    "--preserve-hard",
    action="store_true",
    help="only accept moves that keep sign solvable",
)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument(
    "--move-probs",
    type=str,
    default="0.5,0.3,0.2",
    help="comma probs for swap,double,3cycle",
)
args = parser.parse_args()
random.seed(args.seed)

# load sign-consistent summary to get W list
with open(
    ROOT / "artifacts" / "sign_consistent_summary.json", "r", encoding="utf-8"
) as f:
    sign_summary = json.load(f)
available_w = [entry["W_idx"] for entry in sign_summary]
if args.w_list != "from_summary":
    selected = sorted(int(x) for x in args.w_list.split(","))
else:
    selected = sorted(available_w)
print("Selected W indices:", selected)

# load E6 triads
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]

# sign gauge bits
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
print("Found", len(subspace_list), "subspaces")

# helper functions
from itertools import combinations as comb


def coset_triads_for_W(W):
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    coset_triads = set()
    for u1, u2, u3 in comb(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            coset_triads.add(tuple(sorted((u1, u2, u3))))
    return coset_triads


# solvability checker
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
        rhs = D_BITS.get(tuple(sorted(tri)), 0)
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


# matched triads for mapping
def matched_tris_for_mapping(mapping, coset_triads_set):
    matched = []
    for tri in E6_TRIADS:
        i, j, k = tri
        ct = tuple(sorted((mapping[i], mapping[j], mapping[k])))
        if ct in coset_triads_set:
            matched.append(tri)
    return matched


# move proposals
def propose_move(perm, move_type):
    n = len(perm)
    if move_type == "swap":
        i, j = random.sample(range(n), 2)
        p = perm.copy()
        p[i], p[j] = p[j], p[i]
        return p, ("swap", i, j)
    if move_type == "double":
        i, j, k, l = random.sample(range(n), 4)
        p = perm.copy()
        p[i], p[j] = p[j], p[i]
        p[k], p[l] = p[l], p[k]
        return p, ("double", (i, j), (k, l))
    if move_type == "3cycle":
        i, j, k = random.sample(range(n), 3)
        p = perm.copy()
        p[i], p[j], p[k] = perm[j], perm[k], perm[i]
        return p, ("3cycle", i, j, k)
    # fallback: simple swap
    i, j = random.sample(range(n), 2)
    p = perm.copy()
    p[i], p[j] = p[j], p[i]
    return p, ("swap", i, j)


# scoring function: prefer matched triads count; penalize sign-inconsistency


def score_map(mapping, coset_triads_set):
    matched = matched_tris_for_mapping(mapping, coset_triads_set)
    c = len(matched)
    solv = solvable_sign_system(matched)
    score = c * 10000 - (0 if solv else 1000000)
    return score, c, solv


# run for a single W
def run_for_w(widx):
    print("Running intense local search on W", widx)
    W = subspace_list[widx]
    coset_set = coset_triads_for_W(W)
    # seed mapping: try best from local_swap results if present
    seed_path = ROOT / "artifacts" / f"local_swap_W{widx}_results.json"
    if seed_path.exists():
        seed = json.load(open(seed_path, "r", encoding="utf-8"))["best_mapping"]
    else:
        sign_path = ROOT / "artifacts" / f"sign_consistent_mapping_W{widx}.json"
        if sign_path.exists():
            seed = json.load(open(sign_path, "r", encoding="utf-8"))["mapping"]
        else:
            seed = list(range(27))

    # initial values
    perm = seed.copy()
    s_curr, c_curr, solv_curr = score_map(perm, coset_set)
    best_perm = perm.copy()
    best_score = s_curr
    best_matched = c_curr
    best_solv = solv_curr
    # SA setup
    iters = args.iters
    probs = [float(x) for x in args.move_probs.split(",")]
    move_types = ["swap", "double", "3cycle"]
    alpha = math.exp(math.log(1e-4 / 1.0) / max(iters, 1))
    T = 1.0
    for it in range(iters):
        # pick move
        r = random.random()
        cum = 0.0
        mt = move_types[0]
        for p, m in zip(probs, move_types):
            cum += p
            if r <= cum:
                mt = m
                break
        perm2, meta = propose_move(perm, mt)
        s2, c2, solv2 = score_map(perm2, coset_set)
        if args.preserve_hard and not solv2:
            accept = False
        else:
            delta = s2 - s_curr
            accept = (delta > 0) or (random.random() < math.exp(delta / max(T, 1e-12)))
        if accept:
            perm = perm2
            s_curr = s2
            c_curr = c2
            solv_curr = solv2
            if s2 > best_score and (not args.preserve_hard or solv2):
                best_perm = perm.copy()
                best_score = s2
                best_matched = c2
                best_solv = solv2
                print(f" W{widx} new best it{it} matched {c2} solv {solv2}")
        T = max(T * alpha, 1e-4)
        # periodic writes
        if it % max(1, iters // 10) == 0:
            out = {
                "W_idx": widx,
                "iter": it,
                "current_matched": c_curr,
                "current_solvable": bool(solv_curr),
                "best_matched": int(best_matched),
                "best_solvable": bool(best_solv),
            }
            (ROOT / "artifacts" / f"intense_local_W{widx}_progress.json").write_text(
                json.dumps(out, indent=2), encoding="utf-8"
            )
    # final fine greedy to polish
    improved = True
    mapping = best_perm.copy()
    while improved:
        improved = False
        for i in range(27):
            if improved:
                break
            for j in range(i + 1, 27):
                m2 = mapping.copy()
                m2[i], m2[j] = m2[j], m2[i]
                s2, c2, solv2 = score_map(m2, coset_set)
                if args.preserve_hard and not solv2:
                    continue
                if c2 > best_matched:
                    mapping = m2
                    best_matched = c2
                    best_solv = solv2
                    improved = True
                    print(
                        f" W{widx} final greedy improved to {best_matched} (swap {i},{j})"
                    )
                    break
    out = {
        "W_idx": widx,
        "best_matched": int(best_matched),
        "best_solvable": bool(best_solv),
        "best_mapping": best_perm,
    }
    (ROOT / "artifacts" / f"intense_local_W{widx}_results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(" W", widx, "done: best", best_matched, "solvable", best_solv)
    return out


# dispatch
results = []
if args.workers > 1:
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(run_for_w, w): w for w in selected}
        for fut in as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
            except Exception as e:
                print("Error in worker:", e)
else:
    for w in selected:
        res = run_for_w(w)
        results.append(res)

(ROOT / "artifacts" / "intense_local_summary.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("\nAll jobs finished. Summary written to artifacts/intense_local_summary.json")
