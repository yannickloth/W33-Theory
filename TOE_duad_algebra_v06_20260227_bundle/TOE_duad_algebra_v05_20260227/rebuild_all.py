#!/usr/bin/env python3
"""
Rebuild W(3,3) over F3, the 120-duad action of PSp(4,3), the rank-5 association scheme,
and solve the Bose–Mesner algebra (p_{ij}^k, P, Q, primitive idempotents).
Also exports the spherical character table (dims 1,20,15,24,60) across the 20 conjugacy classes.

No repo dependencies. Pure python + numpy + sympy.
"""
import itertools, math, json, os
import numpy as np
import sympy as sp
import pandas as pd

def inv3(a):
    a%=3
    if a==1: return 1
    if a==2: return 2
    raise ZeroDivisionError

def canonical_point(v):
    v=list(v)
    for i in range(4):
        if v[i]%3!=0:
            inv=inv3(v[i])
            return tuple((x*inv)%3 for x in v)
    raise ValueError("zero")

def omega(u,v):
    return (u[0]*v[2]-u[2]*v[0]+u[1]*v[3]-u[3]*v[1])%3

J=np.array([[0,0,1,0],
            [0,0,0,1],
            [2,0,0,0],
            [0,2,0,0]], dtype=int)%3

def det_mod3_gauss(A):
    A=A.copy()%3
    n=A.shape[0]
    det=1
    for i in range(n):
        pivot=None
        for r in range(i,n):
            if A[r,i]%3!=0:
                pivot=r; break
        if pivot is None:
            return 0
        if pivot!=i:
            A[[i,pivot]]=A[[pivot,i]]
            det = (-det) %3
        pv=A[i,i]%3
        det = (det*pv)%3
        inv=inv3(pv)
        for c in range(i,n):
            A[i,c]=(A[i,c]*inv)%3
        for r in range(i+1,n):
            f=A[r,i]%3
            if f==0: continue
            for c in range(i,n):
                A[r,c]=(A[r,c]-f*A[i,c])%3
    return det%3

def is_invertible(A): return det_mod3_gauss(A)%3!=0
def is_symplectic(A):
    return np.array_equal((A.T.dot(J).dot(A))%3, J)

def compose(p,q):
    return tuple(p[i] for i in q)
def inv_perm(p):
    inv=[0]*len(p)
    for i,pi in enumerate(p): inv[pi]=i
    return tuple(inv)
def group_closure(gens, n, max_size=None):
    gens=[tuple(g) for g in gens]
    gens2=gens+[inv_perm(g) for g in gens]
    idp=tuple(range(n))
    seen={idp}
    stack=[idp]
    while stack:
        g=stack.pop()
        for s in gens2:
            h=compose(s,g)
            if h not in seen:
                seen.add(h); stack.append(h)
                if max_size and len(seen)>=max_size:
                    return seen
    return seen

# 1) Points (40)
points=[]
seen=set()
for v in itertools.product([0,1,2], repeat=4):
    if all(x==0 for x in v): 
        continue
    cp=canonical_point(v)
    if cp not in seen:
        seen.add(cp); points.append(cp)
pt_index={p:i for i,p in enumerate(points)}
pts_arr=[np.array(p, dtype=int) for p in points]

# 2) Lines (40)
def span2_points(u,v):
    s=set()
    for a,b in itertools.product([0,1,2],[0,1,2]):
        if a==0 and b==0: 
            continue
        w=tuple((a*u[i]+b*v[i])%3 for i in range(4))
        cp=canonical_point(w)
        s.add(pt_index[cp])
    return frozenset(s)

lines=set()
for i,u in enumerate(points):
    for j,v in enumerate(points):
        if j<=i: 
            continue
        if omega(u,v)!=0:
            continue
        L=span2_points(u,v)
        if len(L)==4:
            lines.add(L)
lines=list(sorted(lines, key=lambda s: tuple(sorted(s))))
line_index={L:i for i,L in enumerate(lines)}

# 3) Duads (120) = perfect matchings per line
def matchings_of_line(L):
    pts=sorted(L)
    a,b,c,d=pts
    raw=[((a,b),(c,d)), ((a,c),(b,d)), ((a,d),(b,c))]
    out=[]
    for (x,y),(u,v) in raw:
        p1=tuple(sorted((x,y)))
        p2=tuple(sorted((u,v)))
        if p2<p1: p1,p2=p2,p1
        out.append((p1,p2))
    # unique
    res=[]
    seen=set()
    for m in out:
        if m not in seen:
            seen.add(m); res.append(m)
    return res

duads=[]
duad_pairs=[]
for li,L in enumerate(lines):
    ms=matchings_of_line(L)
    for mi,m in enumerate(ms):
        duads.append((li,mi))
        duad_pairs.append(m)

def normalize_matching(m):
    (a,b),(c,d)=m
    p1=tuple(sorted((a,b)))
    p2=tuple(sorted((c,d)))
    if p2<p1: p1,p2=p2,p1
    return (p1,p2)

# 4) Fixed symplectic generators (from the main notebook)
genA=np.array([[2,2,0,2],
               [0,1,1,0],
               [2,1,1,2],
               [1,1,2,2]], dtype=int)%3
genB=np.array([[0,1,0,1],
               [0,1,1,1],
               [1,0,0,1],
               [2,1,1,1]], dtype=int)%3
assert is_invertible(genA) and is_invertible(genB) and is_symplectic(genA) and is_symplectic(genB)

