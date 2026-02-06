#!/usr/bin/env python3
"""
Diagnostic: for each E6 affine triad, compute whether it has any allowed coset
assignment under ordered-couplings constraints across all W choices and
color permutations. Also try unordered mapping to detect whether ordering is
principal obstruction.
Writes results to artifacts/triad_compatibility_summary.json and
artifacts/unordered_cpsat_results.json
"""
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)

ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered}
triads = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
assert len(triads) == 36

# Setup code/CW matrix and M
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

# find distinct 3-dim subspaces (same method as other scripts)
basis = []
for m in kernel:
    if all(x == 0 for x in m):
        continue
    if not basis:
        basis.append(m)
        continue

    def in_span(m, basis):
        if len(basis) == 1:
            for a in range(3):
                if tuple((a * basis[0][i]) % 3 for i in range(6)) == m:
                    return True
            return False
        if len(basis) == 2:
            for a in range(3):
                for b in range(3):
                    if (
                        tuple(
                            ((a * basis[0][i] + b * basis[1][i]) % 3) for i in range(6)
                        )
                        == m
                    ):
                        return True
            return False
        if len(basis) == 3:
            for a in range(3):
                for b in range(3):
                    for c in range(3):
                        if (
                            tuple(
                                (
                                    (
                                        a * basis[0][i]
                                        + b * basis[1][i]
                                        + c * basis[2][i]
                                    )
                                    % 3
                                )
                                for i in range(6)
                            )
                            == m
                        ):
                            return True
            return False
        return False

    if not in_span(m, basis):
        basis.append(m)
    if len(basis) == 4:
        break

seen = set()
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
        if key not in seen:
            seen.add(key)
            # store the generating basis (a,b,c) so we can reconstruct W by linear combos
            subspace_list.append((a, b, c))

print("Found", len(subspace_list), "distinct 3-dim subspaces (expected 40)")
W_choices = subspace_list

COLOR_PERMS = list(permutations([0, 1, 2]))

# For collecting statistics
triad_global = {tri: {"total_allowed": 0, "per_W_counts": {}} for tri in triads}

for wi, Wb in enumerate(W_choices):
    # build W set
    Wset = set()
    for a, b, c in product(range(3), repeat=3):
        w = tuple((a * Wb[0][i] + b * Wb[1][i] + c * Wb[2][i]) % 3 for i in range(6))
        Wset.add(w)
    # cosets
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in Wset:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    # coset triads
    coset_triads = []
    for i, j, k in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
            and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
            and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
        ):
            coset_triads.append((i, j, k))
    if len(coset_triads) != 36:
        print("W idx", wi, "has", len(coset_triads), "triads (expected 36); skipping")
        continue

    for col_perm in COLOR_PERMS:
        for tri in triads:
            i, j, k = tri
            allowed_count = 0
            for ct in coset_triads:
                for perm_ct in permutations(ct):
                    u1, u2, u3 = perm_ct
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
                    pair = (v0, v1)
                    if pair in ORDERED and ORDERED[pair][0] == v2:
                        allowed_count += 1
            if allowed_count > 0:
                triad_global[tri]["total_allowed"] += allowed_count
            triad_global[tri]["per_W_counts"].setdefault(wi, []).append(allowed_count)

# Summarize
summary = {}
zero_across_all = []
for tri, info in triad_global.items():
    total = info["total_allowed"]
    perW = {int(w): sum(info["per_W_counts"][w]) for w in info["per_W_counts"]}
    summary[str(tri)] = {"total_allowed": total, "per_W_total": perW}
    if total == 0:
        zero_across_all.append(tri)

out_path = ROOT / "artifacts" / "triad_compatibility_summary.json"
out_path.write_text(
    json.dumps({"summary": summary, "zero_across_all": zero_across_all}, indent=2),
    encoding="utf-8",
)
print("Wrote", out_path)

# Quick unordered mapping test (ignore ORDERED pairing)
try:
    from ortools.sat.python import cp_model
except Exception as e:
    print("ortools not available; skipping unordered CP-SAT test:", e)
    ROOT.joinpath("artifacts", "unordered_cpsat_results.json").write_text(
        json.dumps({"ortools_missing": True}), encoding="utf-8"
    )
else:
    unordered_results = []
    for wi, Wb in enumerate(W_choices):
        used = set()
        cosets = []
        for m in messages:
            if m in used:
                continue
            cosets.append(m)
            for w in Wset:
                used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
        cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
        coset_triads = []
        for i, j, k in combinations(range(27), 3):
            if (
                sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
                and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
                and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
            ):
                coset_triads.append((i, j, k))
        if len(coset_triads) != 36:
            continue
        for col_perm in COLOR_PERMS:
            # build allowed un-ordered list
            allowed = {}
            for tri in triads:
                i, j, k = tri
                allowed_list = []
                for ct in coset_triads:
                    for perm_ct in permutations(ct):
                        u1, u2, u3 = perm_ct
                        new_colors = {
                            col_perm[coset_colors[u1]]: i,
                            col_perm[coset_colors[u2]]: j,
                            col_perm[coset_colors[u3]]: k,
                        }
                        if set(new_colors.keys()) != {0, 1, 2}:
                            continue
                        # unordered accept any assignment (no ORDERED check)
                        allowed_list.append((u1, u2, u3))
                allowed[tri] = list(set(allowed_list))
            # quick CP-SAT solve
            model = cp_model.CpModel()
            x = {}
            for i in range(27):
                for u in range(27):
                    x[(i, u)] = model.NewBoolVar(f"x_{i}_{u}")
            for i in range(27):
                model.Add(sum(x[(i, u)] for u in range(27)) == 1)
            for u in range(27):
                model.Add(sum(x[(i, u)] for i in range(27)) == 1)
            yvars = {}
            for tri in triads:
                i, j, k = tri
                ylist = []
                for u1, u2, u3 in allowed[tri]:
                    var = model.NewBoolVar(f"y_{i}_{j}_{k}_{u1}_{u2}_{u3}")
                    yvars[(tri, (u1, u2, u3))] = var
                    model.AddBoolAnd(
                        [x[(i, u1)], x[(j, u2)], x[(k, u3)]]
                    ).OnlyEnforceIf(var)
                    model.AddBoolOr(
                        [x[(i, u1)].Not(), x[(j, u2)].Not(), x[(k, u3)].Not()]
                    ).OnlyEnforceIf(var.Not())
                    ylist.append(var)
                if ylist:
                    model.Add(sum(ylist) == 1)
                else:
                    model.Add(sum([]) == 0)  # unsat
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 30.0
            solver.parameters.num_search_workers = 8
            res = solver.Solve(model)
            if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
                mapping = [-1] * 27
                for i in range(27):
                    for u in range(27):
                        if solver.Value(x[(i, u)]) == 1:
                            mapping[i] = u
                            break
                unordered_results.append(
                    {"W_idx": wi, "col_perm": col_perm, "mapping": mapping}
                )
                print("Found unordered solution for W", wi, "perm", col_perm)
                break
        if unordered_results:
            break

    ROOT.joinpath("artifacts", "unordered_cpsat_results.json").write_text(
        json.dumps(unordered_results, indent=2), encoding="utf-8"
    )
    print("Wrote unordered_cpsat_results.json")
