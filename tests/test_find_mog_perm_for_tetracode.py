def test_find_mog_perm_for_tetracode():
    """Search (quick brute-force) for a MOG-symmetry permutation that makes
    all hexads satisfy the MiniMOG tetracode row-parity. Print permutation if
    found so we can inspect and apply the fix."""
    from itertools import permutations, product
    import THE_EXACT_MAP as exact

    def tetracode_words():
        G = [[1, 1, 1, 0], [0, 1, 2, 1]]
        words = set()
        for a in range(3):
            for b in range(3):
                w = [0] * 4
                for i in range(4):
                    w[i] = (a * G[0][i] + b * G[1][i]) % 3
                words.add(tuple(w))
        return words

    def row_counts_mod3_for_positions(hexad_positions):
        mini_rows = [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]
        counts = [sum(1 for p in mini_rows[r] if p in hexad_positions) % 3 for r in range(4)]
        return tuple(counts)

    columns = [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]
    hexads = list(exact.hexads)
    TC = tetracode_words()

    col_perms = list(permutations(range(4)))
    row_perms_all = list(product(*([list(permutations(range(3)))] * 4)))

    found = None
    for cp in col_perms:
        for rps in row_perms_all:
            perm_map = {}
            for orig_col in range(4):
                for r_idx, pos in enumerate(columns[orig_col]):
                    new_col = cp[orig_col]
                    new_row = rps[orig_col][r_idx]
                    target_pos = columns[new_col][new_row]
                    perm_map[pos] = target_pos
            ok = True
            for h in hexads:
                permuted = {perm_map[p] for p in h}
                rc = row_counts_mod3_for_positions(permuted)
                if rc not in TC:
                    ok = False
                    break
            if ok:
                found = (cp, rps, perm_map)
                break
        if found:
            break

    # Known result: exhaustive search + CP‑SAT show there is NO MOG‑symmetry
    # permutation that makes *all* 132 hexads satisfy the MiniMOG tetracode
    # row‑parity. Assert the negative and reference the investigation issue so
    # this test remains a regression guard if the situation changes.
    assert found is None, (
        "Expected no full‑cover MOG permutation (see ISSUES/0001‑MINI_MOG_"
        "TETRACODE_PARITY.md). If this assertion ever fails, capture and"
        " report the discovered permutation for follow‑up."
    )
