#!/usr/bin/env python3
import json
MOD=3
def norm(coords):
    for a in coords:
        if a%MOD!=0:
            inv=1 if a%MOD==1 else 2
            return tuple((inv*x)%MOD for x in coords)
    raise ValueError("zero")
def matT(A): return list(map(list, zip(*A)))
def matmul(A,B):
    m=len(A); n=len(B[0]); k=len(B)
    return [[sum(A[i][t]*B[t][j] for t in range(k))%MOD for j in range(n)] for i in range(m)]
def matvec(A,v):
    return [sum(A[i][j]*v[j] for j in range(len(v)))%MOD for i in range(len(A))]
def mateq(A,B):
    return all(A[i][j]%MOD==B[i][j]%MOD for i in range(len(A)) for j in range(len(A[0])))

with open("Klein_map_line_to_Qpoint.json","r") as f:
    km=json.load(f)
Q_points=[tuple(v) for v in km["Q_points40"]]
coord_to_id={Q_points[i]:i for i in range(40)}

with open("SO53_induced_matrices_5x5.json","r") as f:
    data=json.load(f)
S=data["quadratic_form_matrix_S"]
ind=data["induced_5x5"]

def preserves(M):
    MT=matT(M)
    lhs=matmul(matmul(MT,S),M)
    return mateq(lhs,S)

def perm_from_M(M):
    perm=[]
    for c in Q_points:
        img=norm(tuple(matvec(M,list(c))))
        perm.append(coord_to_id[img])
    return tuple(perm)

for name,M in ind.items():
    assert preserves(M), f"{name} does not preserve S"
print("All induced 5x5 matrices preserve the quadratic form S.")

gens=[perm_from_M(ind[k]) for k in ["T_e1","T_e2","T_e3","T_e4","A","B"]]
ID=tuple(range(40))
def compose(q,p): return tuple(q[p[i]] for i in range(40))
group={ID}
front=[ID]
while front and len(group)<25920:
    cur=front.pop()
    for g in gens:
        nxt=compose(g,cur)
        if nxt not in group:
            group.add(nxt); front.append(nxt)
assert len(group)==25920, f"generated size {len(group)} != 25920"
print("Generated permutation group on Q(4,3) points has size 25920 (PSp(4,3)).")
