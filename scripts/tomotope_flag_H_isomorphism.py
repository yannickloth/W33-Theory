#!/usr/bin/env python3
"""Generate the 192-element tomotope flag group and establish an
explicit isomorphism with the axis-line stabilizer subgroup H from W33.

The script runs purely in standard Python (no Sage dependency).  It
creates two permutation groups acting on 192 points: the regular
representation of H, and an orientation-double-cover of the 96‑element
tomotope automorphism group.  A backtracking search using order and
centralizer invariants then finds a bijection between the two groups.

Outputs written under the workspace root:
  * H_group.json              – generators for H regular rep
  * tomotope_192_group.json   – generators for tomotope flags group
  * isomorphism.json          – the index‑to‑index mapping (if found)

This script is intended to verify that H ≅ W(D4) ≅ (orient. cover of
Γ(tomotope)).
"""

import json
import itertools
import sys

# ------------------------------------------------------------------
# helper utilities for permutations represented as tuples
# ------------------------------------------------------------------

def compose(p, q):
    """Return permutation p∘q (apply q then p)."""
    return tuple(p[q[i]] for i in range(len(p)))

# compute the order of a permutation (cycle structure). brute-force
# since lengths ≤192.
def perm_order(p):
    idp = tuple(range(len(p)))
    cur = p
    k = 1
    while cur != idp:
        cur = compose(p, cur)
        k += 1
        if k > 1000:
            raise RuntimeError("order computation failed")
    return k

# compute centralizer size relative to a multiplication table
def centralizer_size(idx, mul_table):
    n = len(mul_table)
    cnt = 0
    for j in range(n):
        if mul_table[idx][j] == mul_table[j][idx]:
            cnt += 1
    return cnt

# ------------------------------------------------------------------
# Load H subgroup data from axis_line_stabilizer_192.json
# ------------------------------------------------------------------
print("loading H elements from axis_line_stabilizer_192.json")
hfile = "axis_line_stabilizer_192.json"
h_data = json.load(open(hfile))
H_elems = h_data["elements"]

# multiplication rule for octonion axis stabilizer elements
# see compute_w33_axis192_torsor.py for reference

def multiply_h(h1, h2):
    perm1, sign1 = h1["perm"], h1["signs"]
    perm2, sign2 = h2["perm"], h2["signs"]
    newperm = [None] * 7
    newsign = [None] * 7
    for i in range(7):
        j = perm2[i] - 1
        newperm[i] = perm1[j]
        newsign[i] = sign1[j] * sign2[i]
    return {"perm": newperm, "signs": newsign}

H_index = { (tuple(h["perm"]), tuple(h["signs"])): idx
            for idx, h in enumerate(H_elems) }
assert len(H_index) == len(H_elems) == 192

# build regular permutation representation of H on 192 points
H_perms = []
for h in H_elems:
    image = []
    for g in H_elems:
        prod = multiply_h(h, g)
        image.append(H_index[(tuple(prod["perm"]), tuple(prod["signs"]))])
    H_perms.append(tuple(image))

assert len(H_perms) == 192

# ------------------------------------------------------------------
# Build tomotope automorphism group on 12 points and lift to 192
# ------------------------------------------------------------------
print("constructing tomotope flag group")
tomo_file = "data/maniplex_tables/tomotope_permutation_summary.json"
tomo = json.load(open(tomo_file))
parsed = tomo["parsed_generators"]

# generators as 0-indexed permutations on 12 symbols
gens12 = []
for name in ["p0", "p1", "p2", "p3"]:
    mapping = {int(k) - 1: int(v) - 1 for k, v in parsed[name].items()}
    perm = tuple(mapping.get(i, i) for i in range(12))
    gens12.append(perm)

# generate the group closure of the 96-element tomotope automorphism group
G12_elems = [tuple(range(12))]
seen = {G12_elems[0]}
idx = 0
while idx < len(G12_elems):
    g = G12_elems[idx]
    for a in gens12:
        comp = compose(a, g)
        if comp not in seen:
            seen.add(comp)
            G12_elems.append(comp)
    idx += 1

assert len(G12_elems) == 96, "unexpected tomotope group size"

# lift to orientation double cover on 192 points
# index scheme: element index*2 + orientation bit

