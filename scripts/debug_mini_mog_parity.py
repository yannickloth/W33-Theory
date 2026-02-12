import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import THE_EXACT_MAP as exact

# Generator for tetracode words (same as test)
G = [[1,1,1,0],[0,1,2,1]]
words = set()
for a in range(3):
    for b in range(3):
        w = tuple((a*G[0][i] + b*G[1][i]) % 3 for i in range(4))
        words.add(w)

mini_rows = [[0,4,8],[1,5,9],[2,6,10],[3,7,11]]

def row_sums_mod3(codeword):
    sums = [sum(codeword[p] for p in mini_rows[r]) % 3 for r in range(4)]
    return tuple(sums)

bad = []
for c in exact.weight_6:
    rc = row_sums_mod3(c)
    if rc not in words:
        bad.append((exact.support(c), rc))

from collections import Counter
print('Total weight-6 codewords (hexads):', len(exact.weight_6))
print('Bad hexads count (by codeword sums):', len(bad))
# distribution of row_sums across all weight-6 codewords
dist = Counter(row_sums_mod3(c) for c in exact.weight_6)
print('\nRow-sums distribution (sums per group mod3 -> frequency):')
for rc, cnt in sorted(dist.items()):
    ok = 'OK' if rc in words else 'BAD'
    print(f'  {rc}: {cnt}   {ok}')

print('\nFirst 20 failing hexads (if any):')
for i, (h, rc) in enumerate(bad[:20]):
    print(i+1, sorted(h), rc)
