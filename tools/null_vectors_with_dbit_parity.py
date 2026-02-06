#!/usr/bin/env python3
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"
heis = json.load(
    open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8")
)
triads = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
# build matrix rows (27 x 36)
rows = []
for node in range(27):
    mask = 0
    for i, tri in enumerate(triads):
        if node in tri:
            mask |= 1 << i
    rows.append(mask)
# elimination to find nullspace basis as before
m = 27
n = 36
rows_copy = rows.copy()
pivots = {}
row_idx = 0
for col in range(n):
    pivot_row = None
    for r in range(row_idx, m):
        if (rows_copy[r] >> col) & 1:
            pivot_row = r
            break
    if pivot_row is None:
        continue
    rows_copy[row_idx], rows_copy[pivot_row] = rows_copy[pivot_row], rows_copy[row_idx]
    pivots[col] = row_idx
    for r in range(m):
        if r != row_idx and ((rows_copy[r] >> col) & 1):
            rows_copy[r] ^= rows_copy[row_idx]
    row_idx += 1
free_vars = [i for i in range(n) if i not in pivots]
pivot_rows = {c: rows_copy[r] for c, r in pivots.items()}
# basis
basis = []
for f in free_vars:
    x = 1 << f
    for c, rmask in pivot_rows.items():
        if (rmask >> f) & 1:
            x |= 1 << c
    basis.append(x)
# load D_BITS
sdata = json.load(
    open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8")
)
dmap = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in sdata["solution"]["d_triples"]
}
# BFS search for small weight null vectors up to weight 10
from collections import deque

seen = set()
queue = deque()
for i in range(len(basis)):
    queue.append((basis[i], [i]))
    seen.add(basis[i])
found = []
maxw = 10
while queue:
    vec, idxs = queue.popleft()
    w = vec.bit_count()
    # compute D_BIT parity
    supp = [i for i in range(n) if (vec >> i) & 1]
    d_par = sum(dmap.get(triads[i], 0) for i in supp) % 2
    if w <= maxw and d_par == 1:
        found.append((w, supp, idxs))
    if len(idxs) < len(basis):
        last = idxs[-1]
        for j in range(last + 1, len(basis)):
            newvec = vec ^ basis[j]
            if newvec not in seen:
                seen.add(newvec)
                queue.append((newvec, idxs + [j]))
# report smallest
found_sorted = sorted(found, key=lambda x: x[0])
print(
    "Null vectors with odd D_BIT parity (weight<=", maxw, ") count:", len(found_sorted)
)
for w, supp, idxs in found_sorted[:20]:
    print(" weight", w, "supp triad indices", supp, "triads", [triads[i] for i in supp])
print("\nDone")
