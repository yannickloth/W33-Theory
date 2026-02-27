from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from w33_homology import build_w33

n, verts, adj, edges = build_w33()
inf = range(13)
graph = {i: set(adj[i]).intersection(inf) for i in inf}
# remove 0 and compute components among 1..12
seen = set()
comps = []
for i in range(1, 13):
    if i in seen:
        continue
    comp = set()
    stack = [i]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        comp.add(u)
        for v in graph[u]:
            if v != 0 and v not in seen:
                stack.append(v)
    comps.append(sorted(comp))
print('components without 0', comps)
