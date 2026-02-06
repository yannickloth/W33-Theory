#!/usr/bin/env python3
"""
Run CP-SAT feasibility check for all 3-dim subspaces W of ker(M).
For each W and each color permutation, do a fast pre-check (allowed triples per triad).
If a (W, color_perm) passes pre-check, run CP-SAT (time limit) to try to find exact bijection.
"""
import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load artifacts
with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]
ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered}

with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
assert len(E6_TRIADS) == 36

# Code matrices and kernel
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

# enumerate all distinct 3-dim subspaces by spanning combinations of kernel vectors
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
print("Found", len(subspace_list), "distinct 3-dim subspaces (expected 40)")

import argparse

from ortools.sat.python import cp_model

parser = argparse.ArgumentParser()
parser.add_argument(
    "--time", type=int, default=600, help="time per CP-SAT call (seconds)"
)
parser.add_argument("--workers", type=int, default=8, help="num CP-SAT search workers")
parser.add_argument(
    "--stop-on-solution", action="store_true", help="stop when a mapping is found"
)
args = parser.parse_args()

COLOR_PERMS = list(permutations([0, 1, 2]))

for widx, W in enumerate(subspace_list):
    print("\nChecking W idx", widx)
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    if len(cosets) != 27:
        print("  skip W idx", widx, "coset count", len(cosets))
        continue
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    # coset triads
    coset_triads = []
    for u1, u2, u3 in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[u1], cw27[u2])) == 6
            and sum(x != y for x, y in zip(cw27[u1], cw27[u3])) == 6
            and sum(x != y for x, y in zip(cw27[u2], cw27[u3])) == 6
        ):
            coset_triads.append((u1, u2, u3))
    if len(coset_triads) != 36:
        print("  skip W idx", widx, "triad count", len(coset_triads))
        continue

    feasible_found = False
    for col_perm in COLOR_PERMS:
        # quick pre-check
        zero_triads = []
        for tri in E6_TRIADS:
            i, j, k = tri
            allowed = 0
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
                        allowed += 1
            if allowed == 0:
                zero_triads.append(tri)
        if zero_triads:
            print("  col_perm", col_perm, "zero triads count", len(zero_triads))
            continue
        # passes pre-check: build CP-SAT model for this W and col_perm
        print("  col_perm", col_perm, "passes pre-check; building model")
        # build allowed triples map
        allowed = {}
        for tri in E6_TRIADS:
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
                    v0 = new_colors[0]
                    v1 = new_colors[1]
                    v2 = new_colors[2]
                    pair = (v0, v1)
                    if pair in ORDERED and ORDERED[pair][0] == v2:
                        allowed_list.append((u1, u2, u3))
            allowed[tri] = allowed_list

        model = cp_model.CpModel()
        x = {}
        for i in range(27):
            for u in range(27):
                x[(i, u)] = model.NewBoolVar(f"x_{i}_{u}")
        for i in range(27):
            model.Add(sum(x[(i, u)] for u in range(27)) == 1)
        for u in range(27):
            model.Add(sum(x[(i, u)] for i in range(27)) == 1)

        y = {}
        for tri in E6_TRIADS:
            i, j, k = tri
            ylist = []
            for u1, u2, u3 in allowed[tri]:
                var = model.NewBoolVar(f"y_{i}_{j}_{k}_{u1}_{u2}_{u3}")
                y[(tri, (u1, u2, u3))] = var
                model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(
                    var
                )
                model.AddBoolOr(
                    [x[(i, u1)].Not(), x[(j, u2)].Not(), x[(k, u3)].Not()]
                ).OnlyEnforceIf(var.Not())
                ylist.append(var)
            model.Add(sum(ylist) == 1)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = float(args.time)
        solver.parameters.num_search_workers = args.workers
        solver.parameters.maximize = False
        print("    Model built: vars", len(x) + len(y))
        res = solver.Solve(model)
        if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
            print("    Found solution for W", widx, "col_perm", col_perm, "status", res)
            mapping = [-1] * 27
            for i in range(27):
                for u in range(27):
                    if solver.Value(x[(i, u)]) == 1:
                        mapping[i] = u
                        break
            out_path = (
                ROOT
                / "artifacts"
                / f"cpsat_mapping_W{widx}_colperm_{col_perm[0]}{col_perm[1]}{col_perm[2]}.json"
            )
            out_path.parent.mkdir(exist_ok=True)
            out_path.write_text(
                json.dumps({"mapping_e6_to_coset": mapping}, indent=2), encoding="utf-8"
            )
            print("    Wrote", out_path)
            feasible_found = True
            break
        else:
            print(
                "    No solution found for W", widx, "col_perm", col_perm, "status", res
            )
    if feasible_found:
        print("Mapping found; stopping search")
        break

print("Search complete")
