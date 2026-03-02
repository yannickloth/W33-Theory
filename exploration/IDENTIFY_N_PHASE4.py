"""
Phase 4: Analyze O₂(N) (order 32) and refine structural description.

Key questions:
1. What is O₂(N) as an abstract group?
2. How does O₂(N) relate to [N,N]?
3. What is N/O₂(N)?
4. Action signature for SmallGroup matching
"""

import json, itertools
from collections import Counter

with open("N_subgroup.json") as f:
    N_elts = json.load(f)

e = list(range(len(N_elts[0])))

def compose(a, b):
    return [a[x] for x in b]

def inv(p):
    r = [0]*len(p)
    for i,v in enumerate(p): r[v] = i
    return r

def perm_order(p):
    x = p[:]
    for k in range(1, 300):
        if x == e: return k
        x = compose(x, p)
    return -1

def close_subgroup(gens, all_elts_set=None):
    """Close a set of generators under composition and inverse"""
    sub = {tuple(e)}
    queue = [tuple(g) for g in gens]
    for g in queue:
        sub.add(g)
    while queue:
        g = queue.pop()
        for s in list(sub):
            for prod in [compose(list(g), list(s)), compose(list(s), list(g))]:
                tp = tuple(prod)
                if tp not in sub:
                    sub.add(tp)
                    queue.append(tp)
    return [list(s) for s in sub]

def commutator(a, b):
    return compose(compose(a, b), compose(inv(a), inv(b)))

def commutator_subgroup(H, K):
    """Generate [H, K]"""
    comms = []
    for h in H:
        for k in K:
            comms.append(commutator(h, k))
    if not comms:
        return [e]
    return close_subgroup(comms)

def conjugate(g, h):
    """h^{-1} g h"""
    return compose(compose(inv(h), g), h)

def is_normal(sub, ambient):
    sub_set = {tuple(s) for s in sub}
    for g in ambient:
        for s in sub:
            if tuple(conjugate(s, g)) not in sub_set:
                return False
    return True

# ============================================================
# 1. Recompute O₂(N) explicitly
# ============================================================
print("=" * 60)
print("PHASE 4: ANALYZING O₂(N)")
print("=" * 60)

# Find all normal 2-subgroups
N_set = {tuple(g) for g in N_elts}

# Start by finding C₂⁴ = [[N,N],[N,N]]
deriv1 = commutator_subgroup(N_elts, N_elts)
print(f"|[N,N]| = {len(deriv1)}")
deriv2 = commutator_subgroup(deriv1, deriv1)
print(f"|[[N,N],[N,N]]| = {len(deriv2)}")

C24 = deriv2  # This is C₂⁴
C24_set = {tuple(g) for g in C24}

# Get element orders in C₂⁴
c24_orders = Counter(perm_order(g) for g in C24)
print(f"C₂⁴ element orders: {dict(c24_orders)}")

# Identify the F₂-linear involution (centre of D₆)
# From Phase 2: the central involution z of D₆ commutes with C₃ elements
# and acts as a transvection on C₂⁴.

# Find elements of order 2 NOT in C₂⁴
involutions_outside = [g for g in N_elts if perm_order(g) == 2 and tuple(g) not in C24_set]
print(f"\nInvolutions outside C₂⁴: {len(involutions_outside)}")

# Find which involutions normalize C₂⁴ (all should, since C₂⁴ ⊴ N)
# Find which involutions are in O₂(N) — they must be in all Sylow-2 subgroups
# Actually, O₂(N) = largest normal 2-subgroup = ∩ Sylow₂'s = ... no, O₂(N) is the LARGEST normal 2-subgroup

# Let me find the Sylow-2 subgroups first
order3_elts = [g for g in N_elts if perm_order(g) == 3]
print(f"\nOrder-3 elements: {len(order3_elts)}")

# Pick one order-3 element
c3 = order3_elts[0]
c3_inv = inv(c3)

# A Sylow-2 subgroup is the centralizer... no.
# Sylow-2 = normalizer of Sylow-3? No. 
# Actually, Sylow-2 has order 64 and index 3.
# With 3 Sylow-2 subgroups, N acts on them by conjugation → S₃ action

# Let's find Sylow-2 subgroups directly.
# Take a 2-element and close under multiplication to get a Sylow-2
two_elts = [g for g in N_elts if perm_order(g) in [1, 2, 4]]
print(f"Elements of 2-power order: {len(two_elts)}")

# The Sylow-2 subgroups partition... no they don't. 
# Let me find one Sylow-2: take maximal 2-subgroup containing our known 2-elements
# Start from C₂⁴ and extend

