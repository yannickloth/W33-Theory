"""Search for a MOG column/row permutation that makes all hexads pass
the MiniMOG tetracode row-parity test.

This tries permutations that are compositions of:
 - permuting the 4 MOG columns (4!)
 - permuting rows within each column (3! per column)

If a solution is found, prints the permutation mapping (old -> new).
"""

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
    counts = [
        sum(1 for p in mini_rows[r] if p in hexad_positions) % 3 for r in range(4)
    ]
    return tuple(counts)


columns = [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]
hexads = list(exact.hexads)
TC = tetracode_words()

print(f"Checking {len(hexads)} hexads from THE_EXACT_MAP")

# iterate column permutations and intra-column row permutations
col_perms = list(permutations(range(4)))
row_perms_all = list(product(*([list(permutations(range(3)))] * 4)))

print(
    f"Trying {len(col_perms)} column perms × {len(row_perms_all)} intra-column perms = {len(col_perms) * len(row_perms_all)} total"
)

found = None
for cp in col_perms:
    # cp maps original column i -> new column index cp[i]
    for rps in row_perms_all:
        # rps is a tuple of 4 row-permutations, one per original column
        perm_map = {}
        for orig_col in range(4):
            for r_idx, pos in enumerate(columns[orig_col]):
                new_col = cp[orig_col]
                new_row = rps[orig_col][r_idx]
                target_pos = columns[new_col][new_row]
                perm_map[pos] = target_pos
        # build full perm for 0..11
        perm = tuple(perm_map[i] for i in range(12))
        ok = True
        for h in hexads:
            permuted = {perm_map[p] for p in h}
            rc = row_counts_mod3_for_positions(permuted)
            if rc not in TC:
                ok = False
                break
        if ok:
            found = (cp, rps, perm)
            break
    if found:
        break

if not found:
    print(
        "No MOG-symmetry permutation found that makes all hexads pass tetracode parity."
    )
else:
    cp, rps, perm = found
    print("Found solution!")
    print("column_perm:", cp)
    print("row_perms:")
    for i, rp in enumerate(rps):
        print(f"  col {i}: {rp}")
    print("perm (old_index -> new_index):")
    for i, v in enumerate(perm):
        print(f"  {i} -> {v}")
    # print a few failing-check examples for sanity
    bad_examples = []
    for h in hexads:
        permuted = {perm[p] for p in h}
        rc = row_counts_mod3_for_positions(permuted)
        if rc not in TC:
            bad_examples.append((h, rc))
    print("bad_examples_after_perm (should be empty)", bad_examples[:5])
