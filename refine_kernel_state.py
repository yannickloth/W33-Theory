"""Analyze CE2 sign map to determine minimal extra labels required for
axis-swap actions to become deterministic on the 8 observable patterns.

This script reproduces the "8 patterns" result from ChatGPT's earlier
analysis and computes equivalence classes of the tag triple
(t, w, z_sum) that suffice to make the A1/A2 transitions unambiguous.

Usage:  python refine_kernel_state.py
"""
from collections import defaultdict

from scripts.ce2_global_cocycle import (
    _simple_family_sign_map,
    _heisenberg_vec_maps,
    _f3_dot,
    _f3_omega,
    _f3_k_of_direction,
)

# helpers to extract invariants from a sign-map key

def invariants_from_triple(key):
    # given (c_i,match_i,other_i) as ints, compute (t,d,w,s,zsum)
    e6id_to_vec, _ = _heisenberg_vec_maps()
    c_i, match_i, other_i = key
    uc1, uc2, zc = e6id_to_vec[int(c_i)]
    um1, um2, zm = e6id_to_vec[int(match_i)]
    uo1, uo2, zo = e6id_to_vec[int(other_i)]
    t = 1 if (int(um1), int(um2)) == (int(uo1), int(uo2)) else 2
    d1 = (int(um1) - int(uc1)) % 3
    d2 = (int(um2) - int(uc2)) % 3
    w = _f3_omega((uc1, uc2), (d1, d2))
    s = _f3_dot((uc1, uc2), (d1, d2))
    zsum = (int(zm) + int(zo)) % 3
    return t, (d1, d2), int(w), int(s), int(zsum)

# build full dataset grouped by direction
sign_map = _simple_family_sign_map()
groups = defaultdict(list)  # (t,d,w,s,z) -> list of signs
for key, sgn in sign_map.items():
    t, d, w, s, z = invariants_from_triple(key)
    groups[(t, d, w, s, z)].append(int(sgn))

# sanity check: each invariant tuple should be consistent
for k, v in groups.items():
    if len(set(v)) != 1:
        raise RuntimeError(f"conflicting signs for invariants {k}: {v}")

# observable patterns are obtained by fixing an extra tag and letting
# s or w vary, depending on 'direction'.
# for d0=(1,0) seed patterns depend on w at fixed (t,s0,z).
# build map from (t,s0,z) -> pattern tuple of length3 indexed by w
seed_patterns = {}
for (t, d, w, s0, z), vals in groups.items():
    sgn = vals[0]
    if d == (1, 0):
        tag = (t, s0, z)
        seed_patterns.setdefault(tag, [None, None, None])[w] = sgn
# verify all patterns complete
for tag, pat in seed_patterns.items():
    assert None not in pat

# record the 8 unique seed patterns
unique_patterns = {tuple(p) for p in seed_patterns.values()}
print('unique seed patterns (%d):' % len(unique_patterns))
for pat in sorted(unique_patterns):
    print(pat)

# compute output patterns for axis swaps A1 (d=(0,1)) and A2 (d=(0,2))
output_patterns = {1: {}, 2: {}}  # swap_id -> tag -> pattern over s
for swap_id, target in [(1, (0, 1)), (2, (0, 2))]:
    for (t, d, w, s, z), vals in groups.items():
        sgn = vals[0]
        if d == target:
            # tag are the same (t,w,z) according to ChatGPT description
            tag = (t, w, z)
            output_patterns[swap_id].setdefault(tag, [None, None, None])[s] = sgn
    # check completeness
    for tag, pat in output_patterns[swap_id].items():
        assert None not in pat

# show some counts
print('\naxis-swap tag counts:')
for swap_id in (1, 2):
    print('swap', swap_id, 'tags', len(output_patterns[swap_id]))

# determine minimal partition of tags that makes mapping deterministic
def refine_tags_for_swap(swap_id):
    tags = list(output_patterns[swap_id].keys())
    # build mapping from tag -> output pattern
    out = output_patterns[swap_id]
    # two tags are equivalent if for every seed pattern they produce the
    # same output when the seed pattern matches the tag (via witness?)
    # but note the input pattern is determined by (t,s0,z), while tag is
    # (t,w,z). so to compare we need to consider all possible seed patterns
    # for fixed t,z with varying s0 and w. A seed pattern depends only on
    # (t,s0,z); output on (t,w,z).
    # we'll say that two tags (t,w,z) and (t',w',z') are equivalent if
    # t==t', z==z' and for all s0 the output patterns from these tags on any
    # seed pattern with that (t,s0,z) coincide. since patterns depend on
    # differing parameters, the equivalence will reduce to grouping by (t,z)
    # maybe plus some w info.
    eq_classes = []
    while tags:
        base = tags.pop()
        cls = [base]
        t0, w0, z0 = base
        for other in tags[:]:
            t1, w1, z1 = other
            if t0 != t1 or z0 != z1:
                continue
            # compare outputs on all seed patterns with same t,z
            good = True
            for (t_s, s0, z_s), seed_pat in seed_patterns.items():
                if t_s != t0 or z_s != z0:
                    continue
                # output for base tag and other tag using same seed
                out_base = out[base]
                out_other = out[other]
                # mapping from seed pattern to output pattern is not direct,
                # but we just check patterns themselves: they must be equal
                # for equivalence of tags.
                if out_base != out_other:
                    good = False
                    break
            if good:
                cls.append(other)
                tags.remove(other)
        eq_classes.append(cls)
    return eq_classes

for swap_id in (1,2):
    classes = refine_tags_for_swap(swap_id)
    print(f'\nswap {swap_id} has {len(classes)} equivalence classes of tags:')
    print(classes)

# The resulting classes represent a reduced tag set making the transition
# deterministic.  We can encode each class by a small integer.

"""
Running this script will print the eight seed patterns, the axis-swap tag
counts, and the partition of tags.  The classes indicate how many bits are
necessary for a phase tag.
"""
