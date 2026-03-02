import json
from collections import defaultdict
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
    norm=set(normalize(p) for p in points)
    vertices=list(norm)
    edges=[]; adj=defaultdict(list)
    for i,v in enumerate(vertices):
        for j,w in enumerate(vertices):
            if i<j and omega(v,w)==0:
                edges.append((i,j)); adj[i].append(j); adj[j].append(i)
    return vertices,edges,adj

vertices,edges,adj=build_W33()
mapping=json.load(open('data/w33_e8_mapping.json'))
map_arr=[mapping[str(i)] for i in range(len(edges))]

# rebuild E8 roots
roots=[]
for i in range(8):
    for j in range(i+1,8):
        for si in [1,-1]:
            for sj in [1,-1]:
                r=[0]*8; r[i]=si; r[j]=sj; roots.append(tuple(r))
for signs in product([0.5,-0.5], repeat=8):
    if sum(1 for s in signs if s<0)%2==0:
        roots.append(tuple(signs))

# lift function

def lift(v): return tuple(c if c<=1 else c-3 for c in v)

# calculate diff norms

diff_norms=[sum((lift(vertices[e[0]])[k]-lift(vertices[e[1]])[k])**2 for k in range(4)) for e in edges]

zero_edges=[e for e,d in enumerate(diff_norms) if abs(d-2)<1e-6]
print('zero diff edges', zero_edges)

import numpy as np

data_X = []
data_Y = []
for e in zero_edges:
    vi,wi=edges[e]; v=vertices[vi]; w=vertices[wi]
    v_l=lift(v); w_l=lift(w)
    root=roots[map_arr[e]]
    doubled=[int(2*x) for x in root]
    print('edge',e,'v',v,'w',w)
    print(' v_l',v_l,'w_l',w_l)
    print(' root*2',doubled)
    # show some combos
    inter1=[v_l[i] for i in range(4)] + [w_l[i] for i in range(4)]
    inter2=[v_l[i] for i in range(4)] + [-w_l[i] for i in range(4)]
    print(' inter1',inter1,'inter2',inter2)
    # build matrices for linear solving
    data_X.append(doubled)
    data_Y.append(inter1)  # assume mapping uses inter1 basis initially
    print()

# attempt to solve A such that A * Y = X
Y = np.array(data_Y).T  # 8xN
X = np.array(data_X).T  # 8xN
# use least squares
A, residuals, rank, s = np.linalg.lstsq(Y.T, X.T, rcond=None)
# A is Nx8? Actually we solved for Y.T * B = X.T giving B shape (N,8)
# Let's solve properly:
A = X @ np.linalg.pinv(Y)
print('candidate matrix A:')
print(np.round(A,3))
print('check A*Y approx X? max diff', np.max(np.abs(A@Y - X)))
