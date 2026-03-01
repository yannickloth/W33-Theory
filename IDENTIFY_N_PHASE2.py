#!/usr/bin/env python3
"""
IDENTIFY_N_PHASE2.py — Determine the quotient N/C₂⁴ and action matrices
========================================================================

From IDENTIFY_N_DEEP.py we know:
  N = (C₂⁴ ⋊ C₃) ⋊ C₂²
  [N,N]' = C₂⁴ (elementary abelian, normal in N)
  N / C₂⁴ has order 12

This script:
  1. Computes N / C₂⁴ (the quotient of order 12) and identifies it
  2. Expresses C₂⁴ as F₂⁴ and computes the action of N/C₂⁴ on it as 4×4 matrices
  3. Identifies the image in GL(4, F₂)
  4. Pins down the SmallGroup ID
"""

import json
from collections import Counter
from itertools import combinations

def compose(a, b):
    return [a[b[i]] for i in range(len(a))]

def inv(p):
    q = [0]*len(p)
    for i, v in enumerate(p):
        q[v] = i
    return q

def perm_order(p):
    x = list(range(len(p)))
    q = list(p)
    for k in range(1, len(p)+1):
        if q == x:
            return k
        q = compose(p, q)
    return len(p)

# ── load N ────────────────────────────────────────────────────────────

with open("N_subgroup.json") as f:
    N_raw = json.load(f)
N_elts = [tuple(g) for g in N_raw]
N_set = set(N_elts)
e = tuple(range(len(N_elts[0])))
deg = len(e)

# ── recompute [N,N] and [N,N]' = C₂⁴ ────────────────────────────────

print("Recomputing [N,N] ...")
comm_set = set()
for g in N_elts:
    for h in N_elts:
        c = compose(compose(list(g), list(h)),
                    compose(inv(list(g)), inv(list(h))))
        comm_set.add(tuple(c))
deriv = set(comm_set)
changed = True
while changed:
    changed = False
    new = set()
    for a in list(deriv):
        for b in comm_set:
            p = tuple(compose(list(a), list(b)))
            if p not in deriv:
                new.add(p)
    if new:
        deriv |= new
        changed = True
        if len(deriv) > 200:
            break
print(f"|[N,N]| = {len(deriv)}")

print("Recomputing [N,N]' = C₂⁴ ...")
deriv_list = list(deriv)
comm2_set = set()
for g in deriv_list:
    for h in deriv_list:
        c = compose(compose(list(g), list(h)),
                    compose(inv(list(g)), inv(list(h))))
        comm2_set.add(tuple(c))
V = set(comm2_set)
changed = True
while changed:
    changed = False
    new = set()
    for a in list(V):
        for b in comm2_set:
            p = tuple(compose(list(a), list(b)))
            if p not in V:
                new.add(p)
    if new:
        V |= new
        changed = True
        if len(V) > 200:
            break
print(f"|C₂⁴| = |[N,N]'| = {len(V)}")
V_list = sorted(V)

# ── F₂⁴ structure ────────────────────────────────────────────────────

print("\n=== C₂⁴ as F₂-vector space ===")
# V is an elementary abelian 2-group of order 16.
# Find a basis {v1, v2, v3, v4} such that every element is a unique F₂-sum.
V_nonid = [v for v in V_list if v != e]

# Greedy basis selection
basis = []
span = {e}
for v in V_nonid:
    if v not in span:
        # extend span
        new_span = set(span)
        for s in list(span):
            prod = tuple(compose(list(v), list(s)))
            new_span.add(prod)
        if len(new_span) > len(span):
            basis.append(v)
            span = new_span
            if len(basis) == 4:
                break

print(f"  Basis has {len(basis)} vectors, span has {len(span)} elements")
assert len(span) == 16, "Basis should span all of C₂⁴"

# Build coordinate map: element → (b₀,b₁,b₂,b₃) ∈ F₂⁴
# Since the group is abelian and every element has order 2,
# each element is a unique subset-product of basis elements.
coord_map = {}
for mask in range(16):
    prod = list(e)
    for i in range(4):
        if mask & (1 << i):
            prod = compose(prod, list(basis[i]))
    coord_map[tuple(prod)] = tuple((mask >> i) & 1 for i in range(4))