# Strategy: C₂⁴ has 16 elements. Sylow-2 has 64. 
# Pick involutions outside C₂⁴ that normalize C₂⁴ and form a 2-group with it.

# Actually, let me just use the computational approach from Phase 3.
# Pick a 2-element not in C₂⁴ and generate iteratively.

# Better: find ALL Sylow-2 subgroups
# Since there are exactly 3, we can find them

# Take one involution outside C₂⁴ and close with C₂⁴
test_inv = involutions_outside[0]
syl2_candidate = close_subgroup(C24 + [test_inv])
print(f"\nClosing C₂⁴ + 1 involution: |closure| = {len(syl2_candidate)}")

if len(syl2_candidate) < 64:
    # Need more generators
    remain = [g for g in two_elts if tuple(g) not in {tuple(s) for s in syl2_candidate}]
    if remain:
        syl2_candidate = close_subgroup(syl2_candidate + [remain[0]])
        print(f"Adding another: |closure| = {len(syl2_candidate)}")

if len(syl2_candidate) < 64:
    remain = [g for g in two_elts if tuple(g) not in {tuple(s) for s in syl2_candidate}]
    if remain:
        syl2_candidate = close_subgroup(syl2_candidate + [remain[0]])
        print(f"Adding another: |closure| = {len(syl2_candidate)}")

if len(syl2_candidate) == 64:
    print("Found Sylow-2 subgroup P₁!")
    P1 = syl2_candidate
    P1_set = {tuple(g) for g in P1}
    
    # Find P₂ by conjugating P₁ by an order-3 element
    P2 = [conjugate(g, c3) for g in P1]
    P2_set = {tuple(g) for g in P2}
    print(f"|P₂| = {len(P2_set)}")
    
    P3 = [conjugate(g, compose(c3, c3)) for g in P1]
    P3_set = {tuple(g) for g in P3}
    print(f"|P₃| = {len(P3_set)}")
    
    # O₂(N) = P₁ ∩ P₂ ∩ P₃ (since O₂(N) is in every Sylow-2, and 
    # it equals the intersection when N has a normal Sylow complement situation)
    # Actually, O₂(N) ⊆ P₁ ∩ P₂ ∩ P₃, but they need not be equal.
    # The intersection of all Sylow-p's is O_p(G) when it's normal.
    
    O2_intersection = P1_set & P2_set & P3_set
    print(f"\n|P₁ ∩ P₂ ∩ P₃| = {len(O2_intersection)}")
    
    O2_elts = [list(g) for g in O2_intersection]
    
    # Check normality
    norm = is_normal(O2_elts, N_elts)
    print(f"P₁ ∩ P₂ ∩ P₃ normal in N? {norm}")
    
    # Verify this is the O₂(N) we found before
    print(f"\n*** O₂(N) = P₁ ∩ P₂ ∩ P₃ has order {len(O2_elts)} ***")
else:
    print(f"Warning: Sylow-2 generation didn't reach 64, got {len(syl2_candidate)}")
    # Fallback: compute O₂(N) directly
    # O₂(N) is the largest normal 2-subgroup
    # Find all normal subgroups that are 2-groups
    O2_elts = None