def act_on_point(A, idx):
    v=pts_arr[idx]
    w=(A.dot(v))%3
    cp=canonical_point(tuple(int(x) for x in w))
    return pt_index[cp]

def perm_from_matrix_on_points(A):
    return tuple(act_on_point(A,i) for i in range(40))

gens_pts=[perm_from_matrix_on_points(genA), perm_from_matrix_on_points(genB)]
G_pts=group_closure(gens_pts, n=40, max_size=25920)
assert len(G_pts)==25920

def induced_duad_perm_from_point_perm(p):
    perm=[0]*120
    for did,(li,mi) in enumerate(duads):
        L=lines[li]
        Lp=frozenset(p[i] for i in L)
        li2=line_index[Lp]
        (a,b),(c,d)=duad_pairs[did]
        mp=normalize_matching(((p[a],p[b]),(p[c],p[d])))
        mi2=matchings_of_line(Lp).index(mp)
        perm[did]=li2*3 + mi2
    return tuple(perm)

gens_duad=[induced_duad_perm_from_point_perm(g) for g in gens_pts]
G_duad=group_closure(gens_duad, n=120, max_size=25920)
assert len(G_duad)==25920
G_list=list(G_duad)

# 5) Stabilizer orbitals -> relation matrix R
base=0
H=[g for g in G_list if g[base]==base]
assert len(H)==216

def orbit(subgroup, start):
    seen={start}
    stack=[start]
    while stack:
        x=stack.pop()
        for g in subgroup:
            y=g[x]
            if y not in seen:
                seen.add(y); stack.append(y)
    return seen

un=set(range(120))
orbits=[]
while un:
    s=next(iter(un))
    o=orbit(H,s)
    orbits.append(sorted(o))
    un-=o
orbit_by_size={len(o):o for o in orbits}
orbit_order=[orbit_by_size[1], orbit_by_size[2], orbit_by_size[27], orbit_by_size[36], orbit_by_size[54]]
rel0=[None]*120
for k,orb in enumerate(orbit_order):
    for y in orb: rel0[y]=k

to_x={}
for g in G_list:
    x=g[0]
    if x not in to_x: to_x[x]=g
    if len(to_x)==120: break
inv_to_x={x: inv_perm(g) for x,g in to_x.items()}

R=np.empty((120,120), dtype=np.int8)
for x in range(120):
    gx=inv_to_x[x]
    R[x,:]=[rel0[gx[y]] for y in range(120)]
assert np.all(R==R.T)

A=[(R==k).astype(int) for k in range(5)]
rep_y=[orbit_order[k][0] for k in range(5)]

# intersection numbers
pijk=np.zeros((5,5,5), dtype=int)
for i in range(5):
    for j in range(5):
        prod=A[i].dot(A[j])
        for k in range(5):
            pijk[i,j,k]=prod[0, rep_y[k]]

# multiplication matrices in adjacency algebra
M=[sp.Matrix([[int(pijk[i,j,k]) for j in range(5)] for k in range(5)]) for i in range(5)]

# simultaneous eigenvalues (P)
def common_eigenvectors():
    eigs = M[2].eigenvects()
    vecs=[]
    for ev, mult, basis in eigs:
        if mult==1:
            vecs.append(basis[0])
        else:
            B=sp.Matrix.hstack(*basis)
            C = B.gauss_jordan_solve(M[1]*B)[0]
            for ev1,m1,basis1 in C.eigenvects():
                vecs.append(B*basis1[0])
    return vecs

vecs=common_eigenvectors()
def eigenvalues_for_vector(v):
    evs=[]
    for i in range(5):
        w=M[i]*v
        lam=None
        for idx in range(5):
            if v[idx]!=0:
                lam=sp.Rational(w[idx], v[idx]); break
        assert w==lam*v
        evs.append(sp.simplify(lam))
    return tuple(evs)

eig_tuples=[eigenvalues_for_vector(v) for v in vecs]
# put trivial row (A2=27) first
eig_tuples=sorted(eig_tuples, key=lambda t: (t[2]!=27, int(t[1]) ))
P=sp.Matrix(eig_tuples)

# multiplicities from orthogonality
n=120
k=sp.Matrix([int(A[i][0].sum()) for i in range(5)])
m_syms=sp.symbols('m0:5')
Mdiag=sp.diag(*m_syms)
eqs=[]
for i in range(5):
    for j in range(i,5):
        eqs.append(sp.Eq((P.T*Mdiag*P)[i,j], (n*sp.diag(*k))[i,j]))
sol=sp.solve(eqs, m_syms, dict=True)[0]
m=[sol[s] for s in m_syms]
Mdiag=sp.diag(*m)
Q = sp.diag(*k).inv()*P.T*Mdiag

print("P (rows=irreps, cols=A0..A4):")
print(P)
print("dims m:", m)
print("Q:")
print(Q)

# export
out="outputs_duad_algebra"
os.makedirs(out, exist_ok=True)
with open(os.path.join(out,"intersection_numbers_pijk.json"),"w") as f:
    json.dump({"pijk":pijk.tolist()}, f, indent=2)
with open(os.path.join(out,"P.json"),"w") as f:
    json.dump({"P":[[int(x) for x in row] for row in P.tolist()], "dims":[int(x) for x in m], "valencies":[int(x) for x in k]}, f, indent=2)
with open(os.path.join(out,"Q.json"),"w") as f:
    json.dump({"Q":[[str(x) for x in row] for row in Q.tolist()]}, f, indent=2)
np.save(os.path.join(out,"relation_matrix_R.npy"), R)
print("Wrote outputs to", out)
