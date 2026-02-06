#!/usr/bin/env python3
import json
from itertools import combinations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

s = json.load(open(ART / "sign_satisfiable_analysis.json", "r", encoding="utf-8"))
heis = json.load(
    open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8")
)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
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
# build subspaces
kernel = [p for p in messages if (M @ np.array(p) % 3 == 0).all()]
subs = []
from itertools import combinations as combs
from itertools import product as prod

Sset = set()
for a, b, c in combs(kernel, 3):
    sset = set()
    for coeffs in prod(range(3), repeat=3):
        v = tuple(
            (coeffs[0] * a[i] + coeffs[1] * b[i] + coeffs[2] * c[i]) % 3
            for i in range(6)
        )
        sset.add(v)
    if len(sset) == 27:
        key = tuple(sorted(sset))
        if key not in Sset:
            Sset.add(key)
            subs.append(sset)

for item in s:
    fname = item["file"]
    data = json.load(open(ART / fname, "r", encoding="utf-8"))
    W_idx = data["W_idx"]
    W = subs[W_idx]
    # coset triads
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
    for i, j, k in combs(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
            and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
            and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
        ):
            coset_triads.add(tuple(sorted((i, j, k))))
    mapping = data["mapping"]
    matched = []
    for tri in E6_TRIADS:
        u = tuple(sorted((mapping[tri[0]], mapping[tri[1]], mapping[tri[2]])))
        if u in coset_triads:
            matched.append(tri)
    matched = set(matched)
    best = set(tuple(t) for t in item["best_subset"])
    missing = matched - best
    print(
        f"{fname}: matched {len(matched)} best {len(best)} dropped {len(missing)} => {sorted([list(t) for t in missing])}"
    )
