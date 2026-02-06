#!/usr/bin/env python3
"""
Encode the E6->coset mapping as a CP-SAT problem using OR-Tools.
For each color permutation, build allowed triad assignments consistent with
`artifacts/e6_ordered_couplings.json` and `artifacts/coset_coloring.json` and
attempt to find a bijection mapping that satisfies triad -> coset triad constraints.
"""
import json
from itertools import permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# load artifacts
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]

ORDERED_MAP = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered}

# e6 triads (affine_u_lines)
e6_triads = []
for item in heis["affine_u_lines"]:
    for tri in item["triads"]:
        e6_triads.append(tuple(tri))
assert len(e6_triads) == 36

# coset triads
# reconstruct coset triads from repo code (same as other scripts)
import numpy as np

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
# find a kernel basis (deterministic choice used in other scripts)
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
W_basis = basis[:3]
W = set()
for a, b, c in product(range(3), repeat=3):
    W.add(
        tuple(
            (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
            for i in range(6)
        )
    )
used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))

cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]

from itertools import combinations

coset_triads = []
for i, j, k in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
        and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
        and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
    ):
        coset_triads.append((i, j, k))
coset_triads_set = set(tuple(sorted(t)) for t in coset_triads)
assert len(coset_triads) == 36

# OR-Tools
from ortools.sat.python import cp_model

COLOR_PERMS = list(permutations([0, 1, 2]))

for col_perm in COLOR_PERMS:
    print("\nTrying color permutation", col_perm)
    # build allowed triples for each e6 triad
    allowed = {}
    for tri in e6_triads:
        i, j, k = tri
        allowed_list = []
        for ct in coset_triads:
            for perm_ct in permutations(ct):
                u1, u2, u3 = perm_ct
                # check new colors mapping
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
                if pair in ORDERED_MAP:
                    k_expect, raw = ORDERED_MAP[pair]
                    if k_expect == v2:
                        allowed_list.append((u1, u2, u3))
        allowed[tri] = allowed_list
    lengths = [len(allowed[t]) for t in e6_triads]
    print("allowed triples per triad - min", min(lengths), "max", max(lengths))
    zero_tris = [t for t in e6_triads if len(allowed[t]) == 0]
    if zero_tris:
        print("No allowed triple for some triad under this color perm; skipping")
        print("Example zero triads (up to 10):", zero_tris[:10])
        continue

    # build model
    model = cp_model.CpModel()
    x = {}
    for i in range(27):
        for u in range(27):
            x[(i, u)] = model.NewBoolVar(f"x_{i}_{u}")
    # bijection constraints
    for i in range(27):
        model.Add(sum(x[(i, u)] for u in range(27)) == 1)
    for u in range(27):
        model.Add(sum(x[(i, u)] for i in range(27)) == 1)

    # triad assignment variables
    y = {}
    for tri in e6_triads:
        i, j, k = tri
        ylist = []
        for u1, u2, u3 in allowed[tri]:
            var = model.NewBoolVar(f"y_{i}_{j}_{k}_{u1}_{u2}_{u3}")
            y[(tri, (u1, u2, u3))] = var
            # y -> x[i,u1] & x[j,u2] & x[k,u3]
            model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(var)
            # if not var then not(all three)
            model.AddBoolOr(
                [x[(i, u1)].Not(), x[(j, u2)].Not(), x[(k, u3)].Not()]
            ).OnlyEnforceIf(var.Not())
            ylist.append(var)
        # exactly one allowed triple per triad
        model.Add(sum(ylist) == 1)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0
    solver.parameters.num_search_workers = 8
    print("Model built: vars", len(x) + len(y), "constraints approx", "...")

    res = solver.Solve(model)
    if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
        print("Found solution for color perm", col_perm, "status", res)
        mapping = [-1] * 27
        for i in range(27):
            for u in range(27):
                if solver.Value(x[(i, u)]) == 1:
                    mapping[i] = u
                    break
        out_path = (
            ROOT
            / "artifacts"
            / f"cpsat_mapping_colperm_{col_perm[0]}{col_perm[1]}{col_perm[2]}.json"
        )
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_text(
            json.dumps({"mapping_e6_to_coset": mapping}, indent=2), encoding="utf-8"
        )
        print("Wrote", out_path)
        break
    else:
        print("No solution found (status code", res, ") for color perm", col_perm)

print("Done.")
