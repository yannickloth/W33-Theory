#!/usr/bin/env python3
"""
For each 3-dim W, search for a mapping with at least `--min-matched` matched triads
such that for every matched triad the sign parity constraint holds.
Saves any found mappings to artifacts/sign_consistent_mappings_W{widx}.json
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

parser = argparse.ArgumentParser()
parser.add_argument("--min-matched", type=int, default=18)
parser.add_argument("--time", type=int, default=300)
parser.add_argument("--workers", type=int, default=4)
args = parser.parse_args()

# load artifacts
with open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8") as f:
    heis = json.load(f)
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
with open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
D_BITS = {t: (0 if s == 1 else 1) for t, s in d_map_sign.items()}

# code matrices and kernel
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

# find subspaces same as before
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

from ortools.sat.python import cp_model

found_any = []
for widx, W in enumerate(subspace_list):
    print("\nW", widx, "checking")
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
    for u1, u2, u3 in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            coset_triads.add(tuple(sorted((u1, u2, u3))))
    if len(coset_triads) != 36:
        print(" skip W", widx, "triad count", len(coset_triads))
        continue

    # build model: x(i,u), y_m(ti), z assignment variables, s node bits
    model = cp_model.CpModel()
    x = {}
    for i in range(27):
        for u in range(27):
            x[(i, u)] = model.NewBoolVar(f"x_{i}_{u}")
    for i in range(27):
        model.Add(sum(x[(i, u)] for u in range(27)) == 1)
    for u in range(27):
        model.Add(sum(x[(i, u)] for i in range(27)) == 1)

    y_m = {}
    z_vars = {}
    for ti, tri in enumerate(E6_TRIADS):
        y = model.NewBoolVar(f"y_{ti}")
        y_m[ti] = y
        zlist = []
        i, j, k = tri
        for perm_ct in permutations(range(27), 3):
            u1, u2, u3 = perm_ct
            if tuple(sorted((u1, u2, u3))) not in coset_triads:
                continue
            z = model.NewBoolVar(f"z_{ti}_{u1}_{u2}_{u3}")
            model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(z)
            model.Add(z <= y)
            zlist.append(z)
        if zlist:
            model.Add(sum(zlist) >= y)
        else:
            model.Add(y == 0)

    # sign bits
    s = {i: model.NewBoolVar(f"s_{i}") for i in range(27)}
    # parity constraints for matched triads
    for ti, tri in enumerate(E6_TRIADS):
        i, j, k = tri
        db = D_BITS.get(tuple(sorted(tri)))
        if db is None:
            continue
        # s_i + s_j + s_k - 2*t_int == db
        t_int = model.NewIntVar(0, 1, f"t_{ti}")
        model.Add(s[i] + s[j] + s[k] - 2 * t_int == db).OnlyEnforceIf(y_m[ti])

    # require at least min_matched triads
    model.Add(sum(y_m.values()) >= args.min_matched)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time)
    solver.parameters.num_search_workers = args.workers

    print("  Solving W", widx)
    res = solver.Solve(model)
    status = solver.StatusName(res)
    if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
        mapping = [-1] * 27
        for i in range(27):
            for u in range(27):
                if solver.Value(x[(i, u)]) == 1:
                    mapping[i] = u
                    break
        matched = [ti for ti, y in y_m.items() if solver.Value(y) == 1]
        print(" Found sign-consistent mapping for W", widx, "matched", len(matched))
        out = {
            "W_idx": widx,
            "status": status,
            "matched": len(matched),
            "mapping": mapping,
        }
        out_path = ART / f"sign_consistent_mapping_W{widx}.json"
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        found_any.append(out)
    else:
        print(
            " No sign-consistent >=",
            args.min_matched,
            "found for W",
            widx,
            "status",
            status,
        )

print("Done. Found", len(found_any), "mappings")
