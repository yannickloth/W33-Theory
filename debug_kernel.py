from scripts.ce2_kernel_action import build_kernel_tables

try:
    patterns, tags, a1, a2 = build_kernel_tables()
    print('built tables successfully: patterns=', len(patterns))
except AssertionError as e:
    print('Assertion error during build:', e)
    # compute manually
    from scripts.ce2_kernel_action import _simple_family_sign_map, _invariants_from_triple
    sign_map = _simple_family_sign_map()
    seed_patterns = {}
    for key, sgn in sign_map.items():
        t, d, w, s, z = _invariants_from_triple(key)
        if d == (1, 0):
            seed_tag = (t, s, z)
            pat = list(seed_patterns.get(seed_tag, (None, None, None)))
            pat[w] = int(sgn)
            seed_patterns[seed_tag] = tuple(pat)
    seed_patterns = {t: p for t, p in seed_patterns.items() if None not in p}
    patterns = sorted(set(seed_patterns.values()))
    print('manual pattern count', len(patterns))
    print('patterns', patterns)
    print('seed patterns keys', list(seed_patterns.keys()))
    print('tag count', len(set(list(seed_patterns.keys()))))
else:
    print('tags count', len(tags))
