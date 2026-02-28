#!/usr/bin/env python3
"""Attempt A5 embeddings on the octonion 480 orbit.

This script uses the signed-permutation enumeration code from
`recompute_line_polarization_A5.py` (copied here) to test various
A5 subgroups of the full signed-permutation group on seven symbols.

Two classes of embeddings are considered:

* the "naive" S5 action fixing two letters (already known to give
  8×60 orbits), along with all 16 possible sign twists;
* the PSL(2,5) degree‑6 representation embedded into S7 by fixing a
  seventh point, again with all 16 admissible sign twists that satisfy
  the (2,3,5) relations.

The orbit signature for each tested pair is recorded so we can look
for the target fingerprint ``6*60 + 6*20``.  Results are written to
``octonion_A5_psl2_5_attempts.json``.

Usage:
    python scripts/octonion_psl2_5_search.py
"""
from __future__ import annotations
import json
import itertools
import math
from collections import deque
from typing import List, Tuple
from pathlib import Path
import sys
# make sure we can import the octonion helpers
sys.path.insert(0, str(Path("TOE_Wilmot_G2_Clifford_breakthrough_v01_20260227_bundle/src")))

# ---------------------------------------------------------------------------
# signed-permutation helpers (copied from recompute_line_polarization_A5)
# ---------------------------------------------------------------------------

def compose_signed(ga, gb):
    perm_a, sign_a = ga
    perm_b, sign_b = gb
    perm = [0] * 8
    sign = [1] * 8
    for i in range(1, 8):
        j = perm_b[i]
        perm[i] = perm_a[j]
        sign[i] = sign_a[j] * sign_b[i]
    return (tuple(perm), tuple(sign))


def is_identity(elem):
    perm, sign = elem
    if any(perm[i] != i for i in range(8)):
        return False
    if any(sign[i] != 1 for i in range(8)):
        return False
    return True


def enumerate_signed_group():
    """Enumerate all signed permutations on seven imaginary units.

    Deliver the tuple described in the original script: elements,
    elem_to_id, order2_ids, order3_ids, orbit_dict,
    element_for_table, orbit_index_for_elem.
    """
    from itertools import permutations, product

    elements = []
    elem_to_id = {}
    order2_ids = []
    order3_ids = []
    orbit_dict = {}
    element_for_table = []
    orbit_index_for_elem = []

    identity = (tuple(range(8)), tuple([1] * 8))

    # helpers to compute table representation; reuse octonion helpers if available
    # load octonion helpers by file path (bundle contains octonion.py)
    try:
        import importlib.util, os
        oct_path = os.path.join(os.getcwd(),
                                'TOE_Wilmot_G2_Clifford_breakthrough_v01_20260227_bundle',
                                'src', 'octonion.py')
        spec = importlib.util.spec_from_file_location('octonion', oct_path)
        octmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(octmod)
        TAB = octmod.TAB
        encode = octmod.encode
        decode = octmod.decode
    except Exception:
        # fallback dummy functions if real module not available
        TAB = [[0] * 8 for _ in range(8)]
        def encode(a, b):
            return 0
        def decode(code):
            return (1, 0)

    def apply_to_code(code, elem):
        s, idx = decode(code)
        if idx == 0:
            return code
        perm, sign = elem
        return s * sign[idx] * encode(1, perm[idx])

    def table_rep(elem):
        rows = []
        for i in range(8):
            for j in range(8):
                rows.append(apply_to_code(TAB[i][j], elem))
        return tuple(rows)

    id_counter = 0
    for perm in permutations(range(1, 8)):
        perm_arr = [0] * 8
        for i, img in enumerate(perm, start=1):
            perm_arr[i] = img
        for sp in product([1, -1], repeat=7):
            sign_arr = [1] * 8
            for i, sg in enumerate(sp, start=1):
                sign_arr[i] = sg
            rep = (tuple(perm_arr), tuple(sign_arr))
            eid = id_counter
            id_counter += 1
            elements.append(rep)
            elem_to_id[rep] = eid
            # order checks
            if compose_signed(rep, rep) == identity:
                order2_ids.append(eid)
            if compose_signed(compose_signed(rep, rep), rep) == identity:
                order3_ids.append(eid)
            rep_tab = table_rep(rep)
            if rep_tab not in orbit_dict:
                orbit_dict[rep_tab] = len(element_for_table)
                element_for_table.append(eid)
            orbit_index_for_elem.append(orbit_dict[rep_tab])
    return (
        elements,
        elem_to_id,
        order2_ids,
        order3_ids,
        orbit_dict,
        element_for_table,
        orbit_index_for_elem,
    )