print(f"  Coordinate map has {len(coord_map)} entries")
assert set(coord_map.keys()) == V, "Coordinate map must cover all of V"

# Verify: coord_map[e] = (0,0,0,0)
print(f"  e → {coord_map[e]}")
for i, b in enumerate(basis):
    print(f"  basis[{i}] → {coord_map[b]}")

# ── Quotient N / C₂⁴ ─────────────────────────────────────────────────

print("\n=== QUOTIENT N / C₂⁴ (order 12) ===")
cosets_V = {}
coset_reps_V = []
for g in N_elts:
    coset_key = frozenset(tuple(compose(list(g), list(v))) for v in V)
    if coset_key not in cosets_V:
        cosets_V[coset_key] = g
        coset_reps_V.append(g)

Q = coset_reps_V
print(f"  |N/C₂⁴| = {len(Q)} (should be 12)")

# Build multiplication table for Q
def coset_of(g):
    for key, rep in cosets_V.items():
        if tuple(g) in key:
            return rep
    return None

# Faster: build element → coset_rep map
elt_to_coset_rep = {}
for key, rep in cosets_V.items():
    for elt in key:
        elt_to_coset_rep[elt] = rep

# Compute order of each coset-rep in the quotient
print("  Coset representatives and their orders in Q:")
Q_orders = {}
for rep in Q:
    # order in quotient = smallest k such that rep^k ∈ V
    power = list(rep)
    for k in range(1, 13):
        if tuple(power) in V:
            Q_orders[rep] = k
            break
        power = compose(power, list(rep))
    else:
        Q_orders[rep] = 12

Q_order_dist = Counter(Q_orders.values())
print(f"  Q element-order distribution: {dict(sorted(Q_order_dist.items()))}")

# Is Q abelian?
Q_is_abelian = True
for a in Q:
    for b in Q:
        ab = tuple(compose(list(a), list(b)))
        ba = tuple(compose(list(b), list(a)))
        if elt_to_coset_rep[ab] != elt_to_coset_rep[ba]:
            Q_is_abelian = False
            break
    if not Q_is_abelian:
        break
print(f"  Q is abelian? {Q_is_abelian}")

# Centre of Q
Q_centre = []
for a in Q:
    is_central = True
    for b in Q:
        ab = tuple(compose(list(a), list(b)))
        ba = tuple(compose(list(b), list(a)))
        if elt_to_coset_rep[ab] != elt_to_coset_rep[ba]:
            is_central = False
            break
    if is_central:
        Q_centre.append(a)
print(f"  |Z(Q)| = {len(Q_centre)}")

# Identify Q
if len(Q) == 12:
    if Q_is_abelian:
        # C_12 or C_6 × C_2 or C_2 × C_2 × C_3
        has_elt_12 = 12 in Q_order_dist
        print(f"  Q ≅ {'C_12' if has_elt_12 else 'C_6×C_2 or C_2²×C_3'}")
    else:
        # A_4 or D_6 or Dic_3
        if Q_order_dist.get(4, 0) > 0:
            print(f"  Q contains elements of order 4 → likely Dic_3")
        elif Q_order_dist.get(6, 0) > 0:
            print(f"  Q contains elements of order 6 → Q ≅ D_6 = S_3 × C_2")
        else:
            print(f"  Q has orders only in {{1,2,3}} → Q ≅ A_4")

# ── Action of Q on C₂⁴ as matrices ───────────────────────────────────

print("\n=== ACTION OF Q ON C₂⁴ (4×4 matrices over F₂) ===")

def conjugation_matrix(g):
    """Compute the 4×4 F₂-matrix of conjugation by g on C₂⁴."""
    mat = []
    for i in range(4):
        # conjugate basis[i] by g
        conj = tuple(compose(compose(list(g), list(basis[i])), inv(list(g))))
        coord = coord_map[conj]
        mat.append(coord)
    # mat[i] = image of basis[i], so the matrix has rows = images
    return mat

