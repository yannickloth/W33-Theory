"""Check full matched triad sets for unsat using pycryptosat"""

import json
import time
from itertools import combinations, product
from pathlib import Path

import numpy as np
from pycryptosat import Solver

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

# load E6 triads
with open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8") as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]

# D_BITS
with open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
D_BITS = {t: (True if s == -1 else False) for t, s in d_map_sign.items()}

# G_matrix and M
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

# reconstruct subspaces
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

# process mapping files
import glob

files = sorted((ART).glob("opt_mapping_W*_status_*.json"))
print("Found", len(files), "mapping files")
for f in files:
    print("\nProcessing", f.name)
    data = json.load(open(f, "r", encoding="utf-8"))
    W_idx = data["W_idx"]
    mapping = data["mapping"]
    W = subspace_list[W_idx]
    # compute coset triads
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    coset_triads_set = {
        tuple(sorted((u1, u2, u3)))
        for u1, u2, u3 in combinations(range(27), 3)
        if sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
        and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
        and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
    }

    matched = []
    for tri in E6_TRIADS:
        u = tuple(sorted((mapping[tri[0]], mapping[tri[1]], mapping[tri[2]])))
        if u in coset_triads_set:
            matched.append(tri)
    print(" matched count", len(matched))

    s = Solver()
    t0 = time.time()
    for tri in matched:
        rhs = D_BITS.get(tri, False)
        s.add_xor_clause([tri[0] + 1, tri[1] + 1, tri[2] + 1], rhs)
    res = s.solve()
    dt = time.time() - t0
    print("  solve result", res, "time", dt)
    try:
        print("  conflict", s.get_conflict())
    except Exception as e:
        print("  get_conflict error", e)
