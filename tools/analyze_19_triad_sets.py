#!/usr/bin/env python3
"""
Analyze the 19-triad matched sets produced by local_swap_improve_sign_consistent.py.
Computes intersection, frequencies, pairwise Jaccard similarities, and node participation.
Writes artifacts/19_triad_overlap.json
"""
from __future__ import annotations

import json
from itertools import combinations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load summary and per-W results
with open(ROOT / "artifacts" / "local_swap_summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

# load E6 triads
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]

# build messages/kernel/subspaces and cw27 logic to recompute coset triads per W
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

# enumerate subspaces
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

# helper: compute coset triads for W
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
    coset_triads = []
    for u1, u2, u3 in comb(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            coset_triads.append((u1, u2, u3))
    return {tuple(sorted(t)) for t in coset_triads}


# collect matched-triad sets
W_sets = {}
for entry in summary:
    widx = entry["W_idx"]
    infile = ROOT / "artifacts" / f"local_swap_W{widx}_results.json"
    if not infile.exists():
        continue
    data = json.load(open(infile, "r", encoding="utf-8"))
    best_map = data["best_mapping"]
    W = subspace_list[widx]
    coset_set = coset_triads_for_W(W)
    matched = set()
    for tri in E6_TRIADS:
        i, j, k = tri
        ct = tuple(sorted((best_map[i], best_map[j], best_map[k])))
        if ct in coset_set:
            matched.add(tri)
    W_sets[widx] = matched

# compute intersection and frequencies
all_w = sorted(W_sets.keys())
all_sets = [W_sets[w] for w in all_w]
intersection_all = set.intersection(*all_sets) if all_sets else set()
union_all = set.union(*all_sets) if all_sets else set()

# frequencies per triad
freq = {}
for w, s in W_sets.items():
    for tri in s:
        freq[tri] = freq.get(tri, 0) + 1

# pairwise Jaccard
pairwise = {}
for a, b in combinations(all_w, 2):
    A = W_sets[a]
    B = W_sets[b]
    inter = len(A & B)
    uni = len(A | B)
    jacc = inter / uni if uni > 0 else 0.0
    pairwise[f"{a}-{b}"] = {"intersection": inter, "union": uni, "jaccard": jacc}

# node participation counts
node_counts = {w: {i: 0 for i in range(27)} for w in all_w}
for w in all_w:
    for tri in W_sets[w]:
        for v in tri:
            node_counts[w][v] += 1

# aggregate node frequencies across W
node_freq = {i: 0 for i in range(27)}
for tri, c in freq.items():
    for v in tri:
        node_freq[v] += c

out = {
    "W_indices": all_w,
    "intersection_all_size": len(intersection_all),
    "intersection_all": [list(tri) for tri in sorted(intersection_all)],
    "union_all_size": len(union_all),
    "top_triads_by_freq": [
        [list(tri), cnt] for tri, cnt in sorted(freq.items(), key=lambda x: -x[1])[:20]
    ],
    "pairwise": pairwise,
    "node_freq": node_freq,
}

(ROOT / "artifacts" / "19_triad_overlap.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("W indices analyzed:", all_w)
print("Intersection size:", len(intersection_all))
print("Top triads by freq:", out["top_triads_by_freq"][:5])
print("Wrote artifacts/19_triad_overlap.json")
