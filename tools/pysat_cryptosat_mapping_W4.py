#!/usr/bin/env python3
"""Use PySAT encoders to build exact-one constraints and CryptoMiniSat (pycryptosat)
for XOR parity clauses to search for a bijection+sign assignment for W4's anchor tricouplings.

- Uses IDPool to assign consistent variable numbers for x_i_u, s_i, and z vars
- Encodes exact-one (equals 1) for rows and columns via CardEnc (seqcounter)
- Adds z -> x implications and x triple -> z clause
- Adds XOR parity constraints for triads with known D_BITS
- Solves with pycryptosat for fast XOR reasoning

If a valid mapping+signs is found, writes artifact `artifacts/pysat_cryptosat_W4_mapping_signs.json`.
"""
import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np

try:
    from pysat.card import CardEnc
    from pysat.formula import IDPool
except Exception as e:
    print("Missing PySAT (python-sat) dependency:", e)
    raise SystemExit(1)

try:
    from pycryptosat import Solver
except Exception as e:
    print("Missing pycryptosat dependency:", e)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

# load heisenberg triads and D_BITS
with open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8") as f:
    heis = json.load(f)
E6_TRIADS = [tuple(tri) for item in heis["affine_u_lines"] for tri in item["triads"]]
tri_to_idx = {tuple(sorted(t)): i for i, t in enumerate(E6_TRIADS)}

with open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
D_BITS = {t: (0 if s == 1 else 1) for t, s in d_map_sign.items()}

# choose W index
W_idx = 4
# reconstruct coset triads for W
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
W = subspace_list[W_idx]
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

# load anchor matched triads for W4
anchor_file = ART / f"anchor_specific_cpsat_W{W_idx}_status_OPTIMAL.json"
if not anchor_file.exists():
    print("Anchor mapping missing for W4; aborting")
    raise SystemExit(1)
anchor = json.load(open(anchor_file, "r", encoding="utf-8"))
matched_tris = [tuple(sorted(tri)) for tri in anchor.get("matched_tris", [])]
print("Using anchor matched triads count:", len(matched_tris))

# build candidate assignments for each triad
matched_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
for ti, tri in enumerate(E6_TRIADS):
    i, j, k = tri
    for ct in coset_triads:
        for perm_ct in permutations(ct):
            u1, u2, u3 = perm_ct
            matched_candidates[ti].append((u1, u2, u3))

# vpool and variable ids
vpool = IDPool()
# x vars
x_var = {(i, u): vpool.id(f"x_{i}_{u}") for i in range(27) for u in range(27)}
# s vars
s_var = {i: vpool.id(f"s_{i}") for i in range(27)}
# create solver
solver = Solver()
cnf_count = 0
# encode exact-one for rows and columns using seqcounter
print("Adding exact-one constraints for rows (27)")
for i in range(27):
    lits = [x_var[(i, u)] for u in range(27)]
    enc = CardEnc.equals(lits=lits, bound=1, encoding=1, vpool=vpool)
    for cl in enc.clauses:
        solver.add_clause(cl)
        cnf_count += 1
print("Adding exact-one constraints for columns (27)")
for u in range(27):
    lits = [x_var[(i, u)] for i in range(27)]
    enc = CardEnc.equals(lits=lits, bound=1, encoding=1, vpool=vpool)
    for cl in enc.clauses:
        solver.add_clause(cl)
        cnf_count += 1

# add z vars and mapping clauses for required triads
z_vars = {}
z_count = 0
print("Adding z variables and z<->x constraints for required triads")
for tri in matched_tris:
    ti = tri_to_idx[tuple(sorted(tri))]
    zlist = []
    i, j, k = tri
    for u1, u2, u3 in matched_candidates[ti]:
        zv = vpool.id(f"z_{ti}_{u1}_{u2}_{u3}")
        z_vars[(ti, u1, u2, u3)] = zv
        z_count += 1
        # z => x's
        solver.add_clause([-zv, x_var[(i, u1)]])
        solver.add_clause([-zv, x_var[(j, u2)]])
        solver.add_clause([-zv, x_var[(k, u3)]])
        cnf_count += 3
        # x triple => z (if all three x true then z true)
        solver.add_clause([-x_var[(i, u1)], -x_var[(j, u2)], -x_var[(k, u3)], zv])
        cnf_count += 1
        zlist.append(zv)
    if not zlist:
        print("No match candidates for required tri", tri, "on W4; aborting")
        raise SystemExit(1)
    solver.add_clause(zlist)
    cnf_count += 1

