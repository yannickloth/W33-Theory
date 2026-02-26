from scripts.ce2_global_cocycle import _simple_family_sign_map
from scripts.ce2_kernel_action import _invariants_from_triple

sign_map = _simple_family_sign_map()
seed_patterns = {}
for key, sgn in sign_map.items():
    t, d, w, s, z = _invariants_from_triple(key)
    if d == (1,0):
        tag=(t,w,z)
        pat=list(seed_patterns.get(tag,(None,None,None)))
        pat[w]=int(sgn)
        seed_patterns[tag]=tuple(pat)

print('count tags',len(seed_patterns))
for tag, pat in seed_patterns.items():
    print(tag, pat)

print('unique patterns', set(seed_patterns.values()))
print('len unique', len(set(seed_patterns.values())))
