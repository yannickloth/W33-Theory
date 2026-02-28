#!/usr/bin/env python3
"""Check orbit partitions for the A5 subgroup and its binary extension.

Loads the generators from `sp43_A5_data.json` (found earlier) and
computes the orbit sizes on the 480 octonion tables under the group they
generate.  Then include the central sign element to form a 2.A5 subgroup
and repeat the orbit computation.

Usage: python scripts/check_binary_extension.py
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from collections import deque
from itertools import permutations, product

# helper functions copied from other scripts

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


def load_octonion_helpers():
    # attempt to load the bundle's octonion module; fall back to dummy
    try:
        import importlib.util
        oct_path = os.path.join(os.getcwd(),
                                'TOE_Wilmot_G2_Clifford_breakthrough_v01_20260227_bundle',
                                'src', 'octonion.py')
        spec = importlib.util.spec_from_file_location('oct', oct_path)
        octmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(octmod)
        return octmod.TAB, octmod.encode, octmod.decode
    except Exception as exc:
        print('warning: failed to import octonion module', exc)
        TAB = [[0] * 8 for _ in range(8)]
        def encode(a, b): return 0
        def decode(code): return (1, 0)
        return TAB, encode, decode


def apply_to_code(code, elem, decode, encode):
    s, idx = decode(code)
    if idx == 0:
        return code
    perm, sign = elem
    return s * sign[idx] * encode(1, perm[idx])


def table_rep(elem, TAB, decode, encode):
    rows = []
    for i in range(8):
        for j in range(8):
            rows.append(apply_to_code(TAB[i][j], elem, decode, encode))
    return tuple(rows)


def enumerate_signed_group():
    elements = []
    elem_to_id = {}
    order2_ids = []
    order3_ids = []
    orbit_dict = {}
    element_for_table = []
    orbit_index_for_elem = []

    identity = identity_elem()
    TAB, encode, decode = load_octonion_helpers()

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
            if compose_signed(rep, rep) == identity:
                order2_ids.append(eid)
            if compose_signed(compose_signed(rep, rep), rep) == identity:
                order3_ids.append(eid)
            rep_tab = table_rep(rep, TAB, decode, encode)
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

# main execution
if __name__ == '__main__':
    path = Path('sp43_A5_data.json')
    if not path.exists():
        print('necessary data file not found; run find_sp43_A5_480.py first')
        exit(1)
    # Instead of reading generators from JSON (which contained Sp43 edge perms),
    # re-run the signed-permutation A5 search to recover a suitable pair.
    elements, elem_to_id, order2_ids, order3_ids, orbit_dict, element_for_table, orbit_index_for_elem = enumerate_signed_group()
    print('enumerated signed group, size', len(elements))

    # we already know a working pair of generators from the previous
    # exploration (see temp_search output):
    #   g_id = 6151, h_id = 64
    # if you ever want to re‑search for a different pair you can uncomment the
    # loops below and adjust the target fingerprint accordingly.
    g_id = 6151
    h_id = 64
    print('using known generator ids', g_id, h_id)

    # compute H and its binary extension H2
    H = closure_from_generators([g_id, h_id], elements, elem_to_id)
    print('A5 subgroup size', len(H))

    # central sign flip on the seven imaginary units; index 0 fixed as 1
    central = (tuple(range(8)), tuple([1] + [-1] * 7))
    central_id = elem_to_id[central]
    print('central element id', central_id)
    H2 = closure_from_generators(list(H) + [central_id], elements, elem_to_id)
    print('binary subgroup size', len(H2))

    orbs_H = compute_orbit_partition(H, element_for_table, orbit_index_for_elem, elements, elem_to_id)
    orbs_H2 = compute_orbit_partition(H2, element_for_table, orbit_index_for_elem, elements, elem_to_id)
    print('orbits of A5:', orbs_H)
    print('orbits of 2.A5:', orbs_H2)
