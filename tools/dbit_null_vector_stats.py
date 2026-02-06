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
# load D_BIT
sdata = json.load(
    open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8")
)
dmap = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in sdata["solution"]["d_triples"]
}
dbit_triads = [t for t, v in dmap.items() if v == 1]
# reuse elimination from previous script to compute basis
rows = []
for node in range(27):
    mask = 0
    for i, tri in enumerate(triads):
        if node in tri:
            mask |= 1 << i
    rows.append(mask)
# elimination
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
basis = []
for f in free_vars:
    x = 1 << f
    for c, rmask in pivot_rows.items():
        if (rmask >> f) & 1:
            x |= 1 << c
    basis.append(x)
# BFS search null vectors weight<=10 and odd D_BIT parity
from collections import Counter, deque

queue = deque([(basis[i], [i]) for i in range(len(basis))])
seen = set(basis)
maxw = 10
odd_nulls = []
while queue:
    vec, idxs = queue.popleft()
    w = vec.bit_count()
    supp = [i for i in range(n) if (vec >> i) & 1]
    d_par = sum(dmap.get(triads[i], 0) for i in supp) % 2
    if w <= maxw and d_par == 1:
        odd_nulls.append((w, supp, idxs))
    if len(idxs) < len(basis):
        last = idxs[-1]
        for j in range(last + 1, len(basis)):
            newvec = vec ^ basis[j]
            if newvec not in seen:
                seen.add(newvec)
                queue.append((newvec, idxs + [j]))
# analyze frequency of DBIT triads within these odd null vectors
ctr = Counter()
for w, supp, idxs in odd_nulls:
    for i in supp:
        if triads[i] in dbit_triads:
            ctr[triads[i]] += 1
print("Total odd null vectors found (w<=10):", len(odd_nulls))
for tri, cnt in ctr.most_common():
    print("Triad", tri, "count", cnt)
print("\nTop 10 triads (by count):")
for tri, cnt in ctr.most_common(10):
    print(tri, cnt)
print("\nDone")
