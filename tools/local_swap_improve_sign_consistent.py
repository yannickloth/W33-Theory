#!/usr/bin/env python3
"""
Local swap + simulated-anneal improvement starting from each sign-consistent mapping.
Targets the mappings in artifacts/sign_consistent_summary.json and attempts to
increase the number of matched E6 triads > 18 while preserving sign solvability.

Writes per-W results to artifacts/local_swap_W{widx}_results.json and a summary
artifacts/local_swap_summary.json.
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
parser.add_argument(
    "--w-list", type=str, default="from_summary", help='comma list or "from_summary"'
)
parser.add_argument("--sa-iters", type=int, default=20000, help="SA iterations per W")
parser.add_argument(
    "--greedy-rounds", type=int, default=3, help="number of full greedy passes"
)
parser.add_argument(
    "--preserve-hard",
    action="store_true",
    help="only accept moves that keep sign solvable",
)
parser.add_argument("--seed", type=int, default=0)
args = parser.parse_args()
random.seed(args.seed)

# load E6 triads and sign gauge
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
assert len(E6_TRIADS) == 36

# d_bits from gauge
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
# convert to bits: +1 -> 0, -1 -> 1
D_BITS = {t: (0 if s == 1 else 1) for t, s in d_map_sign.items()}

# build messages/kernel/subspaces same as other tools
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
print("Found", len(subspace_list), "distinct 3-dim subspaces (expected 40)")

# load sign_consistent list
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


# solvability checker (GF(2)) using E6 triad indexing
def solvable_sign_system(mapped_tri_set):
    # mapped_tri_set: iterable of E6 triads (tuples of E6 node indices)
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


# helper: matched triads count and list for a mapping (E6->coset mapping)
def matched_tris_for_mapping(mapping, coset_triads_set):
    matched = []
    for tri in E6_TRIADS:
        i, j, k = tri
        ct = tuple(sorted((mapping[i], mapping[j], mapping[k])))
        if ct in coset_triads_set:
            matched.append(tri)
    return matched


results = []

for widx in selected:
    if widx < 0 or widx >= len(subspace_list):
        print("Skipping invalid W idx", widx)
        continue
    W = subspace_list[widx]
    print("\nProcessing W idx", widx)
    # cosets
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    if len(cosets) != 27:
        print(" skip W idx", widx, "coset count", len(cosets))
        continue
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    coset_triads = []
    for u1, u2, u3 in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            coset_triads.append((u1, u2, u3))
    if len(coset_triads) != 36:
        print(" skip W idx", widx, "triad count", len(coset_triads))
        continue
    coset_triads_set = {tuple(sorted(t)) for t in coset_triads}

    # load base mapping
    map_path = ROOT / "artifacts" / f"sign_consistent_mapping_W{widx}.json"
    if not map_path.exists():
        print(" mapping file missing for W", widx)
        continue
    with open(map_path, "r", encoding="utf-8") as f:
        mdata = json.load(f)
    mapping = list(mdata["mapping"])

    initial_matched_list = matched_tris_for_mapping(mapping, coset_triads_set)
    initial_matched = len(initial_matched_list)
    initial_solvable = solvable_sign_system(initial_matched_list)
    print(" initial matched", initial_matched, "solvable", initial_solvable)

    best_mapping = mapping.copy()
    best_matched = initial_matched
    best_solvable = initial_solvable

    # Greedy improvement: first-improvement swap scan
    improved = True
    greedy_pass = 0
    while improved and greedy_pass < args.greedy_rounds:
        improved = False
        greedy_pass += 1
        for i in range(27):
            if improved:
                break
            for j in range(i + 1, 27):
                m2 = mapping.copy()
                m2[i], m2[j] = m2[j], m2[i]
                matched2 = matched_tris_for_mapping(m2, coset_triads_set)
                if args.preserve_hard and not solvable_sign_system(matched2):
                    continue
                c2 = len(matched2)
                if c2 > best_matched:
                    mapping = m2
                    best_matched = c2
                    best_mapping = m2.copy()
                    best_solvable = solvable_sign_system(matched2)
                    improved = True
                    print(f"  greedy improved to {best_matched} (swap {i},{j})")
                    break
        if not improved:
            print("  greedy pass", greedy_pass, "no improvement")

    # Simulated annealing (soft/hard depending on flag)
    perm = mapping.copy()
    score_curr = len(matched_tris_for_mapping(perm, coset_triads_set))
    solv_curr = solvable_sign_system(matched_tris_for_mapping(perm, coset_triads_set))

    # scoring: prefer higher matched and solvable ones
    def score_map(perm):
        matched = matched_tris_for_mapping(perm, coset_triads_set)
        c = len(matched)
        solv = solvable_sign_system(matched)
        return c * 1000 - (0 if solv else 100000), c, solv

    s_curr, c_curr, solv_curr = score_map(perm)
    best_sa = {
        "perm": perm.copy(),
        "score": s_curr,
        "matched": c_curr,
        "solv": solv_curr,
    }

    T0 = 1.0
    T_min = 1e-4
    iters = args.sa_iters
    if iters > 0:
        alpha = math.exp(math.log(T_min / T0) / max(iters, 1))
        T = T0
        for it in range(iters):
            i, j = random.sample(range(27), 2)
            perm2 = perm.copy()
            perm2[i], perm2[j] = perm2[j], perm2[i]
            s2, c2, solv2 = score_map(perm2)
            if args.preserve_hard and not solv2:
                # disallow non-solvable states if hard flag set
                accept = False
            else:
                delta = s2 - s_curr
                accept = (delta > 0) or (
                    random.random() < math.exp(delta / max(T, 1e-12))
                )
            if accept:
                perm = perm2
                s_curr = s2
                c_curr = c2
                solv_curr = solv2
                if solv2 and (
                    c2 > best_sa["matched"]
                    or (c2 == best_sa["matched"] and s2 > best_sa["score"])
                ):
                    best_sa = {
                        "perm": perm.copy(),
                        "score": s2,
                        "matched": c2,
                        "solv": solv2,
                    }
                    print(f"  SA new best (it {it}) matched {c2} solv {solv2}")
            T = max(T * alpha, T_min)
            if it % (max(1, iters // 10)) == 0:
                pass

    # final greedy from best SA
    final_mapping = best_sa["perm"]
    final_improved = True
    while final_improved:
        final_improved = False
        for i in range(27):
            if final_improved:
                break
            for j in range(i + 1, 27):
                m2 = final_mapping.copy()
                m2[i], m2[j] = m2[j], m2[i]
                matched2 = matched_tris_for_mapping(m2, coset_triads_set)
                if args.preserve_hard and not solvable_sign_system(matched2):
                    continue
                c2 = len(matched2)
                if c2 > best_matched:
                    final_mapping = m2
                    best_matched = c2
                    best_mapping = m2.copy()
                    best_solvable = solvable_sign_system(matched2)
                    final_improved = True
                    print(f"  final greedy improved to {best_matched} (swap {i},{j})")
                    break

    # record results
    out = {
        "W_idx": widx,
        "initial_matched": initial_matched,
        "initial_solvable": bool(initial_solvable),
        "best_matched": int(best_matched),
        "best_solvable": bool(best_solvable),
        "improved": int(best_matched) > int(initial_matched),
        "initial_mapping": mapping if isinstance(mapping, list) else None,
        "best_mapping": best_mapping,
    }
    out_path = ROOT / "artifacts" / f"local_swap_W{widx}_results.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        " W",
        widx,
        "done: initial",
        initial_matched,
        "best",
        best_matched,
        "solvable",
        best_solvable,
    )
    results.append(out)

# write summary
(ROOT / "artifacts" / "local_swap_summary.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("\nAll done. Summary written to artifacts/local_swap_summary.json")