def lift_perm12(perm12):
    perm192 = [None] * 192
    for idx, g in enumerate(G12_elems):
        # compute product g * perm12 (apply perm12 after g)
        newg = compose(perm12, g)
        newidx = G12_elems.index(newg)
        perm192[2 * idx + 0] = 2 * newidx + 0
        perm192[2 * idx + 1] = 2 * newidx + 1
    return tuple(perm192)

perms192 = [lift_perm12(p) for p in gens12]
# orientation flip generator
flip192 = tuple(2 * (i // 2) + (1 - (i % 2)) for i in range(192))
perms192.append(flip192)

# close the 192-element group
G192_elems = [tuple(range(192))]
seen = {G192_elems[0]}
idx = 0
while idx < len(G192_elems):
    g = G192_elems[idx]
    for a in perms192:
        comp = compose(a, g)
        if comp not in seen:
            seen.add(comp)
            G192_elems.append(comp)
    idx += 1

assert len(G192_elems) == 192, "unexpected lifted group size"

# ------------------------------------------------------------------
# compute multiplication tables and invariants for both groups
# ------------------------------------------------------------------
n = 192
G192_mul = [[None] * n for _ in range(n)]
for i, p in enumerate(G192_elems):
    for j, q in enumerate(G192_elems):
        G192_mul[i][j] = G192_elems.index(compose(p, q))

H_mul = [[None] * n for _ in range(n)]
for i, p in enumerate(H_perms):
    for j, q in enumerate(H_perms):
        H_mul[i][j] = H_perms.index(compose(p, q))

orders_G192 = [perm_order(p) for p in G192_elems]
orders_H = [perm_order(p) for p in H_perms]

# diagnostic: print order distributions
from collections import Counter
print("order distribution in G192:", Counter(orders_G192))
print("order distribution in H_perms:", Counter(orders_H))

cen_G192 = [centralizer_size(i, G192_mul) for i in range(n)]
cen_H = [centralizer_size(i, H_mul) for i in range(n)]

# save generators and invariants
json.dump({"gens": perms192, "orders": orders_G192, "centralizers": cen_G192},
          open("tomotope_192_group.json", "w"), indent=2)
json.dump({"gens": H_perms, "orders": orders_H, "centralizers": cen_H},
          open("H_group.json", "w"), indent=2)

# ------------------------------------------------------------------
# backtracking search for isomorphism using invariants
# ------------------------------------------------------------------
mapping = [-1] * n
used = [False] * n
# identity maps to identity
mapping[0] = 0
used[0] = True

# prepare candidate lists by order only (centralizer invariants removed)
candidates_by_order = {}
for i in range(n):
    key = orders_G192[i]
    candidates_by_order.setdefault(key, []).append(i)
# check distribution
for i in range(n):
    key = orders_H[i]
    if key not in candidates_by_order:
        print("Order mismatch", key)
        sys.exit(1)

# create mirror structure for H
cands_H = {}
for i in range(n):
    key = orders_H[i]
    cands_H.setdefault(key, []).append(i)

# backtracking function

def backtrack(pos):
    if pos == n:
        return True
    if mapping[pos] != -1:
        return backtrack(pos + 1)
    key = orders_G192[pos]
    for h_idx in cands_H.get(key, []):
        if used[h_idx]:
            continue
        # tentatively assign
        mapping[pos] = h_idx
        used[h_idx] = True
        ok = True
        # check consistency with already mapped elements
        for i in range(pos):
            if mapping[i] >= 0:
                gprod = G192_mul[i][pos]
                hprod = H_mul[mapping[i]][mapping[pos]]
                if mapping[gprod] != -1 and mapping[gprod] != hprod:
                    ok = False
                    break
                gprod2 = G192_mul[pos][i]
                hprod2 = H_mul[mapping[pos]][mapping[i]]
                if mapping[gprod2] != -1 and mapping[gprod2] != hprod2:
                    ok = False
                    break
        if ok and backtrack(pos + 1):
            return True
        # undo
        used[h_idx] = False
        mapping[pos] = -1
    return False

print("searching for isomorphism...")
found = backtrack(1)
print("isomorphism found?", found)

out = {"isomorphic": found}
if found:
    out["mapping"] = mapping
json.dump(out, open("isomorphism.json", "w"), indent=2)

if found:
    print("mapping written to isomorphism.json")
else:
    print("failed to find isomorphism")
