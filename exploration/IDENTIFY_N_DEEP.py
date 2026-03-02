#!/usr/bin/env python3
"""
IDENTIFY_N_DEEP.py — Deep algebraic fingerprint of N
=====================================================

Computes every invariant needed to uniquely identify N among the 1543 groups
of order 192.  Explores the derived series, Frattini subgroup, Sylow
structure, conjugacy class sizes, and action on 27 QIDs.

Key known facts (from Pillars 94–100):
  |N| = 192 = 2^6 · 3
  Z(N) = 1   (trivial centre)
  14 conjugacy classes
  [N,N] has order 48:  element orders {1:1, 2:15, 3:32}
  N / [N,N]  ≅  Z_2^2
  Sylow-2 of N has order 64 (not normal, 3 conjugates)
  Element-order distribution: {1:1, 2:43, 3:32, 4:84, 6:32}
"""

import json, sys, os
from collections import Counter
from itertools import combinations

# ── helpers ──────────────────────────────────────────────────────────

def compose(a, b):
    """Compose permutations a∘b: (a∘b)(i) = a(b(i))."""
    return [a[b[i]] for i in range(len(a))]

def inv(p):
    """Inverse permutation."""
    q = [0]*len(p)
    for i, v in enumerate(p):
        q[v] = i
    return q

def perm_order(p):
    n = len(p)
    x = list(range(n))
    q = list(p)
    for k in range(1, n+1):
        if q == x:
            return k
        q = compose(p, q)
    return n

def identity(n):
    return list(range(n))

# ── load N ────────────────────────────────────────────────────────────

with open("N_subgroup.json") as f:
    N_raw = json.load(f)
N_elts = [tuple(g) for g in N_raw]
n = len(N_elts[0])          # degree of perm rep
N_set = set(N_elts)
e = tuple(range(n))
assert e in N_set, "identity must be in N"
print(f"|N| = {len(N_elts)},  degree = {n}")

# ── element orders ────────────────────────────────────────────────────

order_dist = Counter()
for g in N_elts:
    order_dist[perm_order(g)] += 1
print(f"Element-order distribution: {dict(sorted(order_dist.items()))}")

# ── centre Z(N) ───────────────────────────────────────────────────────

print("\nComputing centre Z(N) ...")
centre = []
for g in N_elts:
    if all(compose(list(g), list(h)) == compose(list(h), list(g)) for h in N_elts):
        centre.append(g)
print(f"|Z(N)| = {len(centre)}")

# ── derived subgroup [N,N] ────────────────────────────────────────────

print("\nComputing [N,N] via commutators ...")
comm_set = set()
for g in N_elts:
    for h in N_elts:
        # [g,h] = g h g^{-1} h^{-1}
        c = compose(compose(list(g), list(h)),
                    compose(inv(list(g)), inv(list(h))))
        comm_set.add(tuple(c))

# close under multiplication
deriv = set(comm_set)
changed = True
while changed:
    changed = False
    new = set()
    for a in list(deriv):
        for b in comm_set:       # only multiply by generators (commutators)
            p = tuple(compose(list(a), list(b)))
            if p not in deriv:
                new.add(p)
    if new:
        deriv |= new
        changed = True
        if len(deriv) > 200:
            break

print(f"|[N,N]| = {len(deriv)}")

# element orders inside [N,N]
deriv_orders = Counter()
for g in deriv:
    deriv_orders[perm_order(g)] += 1
print(f"[N,N] element orders: {dict(sorted(deriv_orders.items()))}")

# ── Sylow-2 of [N,N] ─────────────────────────────────────────────────

print("\nAnalysing Sylow-2 of [N,N] ...")
deriv_2 = [g for g in deriv if perm_order(g) in (1, 2)]
print(f"  Elements of 2-power order in [N,N]: {len(deriv_2)}")
# Check if they form a subgroup
deriv_2_set = set(deriv_2)
is_subgroup = True
for a in deriv_2:
    for b in deriv_2:
        if tuple(compose(list(a), list(b))) not in deriv_2_set:
            is_subgroup = False
            break
    if not is_subgroup:
        break
print(f"  Forms a subgroup? {is_subgroup}")
if is_subgroup:
    print(f"  Sylow-2 of [N,N] is elementary abelian C_2^4" if len(deriv_2) == 16 else
          f"  Sylow-2 order = {len(deriv_2)}")
    # check elementary abelian
    all_involutions = all(perm_order(g) <= 2 for g in deriv_2)
    commutative = all(compose(list(a), list(b)) == compose(list(b), list(a))
                      for a in deriv_2 for b in deriv_2)
    print(f"  All involutions? {all_involutions}")
    print(f"  All commute? {commutative}")

# ── second derived [N,N]' = [[N,N],[N,N]] ─────────────────────────────

