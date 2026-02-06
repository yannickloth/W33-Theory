#!/usr/bin/env python3
"""
Analyze ordered triad counts for the best mappings produced by
`local_swap_with_forbid.py` (forbid tests). Writes `artifacts/forbid_ordered_analysis.json`.
"""
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

# load E6 triads and ordered map
with open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8") as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
with open(ART / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered = json.load(f)
ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered}
coset_colors = json.load(open(ART / "coset_coloring.json", "r", encoding="utf-8"))[
    "colors"
]

# code matrices
G = np.array(
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

# load local-swap-forbid summary
summary = json.load(
    open(ART / "local_swap_with_forbid_summary.json", "r", encoding="utf-8")
)
results = []

# build subspaces (same as other tools)
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

for entry in summary:
    widx = entry["W_idx"]
    best_map = entry["best_mapping"]
    W = subspace_list[widx]
    # build coset triads
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    cw27 = [tuple((np.array(m) @ G % 3).tolist()) for m in cosets]
    coset_triads = set()
    for i, j, k in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
            and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
            and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
        ):
            coset_triads.add(tuple(sorted((i, j, k))))
    # matched and ordered
    matched = []
    ordered_count = 0
    ordered_tris = []
    for tri in E6_TRIADS:
        i, j, k = tri
        u = tuple(sorted((best_map[i], best_map[j], best_map[k])))
        if u in coset_triads:
            matched.append(list(tri))
            # check ordered
            found = False
            for col_perm in permutations([0, 1, 2]):
                new_colors = {}
                new_colors[col_perm[coset_colors[best_map[i]]]] = i
                new_colors[col_perm[coset_colors[best_map[j]]]] = j
                new_colors[col_perm[coset_colors[best_map[k]]]] = k
                if set(new_colors.keys()) != {0, 1, 2}:
                    continue
                v0 = new_colors[0]
                v1 = new_colors[1]
                v2 = new_colors[2]
                if (v0, v1) in ORDERED and ORDERED[(v0, v1)][0] == v2:
                    found = True
                    break
            if found:
                ordered_count += 1
                ordered_tris.append(list(tri))
    results.append(
        {
            "W_idx": widx,
            "matched_count": len(matched),
            "ordered_count": ordered_count,
            "matched": matched,
            "ordered_tris": ordered_tris,
        }
    )

(ART / "forbid_ordered_analysis.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("Wrote artifacts/forbid_ordered_analysis.json")