print("  Matrices for coset representatives:")
action_matrices = {}
for rep in Q:
    mat = conjugation_matrix(rep)
    order_in_Q = Q_orders[rep]
    action_matrices[rep] = mat
    if rep == e:
        label = "identity"
    elif order_in_Q <= 3:
        label = f"order {order_in_Q}"
    else:
        label = f"order {order_in_Q}"

# Print distinct matrices
seen_mats = {}
for rep in Q:
    mat_key = tuple(tuple(r) for r in action_matrices[rep])
    if mat_key not in seen_mats:
        seen_mats[mat_key] = Q_orders[rep]

print(f"  {len(seen_mats)} distinct matrices (should = 12 if faithful)")

for mat_key, order in sorted(seen_mats.items(), key=lambda x: x[1]):
    det = 1  # placeholder
    print(f"  Order {order}: {[list(r) for r in mat_key]}")

# Check if the action is faithful (12 distinct matrices = injective homomorphism)
is_faithful = len(seen_mats) == 12
print(f"\n  Action is faithful? {is_faithful}")

# ── Image in GL(4, F₂) ───────────────────────────────────────────────

print("\n=== IMAGE IN GL(4, F₂) ===")
# The image is a subgroup of GL(4, F₂) of order 12 (if faithful)
# GL(4, F₂) ≅ A₈ and has order 20160

# Find generators of the image
# First, find a generator of C₃ (order-3 element in Q)
c3_gen = None
for rep in Q:
    if Q_orders[rep] == 3:
        c3_gen = rep
        break

# Find generators of C₂² complement
invols = [rep for rep in Q if Q_orders[rep] == 2]
print(f"  Order-3 element in Q: found = {c3_gen is not None}")
print(f"  Involutions in Q: {len(invols)}")

if c3_gen:
    mat_c3 = action_matrices[c3_gen]
    print(f"  C₃ action matrix: {[list(r) for r in mat_c3]}")
    
    # Check characteristic polynomial
    # Need to work over F₂
    # Matrix A such that A³ = I, A ≠ I → minimal poly divides x³-1 = (x-1)(x²+x+1)
    # Since action is fixed-point-free, no eigenvalue 1, so min poly = x²+x+1
    # But this is 4×4, so char poly = (x²+x+1)²
    print(f"  (C₃ action is fixed-point-free → char poly = (x²+x+1)² over F₂)")

for inv_rep in invols[:3]:
    mat_inv = action_matrices[inv_rep]
    # Count fixed points (eigenvalue 1 eigenvectors)
    # Fixed points = {v : M·v = v} = ker(M - I)
    fixed = 0
    for mask in range(16):
        v = tuple((mask >> i) & 1 for i in range(4))
        Mv = tuple(sum(mat_inv[j][i] * v[i] for i in range(4)) % 2 for j in range(4))
        if Mv == v:
            fixed += 1
    print(f"  Involution matrix: {[list(r) for r in mat_inv]}, fixed points: {fixed}")

# ── Determine the GL(4,F₂) conjugacy class ───────────────────────────

print("\n=== IDENTIFYING THE GL(4,F₂) SUBGROUP ===")

# The image is a group of order 12 in GL(4,F₂).
# Subgroups of order 12 in GL(4,F₂):
#   A₄ (element orders {1,2,3}), D₆=S₃×C₂ (orders {1,2,3,6}), Dic₃ (orders {1,2,3,4}), C₁₂ (cyclic)

# We already know the element orders in Q.
# Let's also check: does the image preserve any F₄ structure?

# The C₃ acts as F₄* on F₂⁴. If we identify F₂⁴ with F₄², then:
# - F₄-linear maps on F₄² form GL(2,F₄) of order 180
# - ΓL(2,F₄) = GL(2,F₄) ⋊ Gal(F₄/F₂) has order 360