print("\nComputing [[N,N],[N,N]] ...")
deriv_list = list(deriv)
comm2_set = set()
for g in deriv_list:
    for h in deriv_list:
        c = compose(compose(list(g), list(h)),
                    compose(inv(list(g)), inv(list(h))))
        comm2_set.add(tuple(c))
# close
deriv2 = set(comm2_set)
changed = True
while changed:
    changed = False
    new = set()
    for a in list(deriv2):
        for b in comm2_set:
            p = tuple(compose(list(a), list(b)))
            if p not in deriv2:
                new.add(p)
    if new:
        deriv2 |= new
        changed = True
        if len(deriv2) > 200:
            break
print(f"|[N,N]'| = |[[N,N],[N,N]]| = {len(deriv2)}")

# ── third derived [N,N]'' ─────────────────────────────────────────────

if len(deriv2) > 1:
    print("\nComputing [N,N]'' ...")
    d2_list = list(deriv2)
    comm3_set = set()
    for g in d2_list:
        for h in d2_list:
            c = compose(compose(list(g), list(h)),
                        compose(inv(list(g)), inv(list(h))))
            comm3_set.add(tuple(c))
    deriv3 = set(comm3_set)
    changed = True
    while changed:
        changed = False
        new = set()
        for a in list(deriv3):
            for b in comm3_set:
                p = tuple(compose(list(a), list(b)))
                if p not in deriv3:
                    new.add(p)
        if new:
            deriv3 |= new
            changed = True
            if len(deriv3) > 200:
                break
    print(f"|[N,N]''| = {len(deriv3)}")
else:
    print("[N,N]' is trivial → [N,N] is abelian (IMPOSSIBLE for order 48 with these elements)")

# ── Frattini subgroup Φ(N) ────────────────────────────────────────────

print("\nComputing Frattini subgroup Φ(N) = intersection of maximal subgroups")
print("  (approximation: Φ(N) = N^p · [N,N] for p-groups, but N is not a p-group)")
print("  Using Φ(N) ⊇ [N,N] · N^2  (Burnside basis theorem for the quotient)")

# Compute N^2 = {g^2 : g ∈ N}
N_sq = set()
for g in N_elts:
    N_sq.add(tuple(compose(list(g), list(g))))
print(f"  |N^2| (set of squares) = {len(N_sq)}")

# Generate <N^2, [N,N]>
phi_gens = N_sq | deriv
phi = set(phi_gens)
changed = True
iters = 0
while changed:
    changed = False
    new = set()
    for a in list(phi):
        for b in phi_gens:
            p = tuple(compose(list(a), list(b)))
            if p not in phi:
                new.add(p)
    if new:
        phi |= new
        changed = True
    iters += 1
    if len(phi) >= 192 or iters > 30:
        break
print(f"  |<N^2, [N,N]>| = {len(phi)}")

# ── action on 27 QIDs ─────────────────────────────────────────────────

print("\n=== ACTION ON 27 QIDs ===")
# Load flag map to determine QID assignment
try:
    with open("N_flag_map.json") as f:
        flag_map = json.load(f)
    print(f"  Loaded N_flag_map.json with {len(flag_map)} entries")
except Exception as ex:
    print(f"  Could not load flag map: {ex}")
    flag_map = None