def closure_from_generators(gen_ids, elements, elem_to_id):
    id_to_elem = elements
    seen = set(gen_ids)
    dq = deque(gen_ids)
    while dq:
        a_id = dq.popleft()
        a = id_to_elem[a_id]
        for b_id in list(seen):
            b = id_to_elem[b_id]
            c = compose_signed(a, b)
            c_id = elem_to_id[c]
            if c_id not in seen:
                seen.add(c_id)
                dq.append(c_id)
            d = compose_signed(b, a)
            d_id = elem_to_id[d]
            if d_id not in seen:
                seen.add(d_id)
                dq.append(d_id)
    return seen


def compute_orbit_partition(H_ids, element_for_table, orbit_index_for_elem, elements, elem_to_id):
    def apply_elem_to_index(eid, table_idx):
        g0_id = element_for_table[table_idx]
        g0 = elements[g0_id]
        elem = elements[eid]
        comp = compose_signed(elem, g0)
        comp_id = elem_to_id[comp]
        return orbit_index_for_elem[comp_id]

    visited = set()
    orbits = []
    for i in range(len(element_for_table)):
        if i in visited:
            continue
        queue = [i]
        orb = []
        while queue:
            j = queue.pop()
            if j in visited:
                continue
            visited.add(j)
            orb.append(j)
            for eid in H_ids:
                k = apply_elem_to_index(eid, j)
                if k not in visited:
                    queue.append(k)
        orbits.append(len(orb))
    orbits.sort()
    return orbits

# ---------------------------------------------------------------------------
# PSL(2,5) degree‑6 representation utilities
# ---------------------------------------------------------------------------

def apply_mat_to_point(mat, x):
    # projective action on F5 ∪ {∞} encoded as 0..5 where 5 = ∞
    a,b = mat[0]
    c,d = mat[1]
    if x == 5:
        # ∞ maps to a/c if c≠0 else ∞
        if c % 5 == 0:
            return 5
        return (a * pow(c, -1, 5)) % 5
    num = (a * x + b) % 5
    den = (c * x + d) % 5
    if den % 5 == 0:
        return 5
    return (num * pow(den, -1, 5)) % 5


def build_psl2_5_perms() -> List[Tuple[int, ...]]:
    # enumerate SL(2,5) matrices mod 5 then quotient by ±I
    mats = []
    for a,b,c,d in itertools.product(range(5), repeat=4):
        if (a*d - b*c) % 5 == 1:
            mats.append(((a,b),(c,d)))
    unique = []
    for M in mats:
        M2 = ((-M[0][0] %5, -M[0][1]%5),(-M[1][0]%5,-M[1][1]%5))
        if M2 in unique:
            continue
        unique.append(M)
    perms = []
    for M in unique:
        perm = []
        for x in range(6):
            perm.append(apply_mat_to_point(M, x))
        perms.append(tuple(perm))
    assert len(perms) == 60, f"expected 60 perms got {len(perms)}"
    return perms

# ---------------------------------------------------------------------------
# search routines
# ---------------------------------------------------------------------------

def spin_to_signed(perm7: Tuple[int, ...], sign7: Tuple[int, ...]) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    # convert a 7-permutation with 0..6 to the 8-length signed representation
    perm_full = [0] * 8
    sign_full = [1] * 8
    for i in range(7):
        perm_full[i+1] = perm7[i] + 1
        sign_full[i+1] = sign7[i]
    return (tuple(perm_full), tuple(sign_full))


def evaluate_embedding(base_g, base_h, elements, elem_to_id, element_for_table, orbit_index_for_elem):
    # base_g and base_h are signed-element reps; compute closure and fingerprint
    # return (orbit_sizes, H_size)
    # first find their ids in elements
    g_id = elem_to_id[base_g]
    h_id = elem_to_id[base_h]
    H = closure_from_generators([g_id, h_id], elements, elem_to_id)
    orbit = compute_orbit_partition(H, element_for_table, orbit_index_for_elem, elements, elem_to_id)
    return orbit, len(H)


