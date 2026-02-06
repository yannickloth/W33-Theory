#!/usr/bin/env python3
"""
Run CP-SAT optimization only on a selected subset of W indices.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np
from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--w-list", type=str, default="0,4,5", help="comma-separated W indices to run"
)
parser.add_argument("--time", type=int, default=600, help="seconds per W")
parser.add_argument("--workers", type=int, default=8, help="num CP-SAT search workers")
parser.add_argument("--w-matched", type=float, default=10.0)
parser.add_argument("--w-ordered", type=float, default=20.0)
parser.add_argument(
    "--enforce-signs",
    action="store_true",
    help="enforce parity sign constraints for matched triads",
)
args = parser.parse_args()

# load artifacts
with open(
    ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    heis = json.load(f)
with open(ROOT / "artifacts" / "e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered_coups = json.load(f)
with open(ROOT / "artifacts" / "coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]

ORDERED = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered_coups}
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
assert len(E6_TRIADS) == 36

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
print("Found", len(subspace_list), "distinct 3-dim subspaces (expected 40)")

# d_bits from sign gauge
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

d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_sign.items()}

selected = sorted(int(x) for x in args.w_list.split(","))
print("Running on W indices:", selected)

results = []
for widx in selected:
    if widx < 0 or widx >= len(subspace_list):
        print("Skipping invalid W idx", widx)
        continue
    W = subspace_list[widx]
    print("\nRunning W idx", widx)
    # cosets
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
        print(" skip W idx", widx, "triad count", len(coset_triads))
        continue

    # Precompute candidate assignments
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
                    v0 = new_colors[0]
                    v1 = new_colors[1]
                    v2 = new_colors[2]
                    pair = (v0, v1)
                    if pair in ORDERED and ORDERED[pair][0] == v2:
                        ok_order = True
                        break
                if ok_order:
                    ordered_candidates[ti].append((u1, u2, u3))

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
    z_mat = defaultdict(list)
    z_ord = defaultdict(list)

    for ti, tri in enumerate(E6_TRIADS):
        y_m = model.NewBoolVar(f"y_m_{ti}")
        y_o = model.NewBoolVar(f"y_o_{ti}")
        y_mat[ti] = y_m
        y_ord[ti] = y_o
        for u1, u2, u3 in matched_candidates[ti]:
            z = model.NewBoolVar(f"zm_{ti}_{u1}_{u2}_{u3}")
            i, j, k = tri
            model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(z)
            model.Add(z <= y_m)
            z_mat[ti].append(z)
        if z_mat[ti]:
            model.Add(sum(z_mat[ti]) >= y_m)
            for z in z_mat[ti]:
                model.Add(z <= y_m)
        else:
            model.Add(y_m == 0)
        for u1, u2, u3 in ordered_candidates[ti]:
            z = model.NewBoolVar(f"zo_{ti}_{u1}_{u2}_{u3}")
            i, j, k = tri
            model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(z)
            model.Add(z <= y_o)
            z_ord[ti].append(z)
        if z_ord[ti]:
            model.Add(sum(z_ord[ti]) >= y_o)
            for z in z_ord[ti]:
                model.Add(z <= y_o)
        else:
            model.Add(y_o == 0)
        model.Add(y_o <= y_m)

    if args.enforce_signs:
        s = {i: model.NewBoolVar(f"s_{i}") for i in range(27)}
        for ti, tri in enumerate(E6_TRIADS):
            dbit = d_bits.get(tuple(sorted(tri)))
            if dbit is None:
                continue
            t_int = model.NewIntVar(0, 1, f"t_{ti}")
            i, j, k = tri
            model.Add(s[i] + s[j] + s[k] - 2 * t_int == dbit).OnlyEnforceIf(y_mat[ti])

    total_mat = sum(y_mat.values())
    total_ord = sum(y_ord.values())
    model.Maximize(args.w_matched * total_mat + args.w_ordered * total_ord)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time)
    solver.parameters.num_search_workers = args.workers

    print(" solving: W idx", widx, "time", args.time)
    res = solver.Solve(model)
    status_str = solver.StatusName(res)
    if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
        mapping = [-1] * 27
        for i in range(27):
            for u in range(27):
                if solver.Value(x[(i, u)]) == 1:
                    mapping[i] = u
                    break
        matched = [ti for ti, y in y_mat.items() if solver.Value(y) == 1]
        ordered = [ti for ti, y in y_ord.items() if solver.Value(y) == 1]

        def solvable_sign_system(mapped_tri_set):
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

        matched_tris = [tuple(sorted(E6_TRIADS[ti])) for ti in matched]
        ordered_tris = [tuple(sorted(E6_TRIADS[ti])) for ti in ordered]
        sign_ok = solvable_sign_system(matched_tris)
        print(
            f"  W {widx} status {status_str} matched {len(matched)} ordered {len(ordered)} sign_solvable {sign_ok}"
        )
        out = {
            "W_idx": widx,
            "status": status_str,
            "matched": len(matched),
            "ordered": len(ordered),
            "sign_solvable": bool(sign_ok),
            "mapping": mapping,
        }
        out_path = ROOT / "artifacts" / f"opt_selected_W{widx}_status_{status_str}.json"
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        results.append(out)
    else:
        print(f"  W {widx} no feasible solution found (status {status_str})")

# final summary
(ROOT / "artifacts" / "opt_selected_summary.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("Done. Summary written to artifacts/opt_selected_summary.json")