# Each flag has a QID. We need the map: flag_index → QID
# From Pillar 98: 54 QID-preserving flags, 27 QIDs, block structure
import csv
try:
    qid_of_flag = {}
    with open("K54_54sheet_coords_refined.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx = int(row.get("flag_idx", row.get("flag", -1)))
            qid = int(row.get("qid", -1))
            if idx >= 0 and qid >= 0:
                qid_of_flag[idx] = qid
    print(f"  QID map: {len(qid_of_flag)} flags → QIDs")
except Exception as ex:
    print(f"  Could not load K54: {ex}")
    qid_of_flag = {}

# ── Conjugacy classes (verify count = 14) ─────────────────────────────

print("\n=== CONJUGACY CLASSES ===")
seen = set()
classes = []
for g in N_elts:
    if g in seen:
        continue
    cls = set()
    for h in N_elts:
        c = tuple(compose(compose(list(h), list(g)), inv(list(h))))
        cls.add(c)
    classes.append(cls)
    seen |= cls

class_sizes = sorted(len(c) for c in classes)
print(f"  Number of conjugacy classes: {len(classes)}")
print(f"  Class sizes: {class_sizes}")

# ── class equation ────────────────────────────────────────────────────

print(f"\n  Class equation: {' + '.join(str(s) for s in class_sizes)} = {sum(class_sizes)}")

# ── summary JSON ──────────────────────────────────────────────────────

summary = {
    "order": len(N_elts),
    "degree": n,
    "centre_order": len(centre),
    "element_orders": dict(sorted(order_dist.items())),
    "derived_order": len(deriv),
    "derived_element_orders": dict(sorted(deriv_orders.items())),
    "second_derived_order": len(deriv2),
    "num_conjugacy_classes": len(classes),
    "class_sizes": class_sizes,
    "sylow2_of_derived_is_elementary_abelian": is_subgroup and all_involutions and commutative,
}

print("\n=== STRUCTURAL SUMMARY ===")
for k, v in summary.items():
    print(f"  {k}: {v}")

# ── identification hypothesis ─────────────────────────────────────────

print("\n=== IDENTIFICATION ===")
print("Known:")
print("  [N,N] has order 48 with Sylow-2 = C_2^4 (elementary abelian)")
print("  [N,N] has 32 elements of order 3 and 15 involutions")
print("  → [N,N] ≅ C_2^4 ⋊ C_3 with fixed-point-free action")
print("  → [N,N] ≅ (F_4)^2 ⋊ F_4* (affine scalar group)")
print()
if len(deriv2) == 16:
    print("  [N,N]' = C_2^4 means [N,N] is NOT solvable to depth 1")
    print("  This means [N,N] = C_2^4 ⋊ C_3 where C_3 acts nontrivially on C_2^4")
    print("  and [[N,N],[N,N]] = [C_2^4, C_3] = entire C_2^4 (since action is fixed-point-free)")
elif len(deriv2) == 1:
    print("  [N,N]' = 1 means [N,N] is ABELIAN — impossible with this element distribution!")
else:
    print(f"  [N,N]' has order {len(deriv2)}")

# check coset structure of N/[N,N]
print("\n=== COSET STRUCTURE N / [N,N] ===")
deriv_list_sorted = sorted(deriv, key=lambda g: g)
cosets = {}
coset_reps = []
for g in N_elts:
    # coset = g · [N,N]
    coset_key = frozenset(tuple(compose(list(g), list(d))) for d in deriv)
    if coset_key not in cosets:
        cosets[coset_key] = g
        coset_reps.append(g)

print(f"  Number of cosets: {len(coset_reps)}")
for i, rep in enumerate(coset_reps):
    coset_elements = [tuple(compose(list(rep), list(d))) for d in deriv]
    orders_in_coset = Counter(perm_order(g) for g in coset_elements)
    ord_rep = perm_order(rep)
    print(f"  Coset {i} (rep order {ord_rep}): {dict(sorted(orders_in_coset.items()))}")

# ── check if N splits as [N,N] ⋊ C_2^2 ─────────────────────────────

print("\n=== SPLITTING CHECK ===")
print("Looking for a complement to [N,N] in N (subgroup of order 4 ≅ C_2^2) ...")
# Find all elements of order 2 outside [N,N]
involutions_outside = [g for g in N_elts if perm_order(g) == 2 and g not in deriv]
print(f"  Involutions outside [N,N]: {len(involutions_outside)}")

# Check pairs of commuting involutions that generate a V_4 complement
found_complement = False
complement = None
for i, a in enumerate(involutions_outside[:50]):  # limit search
    for b in involutions_outside[i+1:]:
        ab = tuple(compose(list(a), list(b)))
        if perm_order(ab) == 2 and ab not in deriv:
            # {e, a, b, ab} is a C_2^2 subgroup
            V4 = {e, a, b, ab}
            if V4.issubset(N_set) and V4.isdisjoint(deriv - {e}):
                print(f"  Found complement C_2^2 at involutions {i}, disjoint from [N,N]!")
                found_complement = True
                complement = V4
                break
    if found_complement:
        break

if found_complement:
    print("  → N = [N,N] ⋊ C_2^2  (SPLIT extension!)")
    print("  → N = (C_2^4 ⋊ C_3) ⋊ C_2^2")
    
    # Determine how C_2^2 acts on [N,N]
    print("\n  Determining the action of C_2^2 on [N,N] ...")
    comp_list = [g for g in complement if g != e]
    for ci, c in enumerate(comp_list):
        # conjugation by c
        image_orders = Counter()
        fixes_deriv_2 = 0
        for d in deriv:
            cd = tuple(compose(compose(list(c), list(d)), inv(list(c))))
            image_orders[perm_order(cd)] += 1
            if d in deriv_2_set and cd == d:
                fixes_deriv_2 += 1
        print(f"  Generator c_{ci} (order {perm_order(c)}): "
              f"fixed points in Syl2([N,N]) = {fixes_deriv_2}/16, "
              f"image orders = {dict(sorted(image_orders.items()))}")
else:
    print("  No complement found in first 50 involutions — extension may be non-split")

with open("N_deep_identification.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)
print("\nSaved N_deep_identification.json")