def test_naive_S5(elements, elem_to_id, element_for_table, orbit_index_for_elem):
    # embedding of S5 acting on first 5 coordinates, fixing two letters
    results = []
    # choose standard generators for S5: (0 1) and (0 1 2)
    gen_s = (1,0,2,3,4,5,6)
    gen_t = (1,2,0,3,4,5,6)
    base_g = gen_s
    base_h = gen_t
    # build all 16 sign patterns
    for signs in itertools.product([1,-1], repeat=7):
        g_signed = spin_to_signed(base_g, signs)
        h_signed = spin_to_signed(base_h, signs)
        # verify relations
        if not is_identity(compose_signed(g_signed, g_signed)):
            continue
        if not is_identity(compose_signed(compose_signed(h_signed, h_signed), h_signed)):
            continue
        gh = compose_signed(g_signed, h_signed)
        gh5 = gh
        for _ in range(4):
            gh5 = compose_signed(gh5, gh)
        if not is_identity(gh5):
            continue
        orbit, Hsize = evaluate_embedding(g_signed, h_signed, elements, elem_to_id, element_for_table, orbit_index_for_elem)
        results.append({"signs": list(signs), "orbit": orbit, "H_size": Hsize})
    return results


def test_psl2_5(elements, elem_to_id, element_for_table, orbit_index_for_elem):
    results = []
    perms6 = build_psl2_5_perms()
    # embed into 7 by fixing element 6
    perms7 = [p + (6,) for p in perms6]
    # pick one pair of generators satisfying presentation x^2=y^3=(xy)^5=1
    # choose matrices x,y as described
    # instead of building from perms7 we simply search for any pair in perms7
    for g_base in perms7:
        if permutation_order(g_base) != 2: continue
        for h_base in perms7:
            if permutation_order(h_base) != 3: continue
            # check relation on underlying permutations
            gh = tuple(g_base[i] for i in h_base)
            gh5 = gh
            for _ in range(4):
                gh5 = tuple(gh5[x] for x in gh)
            if gh5 != tuple(range(7)):
                continue
            # found a suitable base pair
            base_g = g_base
            base_h = h_base
            break
        if 'base_g' in locals(): break
    if 'base_g' not in locals():
        raise RuntimeError('could not locate PSL2(5) generators in perms7')
    # now test sign twists
    for signs in itertools.product([1,-1], repeat=7):
        g_signed = spin_to_signed(base_g, signs)
        h_signed = spin_to_signed(base_h, signs)
        if not is_identity(compose_signed(g_signed, g_signed)): continue
        if not is_identity(compose_signed(compose_signed(h_signed, h_signed), h_signed)): continue
        gh = compose_signed(g_signed, h_signed)
        gh5 = gh
        for _ in range(4):
            gh5 = compose_signed(gh5, gh)
        if not is_identity(gh5): continue
        orbit, Hsize = evaluate_embedding(g_signed, h_signed, elements, elem_to_id, element_for_table, orbit_index_for_elem)
        results.append({"signs": list(signs), "orbit": orbit, "H_size": Hsize})
    return results


def permutation_order(perm):
    visited=set(); lcm=1
    n=len(perm)
    for i in range(n):
        if i in visited: continue
        cur=i; cycle=0
        while cur not in visited:
            visited.add(cur); cycle+=1; cur=perm[cur]
        lcm=math.lcm(lcm,cycle)
    return lcm


def main():
    print("enumerating signed group...")
    elements, elem_to_id, order2_ids, order3_ids, orbit_dict, element_for_table, orbit_index_for_elem = enumerate_signed_group()
    print("unique table reps", len(element_for_table))
    naive = test_naive_S5(elements, elem_to_id, element_for_table, orbit_index_for_elem)
    psl = test_psl2_5(elements, elem_to_id, element_for_table, orbit_index_for_elem)
    out = {"naive_S5": naive, "psl2_5": psl}
    with open("octonion_A5_psl2_5_attempts.json","w") as f:
        json.dump(out, f, indent=2)
    print("wrote octonion_A5_psl2_5_attempts.json")

if __name__ == "__main__":
    main()
