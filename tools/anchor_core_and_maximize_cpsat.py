#!/usr/bin/env python3
"""
CP-SAT optimization enforcing the common core triads (from artifacts/19_triad_overlap.json)
for selected W indices. For each W, force y_m[tri_idx] == 1 for each core triad and
maximize matched triads (with optional sign enforcement).
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
    "--w-list",
    type=str,
    default="0,4,5,6,7,8,9,10,11,12,13,14,15",
    help="comma-separated W indices",
)
parser.add_argument("--time", type=int, default=600)
parser.add_argument("--workers", type=int, default=4)
parser.add_argument("--enforce-signs", action="store_true")
parser.add_argument(
    "--forbid",
    type=str,
    default="",
    help="Comma-separated E6 triads like '0-18-25' to forbid from being matched",
)
args = parser.parse_args()

# load heis triads
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
tri_to_idx = {tuple(sorted(t)): i for i, t in enumerate(E6_TRIADS)}

# load core triads
with open(ROOT / "artifacts" / "19_triad_overlap.json", "r", encoding="utf-8") as f:
    overlap = json.load(f)
core_triads = [tuple(sorted(tri)) for tri in overlap.get("intersection_all", [])]
core_indices = [
    tri_to_idx[tri] for tri in core_triads if tuple(sorted(tri)) in tri_to_idx
]
print("Core triads count", len(core_indices))

# d_bits
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
# convert to bits
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
print("Found", len(subspace_list), "subspaces")

selected = sorted(int(x) for x in args.w_list.split(","))
results = []
for widx in selected:
    print("\nAnchored CP-SAT: W idx", widx)
    W = subspace_list[widx]
    # cosets
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
    for u1, u2, u3 in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            coset_triads.append((u1, u2, u3))
    coset_triads_set = {tuple(sorted(t)) for t in coset_triads}

    # precompute candidates
    matched_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
    for ti, tri in enumerate(E6_TRIADS):
        i, j, k = tri
        for ct in coset_triads:
            for perm_ct in permutations(ct):
                u1, u2, u3 = perm_ct
                matched_candidates[ti].append((u1, u2, u3))
    # quick pre-check: are all core triads possible on this W?
    impossible = [ti for ti in core_indices if len(matched_candidates[ti]) == 0]
    if impossible:
        print(
            "  core triads impossible on W",
            widx,
            "skipping; impossible tri indices",
            impossible,
        )
        results.append(
            {"W_idx": widx, "status": "core_impossible", "impossible": impossible}
        )
        continue

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
    z_mat = {}
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

    # apply forbids (if any)
    forbid_indices = set()
    if args.forbid:
        for tstr in args.forbid.split(","):
            parts = tuple(sorted(int(x) for x in tstr.split("-")))
            if tuple(parts) in tri_to_idx:
                forbid_indices.add(tri_to_idx[tuple(parts)])
            else:
                print("Warning: forbid tri", parts, "not an E6 triad")

    # anchor core triads
    for ti in core_indices:
        model.Add(y_mat[ti] == 1)

    # forbid selected triads
    for ti in forbid_indices:
        model.Add(y_mat[ti] == 0)

    # enforce signs if requested
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

    print("  solving anchored model...")
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
        matched_count = len(matched)
        print("  found mapping matched", matched_count, "status", status)
        out = {
            "W_idx": widx,
            "status": status,
            "matched": matched_count,
            "matched_tris": [list(E6_TRIADS[ti]) for ti in matched],
            "mapping": mapping,
        }
        out_path = (
            ROOT / "artifacts" / f"anchor_core_cpsat_W{widx}_status_{status}.json"
        )
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        results.append(out)
    else:
        print("  no solution found (status", status, ")")
        results.append({"W_idx": widx, "status": status})

# write summary
(ROOT / "artifacts" / "anchor_core_cpsat_summary.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("\nDone. Summary written to artifacts/anchor_core_cpsat_summary.json")
