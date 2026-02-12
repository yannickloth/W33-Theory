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


def row_sums_mod3(codeword):
    # MiniMOG 4×3 layout used in THE_EXACT_MAP.py; tetracode coords are
    # the sum of codeword *values* in each column-group, taken mod 3.
    mini_rows = [ [0,4,8], [1,5,9], [2,6,10], [3,7,11] ]
    sums = [sum(codeword[p] for p in mini_rows[r]) % 3 for r in range(4)]
    return tuple(sums)


def test_golay_has_132_hexads():
    # Use hexads built in THE_EXACT_MAP (canonical generator used throughout repo)
    hexads = exact.hexads
    assert len(hexads) == 132


def test_tetracode_words_appear_in_weight6_row_sums():
    # Verify that every tetracode word appears as the column-sums of at least
    # one weight-6 Golay codeword (MiniMOG ↔ tetracode embedding).
    weight6 = exact.weight_6
    tc = tetracode_words()

    mini_rows = [ [0,4,8], [1,5,9], [2,6,10], [3,7,11] ]
    from collections import Counter
    observed = Counter(
        tuple(sum(int(c[p]) for p in mini_rows[i]) % 3 for i in range(4))
        for c in weight6
    )

    # every tetracode word must appear at least once
    assert tc.issubset(set(observed.keys()))

    # sanity: a fixed total number of weight-6 codewords map into tetracode words
    total_mapped = sum(observed[w] for w in tc)
    assert total_mapped == 26, "Unexpected number of weight-6 codewords mapping to tetracode words"


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
