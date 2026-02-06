#!/usr/bin/env python3
"""Find nullspace (dependencies) among the 36 affine triads and search for small-weight null vectors."""
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"
heis = json.load(
    open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8")
)
# list of 36 triads
triads = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
assert len(triads) == 36
# build matrix A (27 equations x 36 variables)
rows = []
for node in range(27):
    mask = 0
    for i, tri in enumerate(triads):
        if node in tri:
            mask |= 1 << i
    rows.append(mask)
# Gaussian elimination mod 2 to find pivots
m = 27
n = 36
rows_copy = rows.copy()
pivots = {}  # pivot_col -> row_index
row_idx = 0
for col in range(n):
    # find row >= row_idx with bit at col
    pivot_row = None
    for r in range(row_idx, m):
        if (rows_copy[r] >> col) & 1:
            pivot_row = r
            break
    if pivot_row is None:
        continue
    # swap
    rows_copy[row_idx], rows_copy[pivot_row] = rows_copy[pivot_row], rows_copy[row_idx]
    pivots[col] = row_idx
    # eliminate others
    for r in range(m):
        if r != row_idx and ((rows_copy[r] >> col) & 1):
            rows_copy[r] ^= rows_copy[row_idx]
    row_idx += 1
    if row_idx >= m:
        break
rank = len(pivots)
free_vars = [i for i in range(n) if i not in pivots]
print("Rank:", rank, "Free vars:", len(free_vars))
# build back-substitution to express pivot vars in terms of free vars
# For each pivot column c at row r, the row mask rows_copy[r] has 1s at pivot and possibly at free vars.
pivot_rows = {c: rows_copy[r] for c, r in pivots.items()}
# For each free var f, create basis vector x where x_f = 1 and other free vars 0
basis = []
for f in free_vars:
    x = 0
    x |= 1 << f
    # compute pivot vars: for each pivot c, if pivot_rows[c] has bit at f, then set x_c = 1
    for c, rmask in pivot_rows.items():
        if (rmask >> f) & 1:
            x |= 1 << c
    basis.append(x)
print("Nullspace dimension (expected):", len(free_vars))
# search for small weight combinations
from collections import deque

seen = set()
# BFS over combinations of basis vectors to find small weight null vectors
max_weight = 10
found = []
# start with single basis vectors
queue = deque([(basis[i], [i]) for i in range(len(basis))])
while queue:
    vec, idxs = queue.popleft()
    w = vec.bit_count()
    if w <= max_weight and vec != 0:
        # record
        found.append((w, idxs.copy(), vec))
        # don't expand further if weight already small? we should expand to find other combinations
    if len(idxs) < len(basis):
        last = idxs[-1] if idxs else -1
        for j in range(last + 1, len(basis)):
            newvec = vec ^ basis[j]
            newidxs = idxs + [j]
            if newvec not in seen and len(newidxs) <= len(basis):
                seen.add(newvec)
                queue.append((newvec, newidxs))
# sort found by weight and report smallest few
found_sorted = sorted(found, key=lambda x: (x[0], len(x[1])))
print("Found null vectors (weight <=", max_weight, ") count:", len(found_sorted))
for w, idxs, vec in found_sorted[:20]:
    # print which triads indices are in support
    supp = [i for i in range(n) if (vec >> i) & 1]
    print(" weight", w, "basis_idxs", idxs, "support triads", supp)
# check if known certificate supports present
# load sign_unsat_cores and check if their certificate rows correspond to any support
try:
    cores = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
    cert_supports = []
    for entry in cores:
        cert = entry["certificate_rows"]
        supp = [
            i for i, t in enumerate(triads) if t in [tuple(sorted(c)) for c in cert]
        ]
        print("Core", entry["file"], "certificate supp indices", supp)
        cert_supports.append(supp)
    # check if any null vector equals these supports
    for supp in cert_supports:
        v = 0
        for i in supp:
            v |= 1 << i
        print(
            "Matches nullspace found?",
            "Yes" if v in [vec for _, _, vec in found_sorted] else "No",
        )
except Exception as e:
    print("No sign_unsat_cores to check or error", e)
print("\nDone")
