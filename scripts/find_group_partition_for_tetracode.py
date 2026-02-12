"""
Search for a partition of the 12 Golay positions into 4 groups of 3
(sizes [3,3,3,3]) so that for every hexad H the counts per group
(mod 3) form a tetracode word.

This searches all (12 choose 3)*(9 choose 3)*(6 choose 3) = 369,600
partitions (feasible). If a partition is found, print it.
"""
from itertools import combinations
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import THE_EXACT_MAP as exact

# tetracode words
G = [[1,1,1,0],[0,1,2,1]]
words = set()
for a in range(3):
    for b in range(3):
        w = tuple((a*G[0][i] + b*G[1][i]) % 3 for i in range(4))
        words.add(w)

positions = list(range(12))
hexads = exact.hexads

count_checked = 0
for g0 in combinations(positions, 3):
    rem1 = [p for p in positions if p not in g0]
    for g1 in combinations(rem1, 3):
        rem2 = [p for p in rem1 if p not in g1]
        for g2 in combinations(rem2, 3):
            g3 = tuple(p for p in rem2 if p not in g2)
            groups = [set(g0), set(g1), set(g2), set(g3)]
            ok = True
            for H in hexads:
                counts = tuple(sum(1 for p in groups[i] if p in H) % 3 for i in range(4))
                if counts not in words:
                    ok = False
                    break
            count_checked += 1
            if ok:
                print("Found groups:")
                for i, g in enumerate(groups):
                    print(f" group{i}: {sorted(g)}")
                raise SystemExit(0)

print("No partition found after checking", count_checked, "candidates")
