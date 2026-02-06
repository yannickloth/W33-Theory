#!/usr/bin/env python3
"""
Optimize mapping using CP-SAT: maximize matched E6 triads and ordered triads
(allowing per-triad color choices). Run across all W choices and write best
mappings and a summary to artifacts.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument("--time", type=int, default=300, help="time per W (seconds)")
parser.add_argument("--workers", type=int, default=4, help="num CP-SAT search workers")
parser.add_argument("--w-matched", type=float, default=10.0)
parser.add_argument("--w-ordered", type=float, default=20.0)
parser.add_argument(
    "--save-every", type=int, default=1, help="save per-W results if >0"
)
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

# find kernel basis (deterministic) same as other scripts
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

# helper: GF(2) sign solvability test re-used
# We need d_bits from existing solved sign gauge
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

# If there is sign2heis mapping, convert; else assume heis labeling
try:
    with open(
        ROOT / "artifacts" / "e6_sign_to_heis_perm.json", "r", encoding="utf-8"
    ) as f:
        sign2heis = json.load(f)["perm"]
        sign2heis = {int(k): int(v) for k, v in sign2heis.items()}
    d_map_heis = {
        tuple(sorted((sign2heis[a], sign2heis[b], sign2heis[c]))): s
        for (a, b, c), s in d_map_sign.items()
    }
except Exception:
    d_map_heis = d_map_sign

# d_bits: mapping E6 unordered tri -> bit (0 for +1, 1 for -1)
d_bits = {t: (0 if s == 1 else 1) for t, s in d_map_heis.items()}

from ortools.sat.python import cp_model

results = []
best_global = None

for widx, W in enumerate(subspace_list):
    print("\nChecking W idx", widx)
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
        print(" skipping W idx", widx, "coset count", len(cosets))
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
        print(" skipping W idx", widx, "triad count", len(coset_triads))
        continue

    # Precompute candidate assignments
    matched_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
    ordered_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
    for ti, tri in enumerate(E6_TRIADS):
        i, j, k = tri
        for ct in coset_triads:
            for perm_ct in permutations(ct):
                u1, u2, u3 = perm_ct
                # matched candidate: x[i,u1] & x[j,u2] & x[k,u3]
                matched_candidates[ti].append((u1, u2, u3))
                # check per-triad color permissive ordering: exists col_perm s.t. ordering holds
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
    # bijection
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
        # matched z's
        for u1, u2, u3 in matched_candidates[ti]:
            z = model.NewBoolVar(f"zm_{ti}_{u1}_{u2}_{u3}")
            # z -> (x[i,u1] & x[j,u2] & x[k,u3])
            i, j, k = tri
            model.AddBoolAnd([x[(i, u1)], x[(j, u2)], x[(k, u3)]]).OnlyEnforceIf(z)
            # z implies y_m
            model.Add(z <= y_m)
            z_mat[ti].append(z)
        # enforce OR: z_list => y_m and y_m => sum(z)>=1
        if z_mat[ti]:
            model.Add(sum(z_mat[ti]) >= y_m)
            for z in z_mat[ti]:
                model.Add(z <= y_m)
        else:
            model.Add(y_m == 0)
        # ordered z's
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
        # ordering implies matching
        model.Add(y_o <= y_m)

    # Optional: enforce sign parity consistency for matched triads
    if args.enforce_signs:
        # per-node sign bits (0 for +1, 1 for -1)
        s = {i: model.NewBoolVar(f"s_{i}") for i in range(27)}
        for ti, tri in enumerate(E6_TRIADS):
            # if tri is matched, require s_i + s_j + s_k ≡ d_bit (mod 2)
            dbit = d_bits.get(tuple(sorted(tri)))
            if dbit is None:
                continue
            t_int = model.NewIntVar(0, 1, f"t_{ti}")
            i, j, k = tri
            # s[i] + s[j] + s[k] - 2*t_int == dbit  (enforce only if matched)
            model.Add(s[i] + s[j] + s[k] - 2 * t_int == dbit).OnlyEnforceIf(y_mat[ti])

    # Objective: weighted sum
    total_mat = sum(y_mat.values())
    total_ord = sum(y_ord.values())
    model.Maximize(args.w_matched * total_mat + args.w_ordered * total_ord)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time)
    solver.parameters.num_search_workers = args.workers
    print(
        "  Model built: vars approx",
        len(x)
        + sum(len(v) for v in z_mat.values())
        + sum(len(v) for v in z_ord.values()),
    )

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

        # sign solvability check (GF(2))
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
        if args.save_every > 0:
            out_path = (
                ROOT / "artifacts" / f"opt_mapping_W{widx}_status_{status_str}.json"
            )
            out_path.parent.mkdir(exist_ok=True)
            out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        results.append(out)
        if best_global is None or (
            out["matched"] * args.w_matched + out["ordered"] * args.w_ordered
        ) > (
            best_global["matched"] * args.w_matched
            + best_global["ordered"] * args.w_ordered
        ):
            best_global = out.copy()
    else:
        print(f"  W {widx} no feasible solution found (status {status_str})")

# write summary
summary = {"best": best_global, "all": results}
(ROOT / "artifacts" / "opt_mapping_summary.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)
print("Done. Best overall:", best_global)
