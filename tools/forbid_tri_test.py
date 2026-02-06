#!/usr/bin/env python3
"""
Test if forbidding specific E6 triads allows a sign-solvable 19-match mapping for a given W.
Writes artifact to artifacts/forbid_test_W{w}_forbid_{tag}.json
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np
from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
parser = argparse.ArgumentParser()
parser.add_argument("--w", type=int, required=True)
parser.add_argument(
    "--forbid", type=str, default="", help="comma-separated triads like '0-18-25,1-2-3'"
)
parser.add_argument("--time", type=int, default=300)
parser.add_argument("--workers", type=int, default=4)
args = parser.parse_args()

# load
with open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8") as f:
    heis = json.load(f)
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
with open(ART / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered = json.load(f)
with open(
    ART / "artifacts" if False else ART / "coset_coloring.json", "r", encoding="utf-8"
) as f:
    coset_colors = json.load(f)["colors"]
ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered}

# d_bits
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

if args.w < 0 or args.w >= len(subspace_list):
    raise SystemExit("invalid W index")
W = subspace_list[args.w]
# coset triads
used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
if len(cosets) != 27:
    raise SystemExit("bad coset count")

cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
coset_triads = []
for u1, u2, u3 in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
        and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
        and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
    ):
        coset_triads.append((u1, u2, u3))

# prepare candidate lists
matched_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
ordered_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
for ti, tri in enumerate(E6_TRIADS):
    i, j, k = tri
    for ct in coset_triads:
        for perm_ct in permutations(ct):
            u1, u2, u3 = perm_ct
            matched_candidates[ti].append((u1, u2, u3))
            ok_order = False
            for col_perm in permutations([0, 1, 2]):
                new_colors = {}
                new_colors[col_perm[coset_colors[u1]]] = i
                new_colors[col_perm[coset_colors[u2]]] = j
                new_colors[col_perm[coset_colors[u3]]] = k
                if set(new_colors.keys()) != {0, 1, 2}:
                    continue
                v0, v1, v2 = new_colors[0], new_colors[1], new_colors[2]
                if (v0, v1) in ORDERED and ORDERED[(v0, v1)][0] == v2:
                    ok_order = True
                    break
            if ok_order:
                ordered_candidates[ti].append((u1, u2, u3))

# parse forbid
forbid_list = []
if args.forbid:
    for tstr in args.forbid.split(","):
        parts = tuple(int(x) for x in tstr.split("-"))
        parts = tuple(sorted(parts))
        try:
            ti = E6_TRIADS.index(parts)
            forbid_list.append(ti)
        except ValueError:
            raise SystemExit(f"forbid tri {parts} not an E6 triad")

# build CP-SAT model
model = cp_model.CpModel()
x = {}
for i in range(27):
    for u in range(27):
        x[(i, u)] = model.NewBoolVar(f"x_{i}_{u}")
for i in range(27):
    model.Add(sum(x[(i, u)] for u in range(27)) == 1)
for u in range(27):
    model.Add(sum(x[(i, u)] for i in range(27)) == 1)

y_mat = {}
y_ord = {}
z_mat = {}
z_ord = {}
for ti, tri in enumerate(E6_TRIADS):
    y_m = model.NewBoolVar(f"y_m_{ti}")
    y_o = model.NewBoolVar(f"y_o_{ti}")
    y_mat[ti] = y_m
    y_ord[ti] = y_o
    zlist = []
    for u1, u2, u3 in matched_candidates[ti]:
        z = model.NewBoolVar(f"zm_{ti}_{u1}_{u2}_{u3}")
        i, j, k = tri
        model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(z)
        model.Add(z <= y_m)
        zlist.append(z)
    if zlist:
        model.Add(sum(zlist) >= y_m)
        for z in zlist:
            model.Add(z <= y_m)
    else:
        model.Add(y_m == 0)
    zlist2 = []
    for u1, u2, u3 in ordered_candidates[ti]:
        z = model.NewBoolVar(f"zo_{ti}_{u1}_{u2}_{u3}")
        i, j, k = tri
        model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(z)
        model.Add(z <= y_o)
        zlist2.append(z)
    if zlist2:
        model.Add(sum(zlist2) >= y_o)
        for z in zlist2:
            model.Add(z <= y_o)
    else:
        model.Add(y_o == 0)
    model.Add(y_o <= y_m)

# apply forbids
for ti in forbid_list:
    model.Add(y_mat[ti] == 0)

# enforce signs
s = {i: model.NewBoolVar(f"s_{i}") for i in range(27)}
for ti, tri in enumerate(E6_TRIADS):
    dbit = D_BITS.get(tuple(sorted(tri)))
    if dbit is None:
        continue
    t_int = model.NewIntVar(0, 1, f"t_{ti}")
    i, j, k = tri
    # only enforce parity if tri is matched
    model.Add(s[i] + s[j] + s[k] - 2 * t_int == dbit).OnlyEnforceIf(y_mat[ti])

# objective: maximize matched then ordered
model.Maximize(sum(y_mat.values()) * 1000 + sum(y_ord.values()))

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = float(args.time)
solver.parameters.num_search_workers = int(args.workers)
print("Solving W", args.w, "forbid", args.forbid)
res = solver.Solve(model)
status = solver.StatusName(res)
print("status", status)
if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
    mapping = [-1] * 27
    for i in range(27):
        for u in range(27):
            if solver.Value(x[(i, u)]) == 1:
                mapping[i] = u
                break
    matched_count = sum(
        1 for ti in range(len(E6_TRIADS)) if solver.Value(y_mat[ti]) == 1
    )
    sign_ok = True
    # compute matched triads list
    matched_tris = [
        tuple(sorted(E6_TRIADS[ti]))
        for ti in range(len(E6_TRIADS))
        if solver.Value(y_mat[ti]) == 1
    ]
    # quick GF(2) check
    nodes = sorted({v for t in matched_tris for v in t})
    idx = {v: i for i, v in enumerate(nodes)}
    rows = []
    for t in matched_tris:
        m = 0
        for v in t:
            m |= 1 << idx[v]
        rhs = D_BITS.get(tuple(sorted(t)), 0)
        rows.append((m, rhs))
    pivots = {}
    sign_ok = True
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
            sign_ok = False
            break
    out = {
        "W_idx": args.w,
        "forbid": args.forbid,
        "status": status,
        "matched": matched_count,
        "sign_ok": bool(sign_ok),
        "mapping": mapping,
    }
    (
        ART
        / f'forbid_test_W{args.w}_forbid_{args.forbid.replace(",","_").replace("-","_")}.json'
    ).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("matched", matched_count, "sign_ok", sign_ok)
else:
    print("no solution (status", status, ")")
