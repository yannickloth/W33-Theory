#!/usr/bin/env python3
"""
CP-SAT optimization: for each 3-dim W, maximize a weighted sum of
- matched E6 triads (no order requirement)
- ordered E6 triads (exists color permutation that makes the ordered pair match)

This is per-triad color permissive (we accept any col_perm per triad), and post-checks
sign solvability for the matched set. Results are written to artifacts/cpsat_opt_results.json
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
    "--time-per-w", type=int, default=300, help="seconds per (W) CP-SAT solve"
)
parser.add_argument("--workers", type=int, default=8)
parser.add_argument("--weight-matched", type=int, default=10)
parser.add_argument("--weight-ordered", type=int, default=20)
args = parser.parse_args()

# load artifacts
with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)

ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered}
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]

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

# enumerate distinct 3-dim subspaces
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
print("Found", len(subspace_list), "distinct 3-dim subspaces")


# helper: sign solvability checker (same logic as before)
def solvable_sign_system(mapped_tri_set, d_bits):
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
        rhs = d_bits.get(tri, 0)
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


# d_bits from e6 cubic sign gauge solution
try:
    with open(
        ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8"
    ) as f:
        sdata = json.load(f)
    d_map_sign = {
        tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
    }
    # convert to bits +1->0, -1->1
    d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_sign.items()}
except Exception:
    d_bits = {}

results = []

for widx, W in enumerate(subspace_list):
    print("\nW idx", widx)
    # build cosets
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
        print(" skip W idx", widx, "triads count", len(coset_triads))
        continue

    # precompute lists: for each E6 triad, list candidate coset permutations that could map to it
    matched_candidates = {tri: [] for tri in E6_TRIADS}
    ordered_candidates = {tri: [] for tri in E6_TRIADS}
    for tri in E6_TRIADS:
        i, j, k = tri
        for ct in coset_triads:
            for perm_ct in permutations(ct):
                u1, u2, u3 = perm_ct
                # this permutation is a possible mapping from (i,j,k) -> (u1,u2,u3)
                matched_candidates[tri].append((u1, u2, u3))
                # ordered check: allow if exists a color permutation that makes ordered relation hold
                ok_ordered = False
                for col_perm in permutations([0, 1, 2]):
                    new_colors = {
                        col_perm[coset_colors[u1]]: i,
                        col_perm[coset_colors[u2]]: j,
                        col_perm[coset_colors[u3]]: k,
                    }
                    if set(new_colors.keys()) != {0, 1, 2}:
                        continue
                    v0 = new_colors[0]
                    v1 = new_colors[1]
                    v2 = new_colors[2]
                    if (v0, v1) in ORDERED and ORDERED[(v0, v1)][0] == v2:
                        ok_ordered = True
                        break
                if ok_ordered:
                    ordered_candidates[tri].append((u1, u2, u3))

    # quick sanity: count zeros
    zeros = sum(1 for tri in E6_TRIADS if len(matched_candidates[tri]) == 0)
    print(" matched-candidate zeros:", zeros, " (should be 0)")
    zeros_ord = sum(1 for tri in E6_TRIADS if len(ordered_candidates[tri]) == 0)
    print(" ordered-candidate zeros:", zeros_ord)

    # build CP-SAT model
    model = cp_model.CpModel()
    x = {}
    for i in range(27):
        for u in range(27):
            x[(i, u)] = model.NewBoolVar(f"x_{i}_{u}")
    # bijection
    for i in range(27):
        model.Add(sum(x[(i, u)] for u in range(27)) == 1)
    for u in range(27):
        model.Add(sum(x[(i, u)] for i in range(27)) == 1)

    # matched y vars and ordered z vars
    y_vars = {}
    z_vars = {}
    m_vars = {}
    o_vars = {}
    for tri in E6_TRIADS:
        m_vars[tri] = model.NewBoolVar(f"m_{tri[0]}_{tri[1]}_{tri[2]}")
        o_vars[tri] = model.NewBoolVar(f"o_{tri[0]}_{tri[1]}_{tri[2]}")
        # matched candidates
        ylist = []
        for u1, u2, u3 in matched_candidates[tri]:
            v = model.NewBoolVar(f"y_{tri}_{u1}_{u2}_{u3}")
            y_vars[(tri, u1, u2, u3)] = v
            # y implies the three x's
            model.Add(v <= x[(tri[0], u1)])
            model.Add(v <= x[(tri[1], u2)])
            model.Add(v <= x[(tri[2], u3)])
            # if all three x's true then some y can be 1; enforce at least via linear bound
            model.Add(v >= x[(tri[0], u1)] + x[(tri[1], u2)] + x[(tri[2], u3)] - 2)
            ylist.append(v)
        # m_tri is 1 iff any y in ylist is 1; model m >= y for all, and m <= sum(ylist)
        for v in ylist:
            model.Add(m_vars[tri] >= v)
        if ylist:
            model.Add(m_vars[tri] <= sum(ylist))

        # ordered candidates
        zlist = []
        for u1, u2, u3 in ordered_candidates[tri]:
            v = model.NewBoolVar(f"z_{tri}_{u1}_{u2}_{u3}")
            z_vars[(tri, u1, u2, u3)] = v
            model.Add(v <= x[(tri[0], u1)])
            model.Add(v <= x[(tri[1], u2)])
            model.Add(v <= x[(tri[2], u3)])
            model.Add(v >= x[(tri[0], u1)] + x[(tri[1], u2)] + x[(tri[2], u3)] - 2)
            zlist.append(v)
        for v in zlist:
            model.Add(o_vars[tri] >= v)
        if zlist:
            model.Add(o_vars[tri] <= sum(zlist))

    # objective
    matched_sum = sum(m_vars[t] for t in E6_TRIADS)
    ordered_sum = sum(o_vars[t] for t in E6_TRIADS)
    model.Maximize(
        args.weight_matched * matched_sum + args.weight_ordered * ordered_sum
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time_per_w)
    solver.parameters.num_search_workers = int(args.workers)

    print(" solving: W idx", widx, "time", args.time_per_w)
    res = solver.Solve(model)
    if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
        mapping = [-1] * 27
        for i in range(27):
            for u in range(27):
                if solver.Value(x[(i, u)]) == 1:
                    mapping[i] = u
                    break
        matched_count = int(sum(1 for t in E6_TRIADS if solver.Value(m_vars[t]) == 1))
        ordered_count = int(sum(1 for t in E6_TRIADS if solver.Value(o_vars[t]) == 1))
        # compute matched triads set
        matched_tris = [t for t in E6_TRIADS if solver.Value(m_vars[t]) == 1]
        sign_ok = solvable_sign_system(matched_tris, d_bits)
        print(
            "  found mapping: matched",
            matched_count,
            "ordered",
            ordered_count,
            "sign_ok",
            sign_ok,
        )
        results.append(
            {
                "widx": widx,
                "mapping": mapping,
                "matched": matched_count,
                "ordered": ordered_count,
                "sign_ok": bool(sign_ok),
                "status": res,
            }
        )
        # save immediate artifact
        out_path = ROOT / "artifacts" / f"cpsat_opt_W{widx}.json"
        out_path.write_text(json.dumps(results[-1], indent=2), encoding="utf-8")
    else:
        print("  no solution found (status", res, ")")

# write summary
(ROOT / "artifacts").mkdir(exist_ok=True)
with open(ROOT / "artifacts" / "cpsat_opt_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Done. W results saved to artifacts/cpsat_opt_results.json")