# XOR parity clauses for required triads with known D_BITS
xor_count = 0
for tri in matched_tris:
    dbit = D_BITS.get(tuple(sorted(tri)))
    if dbit is None:
        continue
    a, b, c = s_var[tri[0]], s_var[tri[1]], s_var[tri[2]]
    solver.add_xor_clause([a, b, c], bool(dbit))
    xor_count += 1

print("CNF clauses added (approx):", cnf_count)
print("Z variables introduced:", z_count)
print("XOR clauses added:", xor_count)
print("Total vars in vpool:", vpool.top)

# solve
print("Solving... (may take a while)")
res = solver.solve()
print("Solver returned", res)
sat = bool(res[0])
assignment = res[1]

# interpret assignment
mapping = [-1] * 27
signs = [False] * 27
valid = False
if sat and assignment is not None:
    # assignment is sequence-like: index = var-1 -> bool
    def val(v):
        # pycryptosat assignment sequence uses index == var id (assignment[0] is placeholder None)
        idx = v
        if idx < 0 or idx >= len(assignment):
            return False
        return bool(assignment[idx])

    # reconstruct mapping with detailed debug for failures
    print("assignment length:", len(assignment), "vpool.top:", vpool.top)
    for i in range(27):
        trues = [u for u in range(27) if val(x_var[(i, u)])]
        if len(trues) == 1:
            mapping[i] = trues[0]
        elif len(trues) > 1:
            print("Row", i, "has multiple true x candidates", trues)
        else:
            print(
                "Row",
                i,
                "has ZERO true x; var ids =",
                [x_var[(i, u)] for u in range(27)],
            )
            # print corresponding assignment values if available
            vals = []
            for u in range(27):
                v = x_var[(i, u)]
                if v - 1 < len(assignment):
                    vals.append((v, assignment[v - 1]))
                else:
                    vals.append((v, "OOB"))
            print("  var assignment snapshot (var, val):", vals)
    for i in range(27):
        signs[i] = val(s_var[i])
    # validity checks
    valid_bijection = len(set(mapping)) == 27 and all(m != -1 for m in mapping)
    triad_ok = True
    parity_ok = True
    for tri in matched_tris:
        i, j, k = tri
        mapped = tuple(sorted((mapping[i], mapping[j], mapping[k])))
        if mapped not in coset_triads_set:
            triad_ok = False
            break
        dbit = D_BITS.get(tuple(sorted(tri)))
        if dbit is not None:
            if (signs[i] ^ signs[j] ^ signs[k]) != bool(dbit):
                parity_ok = False
                break
    valid = valid_bijection and triad_ok and parity_ok
    print(
        "Validity: bijection?",
        valid_bijection,
        "triads_ok?",
        triad_ok,
        "parity_ok?",
        parity_ok,
    )

# write artifact
out = {
    "W_idx": W_idx,
    "sat": sat,
    "valid": bool(valid),
    "mapping": mapping,
    "signs": signs,
}
(ART / f"pysat_cryptosat_W{W_idx}_mapping_signs.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote artifact:", ART / f"pysat_cryptosat_W{W_idx}_mapping_signs.json")
# write debug assignment summary
rows_debug = []
if assignment is not None:
    for i in range(27):
        trues = [u for u in range(27) if val(x_var[(i, u)])]
        var_ids = [x_var[(i, u)] for u in range(27)]
        var_vals = []
        for v in var_ids:
            if v - 1 < len(assignment):
                var_vals.append(bool(assignment[v - 1]))
            else:
                var_vals.append("OOB")
        rows_debug.append(
            {"row": i, "true_us": trues, "var_ids": var_ids, "var_vals": var_vals}
        )
    dbg = {
        "assignment_len": len(assignment),
        "vpool_top": vpool.top,
        "rows": rows_debug,
    }
    (ART / f"pysat_cryptosat_W{W_idx}_assignment_debug.json").write_text(
        json.dumps(dbg, indent=2), encoding="utf-8"
    )
    print(
        "Wrote debug assignment snapshot:",
        ART / f"pysat_cryptosat_W{W_idx}_assignment_debug.json",
    )
if not sat:
    raise SystemExit(2)
sys.exit(0)
