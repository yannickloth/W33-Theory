"""Attempt to compute exact rational 8x8 matrix mapping edge data → doubled roots.

We treat the mapping as A * Y = X where
- Y is matrix (8 x 240) built from edge endpoints (lifted GF3 coords concatenated),
- X is matrix (8 x 240) of 2*E8 root coordinates.

We solve for A in rationals by computing A = X * Y.T * (Y * Y.T)^{-1}.  If the
resulting entries are small rationals (denominator dividing, say, 3 or 6) then we
may have found a closed-form linear rule.
"""

import json
from itertools import product
import sympy as sp

# build W33 same as earlier

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

# E8 roots
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

# lift function

def lift(v): return [c if c<=1 else c-3 for c in v]

# build sympy matrices
# create rational matrices
Y = []  # 240 rows of 8 entries
X = []
for e,(vi,wi) in enumerate(edges):
    v=lift(vertices[vi]); w=lift(vertices[wi])
    # convert each entry to Rational
    Y.append([sp.Rational(x) for x in (v + w)])
    root=roots[map_arr[e]]
    X.append([sp.Rational(2*r) for r in root])

# now build sympy matrices with exact rationals
Ymat = sp.Matrix(Y).T  # 8x240
Xmat = sp.Matrix(X).T  # 8x240

# compute A = X Y^T (Y Y^T)^{-1}
Yyt = Ymat * Ymat.T
if Yyt.det() == 0:
    print('Y Y^T singular, rank', Yyt.rank())
else:
    A = Xmat * Ymat.T * Yyt.inv()
    print('computed rational matrix A:')
    sp.pprint(A)
    # simplify denominators
    denoms = [fr.q for fr in A]
    print('denominators:', sorted(set(denoms)))
    # check that A*Y ≈ X exactly
    residual = A*Ymat - Xmat
    print('max residual entry', max(abs(r) for r in residual))
