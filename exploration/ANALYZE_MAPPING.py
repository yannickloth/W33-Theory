import json
import numpy as np
from collections import defaultdict
import statistics

# rebuild necessary components (copy from hunt script)
def build_W33():
    from itertools import product
    def omega(v, w):
        return (v[0]*w[1]-v[1]*w[0]+v[2]*w[3]-v[3]*w[2]) % 3
    def normalize(v):
        for i,x in enumerate(v):
            if x!=0:
                inv=pow(x,-1,3)
                return tuple((inv*c)%3 for c in v)
        return v
    points=[p for p in product(range(3), repeat=4) if p!=(0,0,0,0)]
    normalized=set()
    for p in points: normalized.add(normalize(p))
    vertices=list(normalized)
    edges=[]
    adj=defaultdict(list)
    for i,v in enumerate(vertices):
        for j,w in enumerate(vertices):
            if i<j and omega(v,w)==0:
                edges.append((i,j))
                adj[i].append(j); adj[j].append(i)
    return vertices,edges,adj

vertices,edges,adj=build_W33()
# load mapping
table=json.load(open('data/w33_e8_mapping.json'))
map_arr=[table[str(i)] for i in range(len(edges))]

# build E8 roots

def build_E8_roots():
    roots=[]
    for i in range(8):
        for j in range(i+1,8):
            for si in [1,-1]:
                for sj in [1,-1]:
                    r=[0]*8
                    r[i]=si; r[j]=sj
                    roots.append(tuple(r))
    from itertools import product
    for signs in product([0.5,-0.5], repeat=8):
        if sum(1 for s in signs if s<0)%2==0:
            roots.append(tuple(signs))
    return roots

E8_roots=build_E8_roots()

int_type=[i for i,r in enumerate(E8_roots) if all(float(c).is_integer() for c in r)]
half_type=[i for i,r in enumerate(E8_roots) if not all(float(c).is_integer() for c in r)]

counts_int=sum(1 for e,r in enumerate(map_arr) if r in int_type)
counts_half=len(edges)-counts_int
print('integer-root mappings:',counts_int,'half-root mappings:',counts_half)

# diff norms

def lift(v): return tuple(c if c<=1 else c-3 for c in v)

diff_norms=[sum((lift(vertices[e[0]])[k]-lift(vertices[e[1]])[k])**2 for k in range(4)) for e in edges]

int_norms=[diff_norms[e] for e,r in enumerate(map_arr) if r in int_type]
half_norms=[diff_norms[e] for e,r in enumerate(map_arr) if r in half_type]
print('diff_norms integer roots: mean',statistics.mean(int_norms), 'half',statistics.mean(half_norms))
print('diff_norm counts by value', {val:diff_norms.count(val) for val in sorted(set(diff_norms))})

# check zero-distance matches earlier correspond to diff=2 maybe? compute edges with diff_norm==2
zero_edge_indices=[i for i,d in enumerate(diff_norms) if d==2]
print('edges with diff norm 2:', len(zero_edge_indices))
print('zero-edge norms vs mapping root types:')
for i in zero_edge_indices:
    r=map_arr[i]
    print(i, 'root type', 'int' if r in int_type else 'half')
