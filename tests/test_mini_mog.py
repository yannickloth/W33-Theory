import itertools

import pytest

import THE_EXACT_MAP as exact


def tetracode_words():
    # Generator matrix for tetracode over F3: rows as in repository notes
    G = [[1, 1, 1, 0], [0, 1, 2, 1]]
    words = set()
    for a in range(3):
        for b in range(3):
            w = [0, 0, 0, 0]
            for i in range(4):
                w[i] = (a * G[0][i] + b * G[1][i]) % 3
            words.add(tuple(w))
    return words


def row_counts_mod3(hexad):
    # MiniMOG row layout used in THE_EXACT_MAP.py
    rows = [list(range(0, 4)), list(range(4, 8)), list(range(8, 12))]
    # We use 4 rows of 3 columns in MiniMOG; map indices accordingly
    # In THE_EXACT_MAP the canonical rows are: [0,1,2,3],[4,5,6,7],[8,9,10,11]
    # For tetracode we need counts per *grouping of 4* (4 rows of 3 columns)
    # The MiniMOG 4×3 is interpreted as columns = [{0,4,8},{1,5,9},{2,6,10},{3,7,11}]
    # Rows (4 of them) are the column entries grouped by index within column-pair:
    mini_rows = [ [0,4,8], [1,5,9], [2,6,10], [3,7,11] ]
    counts = [sum(1 for p in mini_rows[r] if p in hexad) % 3 for r in range(4)]
    return tuple(counts)


def test_golay_has_132_hexads():
    # Use hexads built in THE_EXACT_MAP (canonical generator used throughout repo)
    hexads = exact.hexads
    assert len(hexads) == 132


def test_hexads_satisfy_miniMOG_tetracode_row_parity():
    hexads = exact.hexads
    tc = tetracode_words()

    bad = []
    for h in hexads:
        rc = row_counts_mod3(h)
        if rc not in tc:
            bad.append((h, rc))

    assert not bad, f"Some hexads fail the MiniMOG tetracode row‑parity: {bad[:5]}"


def test_build_mog_map_is_bijection_and_signatures():
    pos_to_line = exact.build_mog_map()
    # bijection 0..11 -> 0..11
    assert set(pos_to_line.keys()) == set(range(12))
    assert len(set(pos_to_line.values())) == 12

    # For every hexad, the parallel‑class signature sums to 6
    sigs = [exact.hexad_parallel_signature(h, pos_to_line) for h in exact.hexads]
    assert all(sum(s) == 6 for s in sigs)
    # signatures should not be all identical (sanity check)
    assert len(set(sigs)) > 1
