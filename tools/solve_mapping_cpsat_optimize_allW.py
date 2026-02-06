#!/usr/bin/env python3
"""
CP-SAT optimization across all 3-dim W: maximize matched E6 triads and ordered
triads (per-triad color permissive). For each W, iterate: find best mapping, if
mapping is not sign-solvable then forbid that mapping and continue until time
budget per-W is exhausted or we find a sign-solvable mapping.

Writes per-W artifacts to artifacts/cpsat_opt_W{widx}_best.json and a summary
artifacts/cpsat_opt_summary.json
"""
from __future__ import annotations

import json
import time
from itertools import combinations, permutations, product
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[1]

# parameters
TIME_PER_W = 300  # seconds per W by default (5 minutes)
WORKERS = 8
WEIGHT_MATCHED = 1
WEIGHT_ORDERED = 2

# load data
with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered_coups = json.load(f)
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]
with open(
    ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8"
) as f:
    sdata = json.load(f)

ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered_coups}
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
assert len(E6_TRIADS) == 36

# build d_bits from gauge solution (for sign solvability test)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
# In these scripts we assume d_map_sign is in the E6 labeling.
d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_sign.items()}

# helpers


def solvable_sign_system(mapped_tri_set: List[Tuple[int, int, int]]) -> bool:
    # mapped_tri_set in sorted E6 triad form
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


# code matrices and grading M
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

# find kernel and distinct 3-dim subspaces (same deterministic method used earlier)
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]
basis = []
for m in kernel:
    if all(x == 0 for x in m):
        continue
    if not basis:
        basis.append(m)
        continue

    def in_span_local(mv, basis_local):
        if len(basis_local) == 1:
            for a in range(3):
                if tuple((a * basis_local[0][i]) % 3 for i in range(6)) == mv:
                    return True
            return False
        if len(basis_local) == 2:
            for a in range(3):
                for b in range(3):
                    if (
                        tuple(
                            ((a * basis_local[0][i] + b * basis_local[1][i]) % 3)
                            for i in range(6)
                        )
                        == mv
                    ):
                        return True
            return False
        if len(basis_local) == 3:
            for a in range(3):
                for b in range(3):
                    for c in range(3):
                        if (
                            tuple(
                                (
                                    (
                                        a * basis_local[0][i]
                                        + b * basis_local[1][i]
                                        + c * basis_local[2][i]
                                    )
                                    % 3
                                )
                                for i in range(6)
                            )
                            == mv
                        ):
                            return True
            return False
        return False

    if not in_span_local(m, basis):
        basis.append(m)
    if len(basis) == 4:
        break
# enumerate distinct 3-subspaces
subspaces = set()
subspace_list = []
for a, b, c in combinations(basis, 3):
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

