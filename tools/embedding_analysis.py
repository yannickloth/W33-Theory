"""Investigate how the current bijection interacts with standard E6 embeddings
inside E8.

We test several candidate descriptions of an E6 root subset in the E8 system and
count how many edges map into that subset.  This may help identify the canonical
E6 sublattice used by the equivariant mapping.
"""

import json
from itertools import product

# rebuild W33

def build_W33():
    def omega(v,w):
        return (v[0]*w[1]-v[1]*w[0]+v[2]*w[3]-v[3]*w[2])%3
    def normalize(v):
        for i,x in enumerate(v):
            if x!=0:
                inv=pow(x,-1,3)
                return tuple((inv*c)%3 for c in v)
        return v
    points=[p for p in product(range(3), repeat=4) if p!=(0,0,0,0)]
    vertices=list({normalize(p) for p in points})
    edges=[]
    for i,v in enumerate(vertices):
        for j,w in enumerate(vertices):
            if i<j and omega(v,w)==0:
                edges.append((i,j))
    return vertices, edges

vertices, edges = build_W33()

# build E8 roots
roots=[]
for i in range(8):
    for j in range(i+1,8):
        for si in [1,-1]:
            for sj in [1,-1]:
                r=[0]*8; r[i]=si; r[j]=sj; roots.append(tuple(r))
from itertools import product
for signs in product([0.5,-0.5], repeat=8):
    if sum(1 for s in signs if s<0)%2==0:
        roots.append(tuple(signs))

# load mapping
map_json=json.load(open('data/w33_e8_mapping.json'))
map_arr=[map_json[str(i)] for i in range(len(edges))]

# candidate E6 embeddings
candidates = {}
# 1: r6 + r7 = 0 (last two coords cancel)
candidates['r6+r7=0'] = [i for i,r in enumerate(roots) if abs(r[6]+r[7])<1e-6]
# 2: sum of last three coordinates = 0
candidates['sum_last3=0'] = [i for i,r in enumerate(roots) if abs(r[5]+r[6]+r[7])<1e-6]
# 3: r7=r8=r9? but we only have 8 coords; try r5=r6=r7
candidates['r5=r6=r7'] = [i for i,r in enumerate(roots) if abs(r[5]-r[6])<1e-6 and abs(r[6]-r[7])<1e-6]
# 4: something like first 6 coords sum 0? (yet ambiguous)
candidates['sum_first6=0'] = [i for i,r in enumerate(roots) if abs(sum(r[:6]))<1e-6]

for name, subset in candidates.items():
    print(f"candidate {name}: {len(subset)} roots")
    count=0
    for e_idx,r_idx in enumerate(map_arr):
        if r_idx in subset:
            count+=1
    print(f"  edges mapped into set: {count}")

# show some edges for first candidate
first = list(candidates.values())[0]
print('\nsample edges mapping into first candidate:')
for e_idx,r_idx in enumerate(map_arr):
    if r_idx in first:
        print(e_idx, edges[e_idx], roots[r_idx])
        if e_idx>10: break
