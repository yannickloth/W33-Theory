"""
MATCH_E6_TRIADS_TO_COSETS.py

Attempt to find a bijection between E6 affine triads (36 triples) from
'artifacts/e6_cubic_affine_heisenberg_model.json' and the 36 pairwise-Hamming=6
triples found among the 27 coset-based codewords.
"""

import json
from collections import defaultdict
from itertools import combinations, product

import numpy as np

# Load e6 triples from affine heisenberg model
with open(
    "artifacts/e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    e6_heis = json.load(f)

# extract triads (36 triples) from affine_u_lines
e6_triads = []
for item in e6_heis["affine_u_lines"]:
    for tri in item["triads"]:
        e6_triads.append(tuple(sorted(tri)))

assert len(e6_triads) == 36
e6_triads = sorted(set(e6_triads))
assert len(e6_triads) == 36

# Build coset triads by reusing code from MAP_27_FROM_QUOTIENT.py
G_matrix = np.array(
    [
        [1, 0, 0, 0, 0, 0, 1, 1, 2, 2, 1, 2],
        [0, 1, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 2, 1, 1, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 2, 2, 1, 1, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 1, 2],
        [0, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1, 1],
    ]
)
M = np.array([[2, 2, 1, 2, 1, 2], [0, 2, 2, 0, 2, 1]], dtype=int)
messages = list(product(range(3), repeat=6))

kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]
W_basis = [(0, 0, 0, 0, 1, 1), (0, 0, 1, 0, 0, 1), (0, 1, 0, 1, 0, 1)]
W = set()
for a, b, c in product(range(3), repeat=3):
    w = tuple(
        (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
        for i in range(6)
    )
    W.add(w)

used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))

assert len(cosets) == 27


def message_to_codeword(m):
    v = np.array(m)
    return tuple((v @ G_matrix % 3).tolist())


codewords_27 = [message_to_codeword(m) for m in cosets]


# compute coset triads (pairwise hamming=6)
def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


coset_triads = []
for i, j, k in combinations(range(27), 3):
    if (
        hamming(codewords_27[i], codewords_27[j]) == 6
        and hamming(codewords_27[i], codewords_27[k]) == 6
        and hamming(codewords_27[j], codewords_27[k]) == 6
    ):
        coset_triads.append(tuple(sorted((i, j, k))))
coset_triads = sorted(set(coset_triads))
assert len(coset_triads) == 36

print("36 coset triads computed")

# Build incidence maps: for each label, list triads it belongs to

e6_triads_by_node = defaultdict(set)
for t in e6_triads:
    for v in t:
        e6_triads_by_node[v].add(t)

coset_triads_by_node = defaultdict(set)
for t in coset_triads:
    for v in t:
        coset_triads_by_node[v].add(t)

# signature: number of triads per node

e6_sig = {v: len(e6_triads_by_node[v]) for v in range(27)}
coset_sig = {v: len(coset_triads_by_node[v]) for v in range(27)}
print("unique e6 triad counts:", sorted(set(e6_sig.values())))
print("unique coset triad counts:", sorted(set(coset_sig.values())))

# load ordered couplings and coset coloring to allow stronger pruning
with open("artifacts/e6_ordered_couplings.json", "r", encoding="utf-8") as f:
    ordered_coups = json.load(f)
ORDERED_MAP = {(it["i"], it["j"]): (it["k"], int(it["raw"])) for it in ordered_coups}
with open("artifacts/coset_coloring.json", "r", encoding="utf-8") as f:
    coset_colors = json.load(f)["colors"]
from itertools import permutations

COLOR_PERMS = list(permutations([0, 1, 2]))

print("Loaded ORDERED_MAP length", len(ORDERED_MAP))

# try to find mapping via backtracking using signature and neighbor signature matching

# For each e6 node, candidates are coset nodes with same triad count
candidates = {v: [u for u in range(27) if coset_sig[u] == e6_sig[v]] for v in range(27)}

# order e6 nodes by number of candidates (smallest first)
order = sorted(range(27), key=lambda x: len(candidates[x]))
print(
    "min/max candidate counts",
    min(len(candidates[v]) for v in order),
    max(len(candidates[v]) for v in order),
)

# Precompute triad sets for quick checking

e6_triads_set = set(e6_triads)
coset_triads_set = set(coset_triads)

mapping = {}  # e6 -> coset
used_coset = set()

# For pruning: for any partial mapping, we can check whether for each e6 triad with all 3 nodes mapped, its mapped triple is in coset_triads_set