# ============================================================
# 2. Analyze O₂(N) structure
# ============================================================
if len(O2_elts) == 32:
    print("\n" + "=" * 60)
    print("O₂(N) STRUCTURE ANALYSIS")
    print("=" * 60)
    
    o2_orders = Counter(perm_order(g) for g in O2_elts)
    print(f"Element orders: {dict(o2_orders)}")
    
    # Centre of O₂(N)
    O2_set = {tuple(g) for g in O2_elts}
    centre = []
    for g in O2_elts:
        central = True
        for h in O2_elts:
            if tuple(compose(g, h)) != tuple(compose(h, g)):
                central = False
                break
        if central:
            centre.append(g)
    print(f"|Z(O₂(N))| = {len(centre)}")
    centre_orders = Counter(perm_order(g) for g in centre)
    print(f"Z(O₂(N)) element orders: {dict(centre_orders)}")
    
    # Derived subgroup of O₂(N)
    o2_deriv = commutator_subgroup(O2_elts, O2_elts)
    print(f"|[O₂(N), O₂(N)]| = {len(o2_deriv)}")
    o2_deriv_orders = Counter(perm_order(g) for g in o2_deriv)
    print(f"[O₂(N),O₂(N)] element orders: {dict(o2_deriv_orders)}")
    
    # Frattini subgroup Φ(O₂(N)) for a 2-group = [O₂(N),O₂(N)] · O₂(N)²
    # For a 2-group, Φ = [G,G]·G² where G² = {g² : g ∈ G}
    squares = {tuple(compose(g, g)) for g in O2_elts}
    print(f"|{'{'}g² : g ∈ O₂(N){'}'}| = {len(squares)}")
    
    # Frattini = closure of [G,G] ∪ G²
    frat_gens = o2_deriv + [list(s) for s in squares]
    frat = close_subgroup(frat_gens)
    print(f"|Φ(O₂(N))| = {len(frat)}")
    
    # Exponent
    max_ord = max(perm_order(g) for g in O2_elts)
    print(f"Exponent of O₂(N): {max_ord}")
    
    # Nilpotency class (O₂(N) is a 2-group, hence nilpotent)
    gamma = O2_elts[:]
    lcs_series = [len(gamma)]
    for i in range(10):
        gamma = commutator_subgroup(O2_elts, gamma)
        lcs_series.append(len(gamma))
        if len(gamma) == 1:
            break
    print(f"Lower central series of O₂(N): {lcs_series}")
    print(f"Nilpotency class: {len(lcs_series) - 2}")
    
    # How does O₂(N) relate to C₂⁴?
    o2_cap_c24 = O2_set & C24_set
    print(f"\n|O₂(N) ∩ C₂⁴| = {len(o2_cap_c24)}")
    
    # O₂(N) ∩ [N,N]
    deriv1_set = {tuple(g) for g in deriv1}
    o2_cap_deriv = O2_set & deriv1_set
    print(f"|O₂(N) ∩ [N,N]| = {len(o2_cap_deriv)}")
    
    # Check if C₂⁴ ⊂ O₂(N)
    print(f"C₂⁴ ⊂ O₂(N)? {C24_set <= O2_set}")
    
    # O₂(N) / C₂⁴
    print(f"|O₂(N)/C₂⁴| = {len(O2_elts) // len(C24)} (if C₂⁴ ⊂ O₂(N))")
    
    # Find elements of O₂(N) NOT in C₂⁴
    o2_outside_c24 = [g for g in O2_elts if tuple(g) not in C24_set]
    print(f"Elements of O₂(N) outside C₂⁴: {len(o2_outside_c24)}")
    outside_orders = Counter(perm_order(g) for g in o2_outside_c24)
    print(f"Their orders: {dict(outside_orders)}")
    
    # Check: are these all involutions that commute with C₃?
    # (i.e., are they F₄-linear transvections?)
    c3_orders = [g for g in N_elts if perm_order(g) == 3]
    for g in o2_outside_c24[:3]:  # Check first few
        commutes_with_c3 = any(
            tuple(compose(g, c)) == tuple(compose(c, g)) 
            for c in c3_orders
        )
        print(f"  outside element (order {perm_order(g)}): commutes with some C₃? {commutes_with_c3}")
    
    # ============================================================
    # 3. Check which involutions are in O₂(N)
    # ============================================================
    print("\n" + "=" * 60)
    print("CONJUGACY CLASS ANALYSIS OF O₂(N)")
    print("=" * 60)
    
    # Conjugacy classes of O₂(N) itself
    o2_classes = []
    classified = set()
    for g in O2_elts:
        tg = tuple(g)
        if tg in classified:
            continue
        cls = set()
        for h in O2_elts:
            c = conjugate(g, h)
            cls.add(tuple(c))
        o2_classes.append((perm_order(g), len(cls)))
        classified |= cls
    
    o2_classes.sort()
    print(f"Conjugacy classes of O₂(N): {o2_classes}")
    print(f"Number of conjugacy classes: {len(o2_classes)}")
    
    # ============================================================
    # 4. N/O₂(N) analysis
    # ============================================================
    print("\n" + "=" * 60)
    print("QUOTIENT N/O₂(N)")
    print("=" * 60)
    
    # Cosets
    cosets = []
    covered = set()
    for g in N_elts:
        tg = tuple(g)
        if tg in covered:
            continue
        coset = frozenset(tuple(compose(g, h)) for h in O2_elts)
        cosets.append(coset)
        covered |= coset
    
    print(f"|N/O₂(N)| = {len(cosets)}")
    
    # Representative orders
    coset_reps = []
    for coset in cosets:
        rep = list(list(coset)[0])
        rep_order = perm_order(rep)
        # All elements in coset have same order mod O₂(N)?
        # Actually they can have different orders. Find min order of elements.
        elem_orders = {perm_order(list(c)) for c in coset}
        coset_reps.append(sorted(elem_orders))
    
    print("Element orders in each coset of O₂(N):")
    for i, ords in enumerate(coset_reps):
        print(f"  Coset {i}: {Counter(ords)}")
    
    # Check if N/O₂(N) ≅ S₃ or C₆
    # S₃ has elements of orders 1, 2, 2, 2, 3, 3
    # C₆ has elements of orders 1, 2, 3, 3, 6, 6
    
    # ============================================================
    # 5. Is O₂(N) abelian?
    # ============================================================
    print("\n" + "=" * 60)
    print("IS O₂(N) ABELIAN?")
    print("=" * 60)
    
    is_abelian = True
    for i, g in enumerate(O2_elts):
        for j, h in enumerate(O2_elts):
            if i >= j:
                continue
            if tuple(compose(g, h)) != tuple(compose(h, g)):
                is_abelian = False
                break
        if not is_abelian:
            break
    print(f"O₂(N) abelian? {is_abelian}")
    
    if not is_abelian:
        # Find the non-commuting pair
        for g in O2_elts:
            for h in O2_elts:
                if tuple(compose(g, h)) != tuple(compose(h, g)):
                    print(f"  Non-commuting: order {perm_order(g)} × order {perm_order(h)}")
                    comm = commutator(g, h)
                    print(f"  Commutator order: {perm_order(comm)}")
                    break
            else:
                continue
            break
    
    # ============================================================
    # 6. O₂(N) presentation search
    # ============================================================
    print("\n" + "=" * 60)
    print("O₂(N) GROUP IDENTIFICATION")
    print("=" * 60)
    
    # For a group of order 32, the key invariants are:
    # - abelian or not
    # - exponent
    # - |Z|, |G'|, |Φ|
    # - number of conjugacy classes
    # - element order distribution
    
    # GAP SmallGroup(32, ?) has 51 groups
    # Let's compile our fingerprint:
    
    fingerprint = {
        "order": 32,
        "abelian": is_abelian,
        "exponent": max_ord,
        "center_order": len(centre),
        "derived_order": len(o2_deriv),
        "frattini_order": len(frat),
        "num_conjugacy_classes": len(o2_classes),
        "element_orders": dict(o2_orders),
        "conjugacy_class_fingerprint": o2_classes,
        "nilpotency_class": len(lcs_series) - 2,
    }
    
    print(f"O₂(N) fingerprint:")
    for k, v in fingerprint.items():
        print(f"  {k}: {v}")
    
    # Special checks for known groups of order 32:
    # C₂⁵: abelian, 32 conjugacy classes, all involutions
    # C₄ × C₂³: abelian
    # D₁₆ × C₂: |Z|=2, |G'|=8, exp=16
    # Q₃₂: |Z|=2, |G'|=16, exp=32
    # Extra-special 2⁵: |Z|=2, |G'|=2, Φ=Z
    #   Two types: 2₊^(1+4) (D₈*D₈) and 2₋^(1+4) (Q₈*D₈)
    # Central product types
    
    # Check if extra-special: |Z|=2 and G' = Z = Φ
    if len(centre) == 2 and len(o2_deriv) == 2 and len(frat) == 2:
        print("\n*** O₂(N) is EXTRA-SPECIAL of order 32 = 2^(1+4) ***")
        # Type +: all elements of order ≤ 4, 2^4 elements of order 2
        # Type -: some elements of order 4
        if o2_orders.get(2, 0) > 0:
            n2 = o2_orders[2]
            if n2 == 27:
                print("  Type: too many involutions for extra-special (should be ≤15)")
            elif n2 == 15:
                print("  Type: 2₊^(1+4) ≅ D₈ * D₈ (central product)")
            elif n2 == 7:
                print("  Type: 2₋^(1+4) ≅ Q₈ * D₈")
            else:
                print(f"  Involution count: {n2}")
    elif len(centre) == 4 and len(o2_deriv) == 2:
        print("\n*** O₂(N) has |Z|=4, |G'|=2 — almost extra-special ***")
    elif len(centre) == 4 and len(o2_deriv) == 4:  
        print("\n*** O₂(N) has |Z|=4, |G'|=4 ***")
    
    # ============================================================
    # 7. Save results
    # ============================================================
    
    # Save O₂(N) elements for future use
    results = {
        "O2_order": len(O2_elts),
        "O2_fingerprint": fingerprint,
        "O2_is_intersection_of_sylows": True,
        "C24_subset_of_O2": bool(C24_set <= O2_set),
        "O2_cap_derived": len(o2_cap_deriv),
        "quotient_order": len(cosets),
        "O2_conjugacy_classes": o2_classes,
    }
    
    with open("N_phase4_O2_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Phase 4 results saved to N_phase4_O2_analysis.json")

print("\n" + "=" * 60)
print("PHASE 4 COMPLETE")
print("=" * 60)