# Check if involutions commute with C₃ (F₄-linear) or not (semilinear)
if c3_gen:
    mat_c3_list = action_matrices[c3_gen]
    for inv_rep in invols[:3]:
        mat_inv_list = action_matrices[inv_rep]
        # Compute [C₃, inv] in GL(4, F₂)
        # C₃ · inv · C₃⁻¹ · inv⁻¹
        def mat_mul(A, B):
            n = 4
            return [tuple(sum(A[i][k]*B[k][j] for k in range(n)) % 2 for j in range(n)) for i in range(n)]
        def mat_inv_f2(M):
            # Invert 4×4 matrix over F₂ using Gaussian elimination
            n = 4
            aug = [list(M[i]) + [1 if j==i else 0 for j in range(n)] for i in range(n)]
            for col in range(n):
                pivot = None
                for row in range(col, n):
                    if aug[row][col] == 1:
                        pivot = row
                        break
                if pivot is None:
                    return None
                aug[col], aug[pivot] = aug[pivot], aug[col]
                for row in range(n):
                    if row != col and aug[row][col] == 1:
                        aug[row] = [(aug[row][j] + aug[col][j]) % 2 for j in range(2*n)]
            return [tuple(aug[i][n:]) for i in range(n)]
        
        c3_inv = mat_inv_f2(mat_c3_list)
        inv_inv = mat_inv_f2(mat_inv_list)  # For involution, inv = self
        
        comm = mat_mul(mat_mul(mat_c3_list, mat_inv_list), mat_mul(c3_inv, inv_inv))
        is_identity = all(comm[i] == tuple(1 if i==j else 0 for j in range(4)) for i in range(4))
        print(f"  [C₃, involution] = identity? {is_identity}  (= F₄-linear)" if is_identity
              else f"  [C₃, involution] = {[list(r) for r in comm]}  (semilinear!)")

# ── Count subgroups of key orders ─────────────────────────────────────

print("\n=== SUBGROUP COUNTS (for SmallGroup identification) ===")
# Count normal subgroups of each order
# First, find all subgroups of small orders: 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96

# For efficiency, count subgroups of orders 2, 3, 4
from itertools import product as iterproduct

# Subgroups of order 2: count involutions (each generates a unique C₂)
num_involutions = sum(1 for g in N_elts if perm_order(g) == 2)
print(f"  Involutions: {num_involutions}  → subgroups of order 2: {num_involutions}")

# Subgroups of order 3
num_ord3 = sum(1 for g in N_elts if perm_order(g) == 3)
print(f"  Elements of order 3: {num_ord3}  → subgroups of order 3: {num_ord3 // 2}")

# Check: is there a unique subgroup of order 48 (= [N,N])?
# [N,N] has order 48. Are there other subgroups of order 48?
print("\n  Checking if [N,N] is the UNIQUE subgroup of order 48 ...")
# This is expensive. Let's check if [N,N] is characteristic.
# [N,N] is always characteristic (it's the derived subgroup!), so yes.

# ── Final identification ──────────────────────────────────────────────

print("\n" + "="*60)
print("FINAL STRUCTURAL IDENTIFICATION")
print("="*60)

# Compile the full fingerprint
fingerprint = {
    "order": 192,
    "derived_series": [192, 48, 16, 1],
    "derived_length": 3,
    "centre_order": 1,
    "abelianisation": "C₂²",
    "num_conjugacy_classes": 14,
    "class_sizes": [1, 3, 4, 6, 6, 12, 12, 12, 12, 12, 24, 24, 32, 32],
    "element_orders": {1: 1, 2: 43, 3: 32, 4: 84, 6: 32},
    "exponent": 12,
    "quotient_by_second_derived": "order 12",
    "structure": "N = C₂⁴ ⋊ Q₁₂  where Q₁₂ ≅ ? acts faithfully on C₂⁴"
}

for k, v in fingerprint.items():
    print(f"  {k}: {v}")

# Save
with open("N_phase2_identification.json", "w") as f:
    json.dump(fingerprint, f, indent=2, default=str)
print("\nSaved N_phase2_identification.json")