def check_partial(mapping):
    # mapping: e6id -> coset index
    # 1) fully mapped triads must map to coset triads
    for t in e6_triads:
        mapped = []
        unknown = False
        for v in t:
            if v in mapping:
                mapped.append(mapping[v])
            else:
                unknown = True
                break
        if not unknown:
            if tuple(sorted(mapped)) not in coset_triads_set:
                return False
    # 2) if two nodes of a triad are mapped, there must exist at least one coset node candidate
    #    for the third that completes a coset triad AND is compatible with an ordered coupling
    for t in e6_triads:
        mapped_nodes = [v for v in t if v in mapping]
        if len(mapped_nodes) == 2:
            unmapped_node = [v for v in t if v not in mapping][0]
            c1 = mapping[mapped_nodes[0]]
            c2 = mapping[mapped_nodes[1]]
            # candidates for third coset node: any unused coset node forming a triad with c1,c2
            possible = False
            for cand in range(27):
                if cand in mapping.values():
                    continue
                if tuple(sorted((c1, c2, cand))) not in coset_triads_set:
                    continue
                # now check ordered-coupling compatibility: try all color permutations
                ok_cand = False
                for col_perm in COLOR_PERMS:
                    # map coset nodes to new colors
                    colors_map = {
                        col_perm[coset_colors[c1]]: mapped_nodes[0],
                        col_perm[coset_colors[c2]]: mapped_nodes[1],
                        col_perm[coset_colors[cand]]: unmapped_node,
                    }
                    if set(colors_map.keys()) != {0, 1, 2}:
                        continue
                    v0 = colors_map[0]
                    v1 = colors_map[1]
                    v2 = colors_map[2]
                    # check ordered map for pair (v0,v1) -> v2
                    pair = (v0, v1)
                    if pair in ORDERED_MAP:
                        k_expect, raw = ORDERED_MAP[pair]
                        if k_expect == v2:
                            ok_cand = True
                            break
                if ok_cand:
                    possible = True
                    break
            if not possible:
                return False
    return True


# backtracking search with color-permutation outer loop
found = None

# step counter used for pruning inside backtracking
steps = 0
for col_perm in COLOR_PERMS:
    steps = 0
    print("Trying color permutation", col_perm)
    mapping = {}  # e6 -> coset
    used_coset = set()

    def check_partial_colperm(mapping):
        # same as check_partial but with fixed col_perm
        for t in e6_triads:
            mapped = []
            unknown = False
            for v in t:
                if v in mapping:
                    mapped.append(mapping[v])
                else:
                    unknown = True
                    break
            if not unknown:
                if tuple(sorted(mapped)) not in coset_triads_set:
                    return False
        for t in e6_triads:
            mapped_nodes = [v for v in t if v in mapping]
            if len(mapped_nodes) == 2:
                unmapped_node = [v for v in t if v not in mapping][0]
                c1 = mapping[mapped_nodes[0]]
                c2 = mapping[mapped_nodes[1]]
                possible = False
                used_vals = set(mapping.values())
                for cand in range(27):
                    if cand in used_vals:
                        continue
                    if tuple(sorted((c1, c2, cand))) not in coset_triads_set:
                        continue
                    # check ordered-coupling compatibility with fixed color perm
                    new_colors = {
                        col_perm[coset_colors[c1]]: mapped_nodes[0],
                        col_perm[coset_colors[c2]]: mapped_nodes[1],
                        col_perm[coset_colors[cand]]: unmapped_node,
                    }
                    if set(new_colors.keys()) != {0, 1, 2}:
                        continue
                    v0 = new_colors[0]
                    v1 = new_colors[1]
                    v2 = new_colors[2]
                    pair = (v0, v1)
                    if pair in ORDERED_MAP:
                        k_expect, raw = ORDERED_MAP[pair]
                        if k_expect == v2:
                            possible = True
                            break
                if not possible:
                    return False
        return True

    MAX_STEPS = 30000
    steps = 0

    def backtrack_colperm(idx=0):
        global steps, found
        steps += 1
        if steps % 10000 == 0:
            print("col_perm", col_perm, "steps", steps, "idx", idx)
        if steps > MAX_STEPS:
            return False
        if idx == len(order):
            found = mapping.copy()
            return True
        v = order[idx]
        # heuristic: try candidates in a deterministic but varied order
        for cand in candidates[v]:
            if cand in used_coset:
                continue
            mapping[v] = cand
            used_coset.add(cand)
            if check_partial_colperm(mapping):
                if backtrack_colperm(idx + 1):
                    return True
            used_coset.remove(cand)
            del mapping[v]
        return False

    # run backtracking with fixed color perm
    ok = backtrack_colperm()
    print("col_perm", col_perm, "ok?", ok)
    if ok:
        break

print("Mapping found?", found is not None)
if found is not None:
    map_list = [found[i] for i in range(27)]
    print("Mapping e6id -> coset index:", map_list)
    mapped_triads = [
        tuple(sorted((found[a], found[b], found[c]))) for (a, b, c) in e6_triads
    ]
    matched = set(mapped_triads) & set(coset_triads)
    print("Mapped triads matching coset triads count:", len(matched))

print("Done.")
