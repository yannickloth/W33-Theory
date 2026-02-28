#!/usr/bin/env python3
"""Search for binary icosahedral subgroups acting on the octonion 480 orbit.

A binary icosahedral group is a double cover of A5 of order 120.  In the
signed-permutation model the nontrivial central element is the sign flip of all
seven imaginary units.  A convenient presentation uses generators of orders
4 and 6 whose squares equal the central element and whose product has order
10 (i.e. (gh)^5 = z).  We can therefore scan the signed group for pairs
satisfying:

    ord(g)=4, ord(h)=6,
    g^2 = z, h^3 = z,
    (g*h)^5 = z

If we find such a pair the closure should have size 120.  We'll compute the
orbit partition of the 480 octonion tables and look for the 6×20+6×60
fingerprint (or any nontrivial partition) to see if these subgroups realise the
W33 orbit on the octonion side.

Usage:
    python scripts/octonion_binary_A5_search.py

The search is still somewhat expensive but far smaller than scanning all
element pairs: there are significantly fewer order-4 and order-6 elements.
"""
from __future__ import annotations
import math
import os
from collections import deque
from itertools import permutations, product

import sys
from pathlib import Path

# copypasta from other scripts
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

def identity_elem():
    return (tuple(range(8)), tuple([1] * 8))

def power(elem, n):
    result = identity_elem()
    for _ in range(n):
        result = compose_signed(result, elem)
    return result

def order(elem):
    iden = identity_elem()
    cur = elem
    for k in range(1, 1000):
        if cur == iden:
            return k
        cur = compose_signed(cur, elem)
    return None

# enumeration functions (same as in other scripts)
def enumerate_signed_group():
    from itertools import permutations, product

    elements = []
    elem_to_id = {}
    order2_ids = []
    order3_ids = []
    order4_ids = []
    order6_ids = []
    orbit_dict = {}
    element_for_table = []
    orbit_index_for_elem = []

    identity = identity_elem()
    # try to import octonion module for table rep
    TAB = None
    try:
        import importlib.util
        oct_path = os.path.join(os.getcwd(),
                                'TOE_Wilmot_G2_Clifford_breakthrough_v01_20260227_bundle',
                                'src', 'octonion.py')
        spec = importlib.util.spec_from_file_location('oct', oct_path)
        octmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(octmod)
        TAB = octmod.TAB
        encode = octmod.encode
        decode = octmod.decode
    except Exception as exc:
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
            o = order(rep)
            if o == 2:
                order2_ids.append(eid)
            if o == 3:
                order3_ids.append(eid)
            if o == 4:
                order4_ids.append(eid)
            if o == 6:
                order6_ids.append(eid)
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
        order4_ids,
        order6_ids,
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


def main():
    print('enumerating signed group...')
    (elements, elem_to_id, order2_ids, order3_ids,
     order4_ids, order6_ids, orbit_dict,
     element_for_table, orbit_index_for_elem) = enumerate_signed_group()
    print('size', len(elements))
    z = (tuple(range(8)), tuple([1] + [-1] * 7))  # central flip
    z_id = elem_to_id[z]
    print('central id', z_id)

    target = [20] * 6 + [60] * 6
    for g_id in order4_ids:
        # g^2 should equal central
        if elem_to_id[power(elements[g_id], 2)] != z_id:
            continue
        for h_id in order6_ids:
            if elem_to_id[power(elements[h_id], 3)] != z_id:
                continue
            gh = compose_signed(elements[g_id], elements[h_id])
            if elem_to_id[power(gh, 5)] != z_id:
                continue
            H_ids = closure_from_generators([g_id, h_id], elements, elem_to_id)
            if len(H_ids) != 120:
                continue
            orbs = compute_orbit_partition(H_ids, element_for_table, orbit_index_for_elem, elements, elem_to_id)
            print('candidate', g_id, h_id, 'orbit', orbs)
            if orbs == target:
                print('found matching binary A5')
                return
    print('search finished')

if __name__ == '__main__':
    main()
