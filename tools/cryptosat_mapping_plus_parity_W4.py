"""Encode full mapping (bijective) CNF + parity XOR constraints for W4 and check satisfiability with pycryptosat.

This script:
 - loads W4 coset triads
 - takes the anchor 19-triad set from artifacts/anchor_specific_cpsat_W4_status_OPTIMAL.json
 - encodes x[i,u] (27x27), bijection constraints (exactly one per row/col via pairwise AMO and ALO),
 - encodes triad matching by creating z variables for each allowed assignment of triad->coset triad (and requiring at least one z per triad),
 - adds XOR parity constraints s_i xor s_j xor s_k = dbit for triads in the matched set when dbit is known,
 - solves with pycryptosat.

This is exploratory; performance is expected to be slow for full instance but should be fine for a single W test.
"""

import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np
from pycryptosat import Solver

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

# pick W index 4 (as example)
W_idx = 4
# reconstruct coset triads for W4
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

# load anchor 19-triad set for W4
anchor_file = ART / f"anchor_specific_cpsat_W{W_idx}_status_OPTIMAL.json"
if not anchor_file.exists():
    print("Anchor mapping missing for W4; aborting")
    raise SystemExit(1)
anchor = json.load(open(anchor_file, "r", encoding="utf-8"))
matched_tris = [tuple(sorted(tri)) for tri in anchor.get("matched_tris", [])]
print("Using anchor matched triads count:", len(matched_tris))

# build candidate assignments for each triad (list of (u1,u2,u3) perms)
matched_candidates = {ti: [] for ti in range(len(E6_TRIADS))}
for ti, tri in enumerate(E6_TRIADS):
    i, j, k = tri
    for ct in coset_triads:
        for perm_ct in permutations(ct):
            u1, u2, u3 = perm_ct
            if tuple(sorted(ct)) in coset_triads_set:
                matched_candidates[ti].append((u1, u2, u3))

# filter to just anchor triads we require
required_tri_idxs = [tri_to_idx[tuple(sorted(t))] for t in matched_tris]


# variable numbering helpers
# x_i_u: var = 1 + i*27 + u
def var_x(i, u):
    return 1 + i * 27 + u


# s_i vars follow after x's: offset
S_OFFSET = 1 + 27 * 27


def var_s(i):
    return S_OFFSET + i


# z variables start after s vars
Z_OFFSET = S_OFFSET + 27

solver = Solver()
next_z = 0
z_vars = {}  # (ti,u1,u2,u3) -> var
cnf_added = 0
xor_added = 0

# bijection constraints: ALO for rows
for i in range(27):
    clause = [var_x(i, u) for u in range(27)]
    solver.add_clause(clause)
    cnf_added += 1
# AMO for rows: pairwise negatives
for i in range(27):
    for u1, u2 in combinations(range(27), 2):
        solver.add_clause([-var_x(i, u1), -var_x(i, u2)])
        cnf_added += 1
# ALO for columns
for u in range(27):
    clause = [var_x(i, u) for i in range(27)]
    solver.add_clause(clause)
    cnf_added += 1
# AMO for columns
for u in range(27):
    for i1, i2 in combinations(range(27), 2):
        solver.add_clause([-var_x(i1, u), -var_x(i2, u)])
        cnf_added += 1

# For each required triad, create z variables for its allowed assignments and require at least one
for ti in required_tri_idxs:
    tri = E6_TRIADS[ti]
    zlist = []
    for u1, u2, u3 in matched_candidates[ti]:
        # create z var
        next_z += 1
        zv = Z_OFFSET + next_z
        z_vars[(ti, u1, u2, u3)] = zv
        # z => x(i,u1) etc
        i, j, k = tri
        solver.add_clause([-zv, var_x(i, u1)])
        solver.add_clause([-zv, var_x(j, u2)])
        solver.add_clause([-zv, var_x(k, u3)])
        cnf_added += 3
        # if all three x true => z true: (-x_i_u1 or -x_j_u2 or -x_k_u3 or z)
        solver.add_clause([-var_x(i, u1), -var_x(j, u2), -var_x(k, u3), zv])
        cnf_added += 1
        zlist.append(zv)
    if not zlist:
        print("No match candidates for required tri", tri, "on W4; aborting")
        raise SystemExit(1)
    solver.add_clause(zlist)  # at least one mapping of this triad exists
    cnf_added += 1

# add XOR parity constraints for triads with D_BITS value
for ti in required_tri_idxs:
    tri = E6_TRIADS[ti]
    dbit = D_BITS.get(tuple(sorted(tri)))
    if dbit is None:
        continue
    # s_i xor s_j xor s_k == dbit
    a, b, c = var_s(tri[0]), var_s(tri[1]), var_s(tri[2])
    rhs = bool(dbit)
    solver.add_xor_clause([a, b, c], rhs)
    xor_added += 1

print("CNF clauses added (approx):", cnf_added)
print("XOR clauses added:", xor_added)
print("Total z variables introduced:", next_z)

# solve
res = solver.solve()
print("Solver returned sat?", res[0])
if res[0]:
    # pycryptosat returns (sat_bool, assignment_sequence_or_None)
    assignment = res[1]

    # assignment may be a sequence (index = var-1)
    def val_of(v):
        if assignment is None:
            return False
        # sequence-like
        idx = v - 1
        if idx < 0 or idx >= len(assignment):
            return False
        return bool(assignment[idx])

    # reconstruct mapping and signs
    mapping = [-1] * 27
    for i in range(27):
        for u in range(27):
            if val_of(var_x(i, u)):
                mapping[i] = u
                break
    signs = [val_of(var_s(i)) for i in range(27)]
    # debug: report assignment length and per-row counts
    if assignment is None:
        print("assignment is None")
    else:
        print(
            "assignment length:",
            len(assignment),
            "max var index expected:",
            Z_OFFSET + next_z,
        )
        for i in range(27):
            true_us = [u for u in range(27) if val_of(var_x(i, u))]
            if len(true_us) == 0:
                print("Row", i, "has 0 true x vars")
            elif len(true_us) > 1:
                print("Row", i, "has multiple true assignments:", true_us)
    # validate mapping is bijective
    valid_bijection = len(set(mapping)) == 27 and all(m != -1 for m in mapping)
    # validate triad matches and parity
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
        "Found mapping valid?",
        valid,
        "bijection?",
        valid_bijection,
        "triad_ok?",
        triad_ok,
        "parity_ok?",
        parity_ok,
    )
    print("Mapping (first 10):", mapping[:10])
    print("Signs (first 10):", signs[:10])
    # save artifact
    out = {"W_idx": W_idx, "valid": bool(valid), "mapping": mapping, "signs": signs}
    (ART / f"cryptosat_W{W_idx}_mapping_signs.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
else:
    print("UNSAT: no mapping+sign solution found for W4 with these required triads")