summary = []

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
        print("  skip: coset count", len(cosets))
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
        print("  skip: triad count", len(coset_triads))
        continue

    # build oriented permutations list for all coset triads
    oriented_perms = []
    for ct in coset_triads:
        for perm_ct in permutations(ct):
            oriented_perms.append(perm_ct)

    best_for_W = {
        "objective": -1e9,
        "mapping": None,
        "matched": 0,
        "ordered": 0,
        "sign_solved": False,
    }
    start_time = time.time()
    forbidden_assignments = []
    iteration = 0

    while time.time() - start_time < TIME_PER_W:
        iteration += 1
        model = cp_model.CpModel()
        # x[i,u] mapping variables
        x = {}
        for i in range(27):
            for u in range(27):
                x[(i, u)] = model.NewBoolVar(f"x_{i}_{u}")
        # bijection
        for i in range(27):
            model.Add(sum(x[(i, u)] for u in range(27)) == 1)
        for u in range(27):
            model.Add(sum(x[(i, u)] for i in range(27)) == 1)

        # y variables (oriented) and matched flags
        y = {}  # y[(t_idx, u1,u2,u3)]
        matched = []
        ordered_y_list = []
        for t_idx, (i, j, k) in enumerate(E6_TRIADS):
            y_list_for_t = []
            for u1, u2, u3 in oriented_perms:
                var = model.NewBoolVar(f"y_t{t_idx}_{u1}_{u2}_{u3}")
                y[(t_idx, u1, u2, u3)] = var
                # link: var -> x[i,u1] & x[j,u2] & x[k,u3]
                model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(
                    var
                )
                model.AddBoolOr(
                    [x[(i, u1)].Not(), x[(j, u2)].Not(), x[(k, u3)].Not()]
                ).OnlyEnforceIf(var.Not())
                y_list_for_t.append(var)
                # ordered indicator: if ORDERED[(i,j)] exists and equals k then this orientation is ordered
                if (i, j) in ORDERED and ORDERED[(i, j)][0] == k:
                    ordered_y_list.append(var)
            # matched flag m_t
            m_t = model.NewBoolVar(f"m_{t_idx}")
            # sum(y_list_for_t) >= m_t and <= m_t * N
            model.Add(sum(y_list_for_t) >= m_t)
            model.Add(sum(y_list_for_t) <= m_t * len(y_list_for_t))
            matched.append(m_t)

        # objective
        obj_terms = []
        for m_t in matched:
            obj_terms.append(m_t * WEIGHT_MATCHED)
        for v in ordered_y_list:
            obj_terms.append(v * WEIGHT_ORDERED)
        model.Maximize(sum(obj_terms))

        # Add forbidden assignments (ban exact x pattern found previously)
        for ass in forbidden_assignments:
            # list of (xvars, assignment tuple)
            xvars = [x[(i, u)] for i in range(27) for u in range(27)]
            model.AddForbiddenAssignments(xvars, [ass])

        solver = cp_model.CpSolver()
        time_left = TIME_PER_W - (time.time() - start_time)
        if time_left < 1.0:
            break
        solver.parameters.max_time_in_seconds = max(1.0, min(30.0, time_left))
        solver.parameters.num_search_workers = WORKERS
        # solve
        res = solver.Solve(model)

        if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
            # extract mapping
            mapping = [-1] * 27
            for i in range(27):
                for u in range(27):
                    if solver.Value(x[(i, u)]) == 1:
                        mapping[i] = u
                        break
            matched_list = [
                E6_TRIADS[idx]
                for idx, m_t in enumerate(matched)
                if solver.Value(m_t) == 1
            ]
            ordered_count = sum(1 for v in ordered_y_list if solver.Value(v) == 1)
            obj_val = (
                sum(solver.Value(m_t) for m_t in matched) * WEIGHT_MATCHED
                + ordered_count * WEIGHT_ORDERED
            )
            sign_ok = solvable_sign_system(matched_list)
            print(
                f"  iter {iteration} found obj {obj_val} matched {len(matched_list)} ordered {ordered_count} sign_ok {sign_ok}"
            )
            # record best
            if obj_val > best_for_W["objective"]:
                best_for_W.update(
                    {
                        "objective": obj_val,
                        "mapping": mapping,
                        "matched": len(matched_list),
                        "ordered": ordered_count,
                        "sign_solved": sign_ok,
                    }
                )
                # write artifact
                out_path = ROOT / "artifacts" / f"cpsat_opt_W{widx}_best.json"
                out_path.parent.mkdir(exist_ok=True)
                out_path.write_text(json.dumps(best_for_W, indent=2), encoding="utf-8")
            if sign_ok:
                print("  Sign-solvable mapping found for W", widx)
                break
            # otherwise forbid this exact mapping and continue
            xvars = [x[(i, u)] for i in range(27) for u in range(27)]
            assignment = tuple(
                int(mapping[i] == u) for i in range(27) for u in range(27)
            )
            forbidden_assignments.append(assignment)
        else:
            print("  No solution (status", res, ") in iter", iteration)
            break
        # end iter loop
    summary.append({"W_idx": widx, "best": best_for_W})

# write summary
(ROOT / "artifacts" / "cpsat_opt_summary.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)
print("\nAll W processed. Summary written to artifacts/cpsat_opt_summary.json")
