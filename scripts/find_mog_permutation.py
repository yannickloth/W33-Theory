"""
Search for a permutation of the 12 Golay positions that makes every hexad
satisfy the MiniMOG tetracode row-parity used in tests/test_mini_mog.py.

Strategy:
 - Try all column permutations (4! = 24)
 - For each column permutation, try all row-permutations within each column
   (3!^4 = 1296) => total ~31k permutations (fast).
 - For each candidate permutation p (mapping old_index -> new_index),
   check if for every hexad h in exact.hexads the row-counts mod3 of
   {p(i) for i in h} is in the tetracode word set.

If a working permutation is found, print it and exit.
"""
from itertools import permutations, product
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import THE_EXACT_MAP as exact

# mini_rows grouping expected by tests
mini_rows = [[0,4,8],[1,5,9],[2,6,10],[3,7,11]]

# tetracode words (same as tests)
G = [[1,1,1,0],[0,1,2,1]]
words = set()
for a in range(3):
    for b in range(3):
        w = tuple((a*G[0][i] + b*G[1][i]) % 3 for i in range(4))
        words.add(w)

# columns as used in THE_EXACT_MAP
columns = [ [0,4,8], [1,5,9], [2,6,10], [3,7,11] ]

# helper to compute row counts mod3 for a given hexad (after permuting positions)
def row_counts_mod3_for_hexad(hexad, perm):
    # perm is a mapping old_index -> new_index
    mapped = {perm[i] for i in hexad}
    counts = [sum(1 for p in mini_rows[r] if p in mapped) % 3 for r in range(4)]
    return tuple(counts)

# build all intra-column permutations (each column has 3! possibilities)
intra_perms = list(product(*[list(permutations(col)) for col in columns]))

# But we don't need all reorderings of labels inside columns; instead generate
# permutations as mappings from old_index -> new_index by permuting columns and
# applying a choice of ordering within each column.

def build_mapping(col_perm, intra_perm_choice):
    # col_perm: permutation of [0,1,2,3] indicating column order
    # intra_perm_choice: tuple of 4 permutations, each a tuple of 3 elements (old indices)
    mapping = {}
    for new_col_idx, old_col_idx in enumerate(col_perm):
        new_col = columns[new_col_idx]
        old_col = list(intra_perm_choice[old_col_idx])
        # we want to map each old position -> a new position (new_col[new_row_idx])
        for new_row_idx in range(3):
            old_pos = old_col[new_row_idx]
            new_pos = new_col[new_row_idx]
            mapping[old_pos] = new_pos
    return mapping

# Iterate column permutations and intra-column reorderings
col_perms = list(permutations(range(4)))
for col_perm in col_perms:
    for intra_choice in intra_perms:
        perm_map = build_mapping(col_perm, intra_choice)
        ok = True
        for h in exact.hexads:
            rc = row_counts_mod3_for_hexad(h, perm_map)
            if rc not in words:
                ok = False
                break
        if ok:
            print("Found permutation:")
            print(perm_map)
            # show as list mapping 0..11 -> perm_map[i]
            mapping_list = [perm_map[i] for i in range(12)]
            print(mapping_list)
            raise SystemExit(0)

print("No matching permutation found in column/row search")
