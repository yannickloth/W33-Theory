from collections import Counter, defaultdict
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import THE_EXACT_MAP as exact

G = [[1,1,1,0],[0,1,2,1]]
words = set()
for a in range(3):
    for b in range(3):
        w = tuple((a*G[0][i] + b*G[1][i]) % 3 for i in range(4))
        words.add(w)
mini_rows = [[0,4,8],[1,5,9],[2,6,10],[3,7,11]]

cnt = Counter()
by_word = defaultdict(list)
for c in exact.weight_6:
    s = tuple(sum(int(c[p]) for p in mini_rows[i]) % 3 for i in range(4))
    if s in words:
        cnt[s]+=1
        by_word[s].append(exact.support(c))

print('Total weight6 mapping to tetracode words:', sum(cnt.values()))
for w in sorted(cnt):
    print(w, cnt[w])
