#!/usr/bin/env python3
"""
For a chosen anchor W (default W4), extract its matched triad set and enforce those
triads on target W indices via CP-SAT. Useful to test whether W0 can realize
W4's canonical 19-triad set under sign constraints.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np
from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--anchor-w", type=int, default=4, help="W index to take anchor triads from"
)
parser.add_argument(
    "--targets",
    type=str,
    default="0,4,5,6,7,8,9,10,11,12,13,14,15",
    help="comma list of target W indices",
)
parser.add_argument("--time", type=int, default=300)
parser.add_argument("--workers", type=int, default=4)
parser.add_argument("--enforce-signs", action="store_true")
args = parser.parse_args()

# load heis triads
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
tri_to_idx = {tuple(sorted(t)): i for i, t in enumerate(E6_TRIADS)}

# load anchor mapping and compute anchor triad set
anchor_path = ROOT / "artifacts" / f"local_swap_W{args.anchor_w}_results.json"
if not anchor_path.exists():
    print("Anchor mapping missing:", anchor_path)
    raise SystemExit(1)
anchor = json.load(open(anchor_path, "r", encoding="utf-8"))
anchor_map = anchor["best_mapping"]

# code to compute matched triads for a mapping: requires coset triads for W
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

# find matched triads for anchor W
W_anchor = subspace_list[args.anchor_w]
used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W_anchor:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
coset_triads_anchor = set()
for u1, u2, u3 in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
        and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
        and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
    ):
        coset_triads_anchor.add(tuple(sorted((u1, u2, u3))))
anchor_tris = [
    tri
    for tri in E6_TRIADS
    if tuple(sorted((anchor_map[tri[0]], anchor_map[tri[1]], anchor_map[tri[2]])))
    in coset_triads_anchor
]
print("Anchor triads count:", len(anchor_tris))

# D_BITS
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

# function to run anchored CP-SAT on a target W
from ortools.sat.python import cp_model


def run_on_target(widx):
    print("\nTarget W", widx)
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
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    coset_triads = set()
    for u1, u2, u3 in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            coset_triads.add(tuple(sorted((u1, u2, u3))))
    # precompute candidate assignments
    matched_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
    for ti, tri in enumerate(E6_TRIADS):
        i, j, k = tri
        for ct in coset_triads:
            for perm_ct in permutations(ct):
                u1, u2, u3 = perm_ct
                matched_candidates[ti].append((u1, u2, u3))
    impossible = [
        ti for ti in range(len(E6_TRIADS)) if len(matched_candidates[ti]) == 0
    ]
    if impossible:
        print("  some triads impossible on this W; cannot anchor full set")
    # build model
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
    for ti, tri in enumerate(E6_TRIADS):
        y = model.NewBoolVar(f"y_{ti}")
        y_mat[ti] = y
        z_list = []
        for u1, u2, u3 in matched_candidates[ti]:
            z = model.NewBoolVar(f"z_{ti}_{u1}_{u2}_{u3}")
            i, j, k = tri
            model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(z)
            model.Add(z <= y)
            z_list.append(z)
        if z_list:
            model.Add(sum(z_list) >= y)
            for z in z_list:
                model.Add(z <= y)
        else:
            model.Add(y == 0)
    # anchor all anchor_triads
    for tri in anchor_tris:
        ti = tri_to_idx[tuple(sorted(tri))]
        model.Add(y_mat[ti] == 1)
    # enforce signs
    if args.enforce_signs:
        s = {i: model.NewBoolVar(f"s_{i}") for i in range(27)}
        for ti, tri in enumerate(E6_TRIADS):
            dbit = D_BITS.get(tuple(sorted(tri)))
            if dbit is None:
                continue
            t_int = model.NewIntVar(0, 1, f"t_{ti}")
            i, j, k = tri
            model.Add(s[i] + s[j] + s[k] - 2 * t_int == dbit).OnlyEnforceIf(y_mat[ti])
    total_mat = sum(y_mat.values())
    model.Maximize(total_mat)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time)
    solver.parameters.num_search_workers = int(args.workers)
    res = solver.Solve(model)
    status = solver.StatusName(res)
    if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
        mapping = [-1] * 27
        for i in range(27):
            for u in range(27):
                if solver.Value(x[(i, u)]) == 1:
                    mapping[i] = u
                    break
        matched = [ti for ti, y in y_mat.items() if solver.Value(y) == 1]
        print("  found mapping matched", len(matched), "status", status)
        out = {
            "W_idx": widx,
            "status": status,
            "matched": len(matched),
            "mapping": mapping,
            "matched_tris": [list(E6_TRIADS[ti]) for ti in matched],
        }
        (
            ROOT / "artifacts" / f"anchor_specific_cpsat_W{widx}_status_{status}.json"
        ).write_text(json.dumps(out, indent=2), encoding="utf-8")
        return out
    else:
        print("  no solution found (status", status, ")")
        return {"W_idx": widx, "status": status}


# run on targets
targets = [int(x) for x in args.targets.split(",")]
all_results = []
for t in targets:
    out = run_on_target(t)
    all_results.append(out)
(ROOT / "artifacts" / "anchor_specific_cpsat_summary.json").write_text(
    json.dumps(all_results, indent=2), encoding="utf-8"
)
print("Done. Summary written to artifacts/anchor_specific_cpsat_summary.json")
