#!/usr/bin/env python3
"""Solve the Bose–Mesner algebra from duad_intersection_numbers.json."""
import json, math
import numpy as np
import pandas as pd
import sympy as sp
from pathlib import Path

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'duad_intersection_numbers.json').read_text())

k=np.array(data['relation_sizes'],dtype=int)
tensor=np.array(data['p_ijk'],dtype=int)  # i,j,k
n=int(sum(k))

Ls=[sp.Matrix(tensor[i].T) for i in range(5)]
M=3*Ls[1] + 5*Ls[2] + 7*Ls[3] + 11*Ls[4]

eigs=M.eigenvects()
vecs=[]
for ev,mult,vs in eigs:
    v=vs[0]
    lcm=sp.ilcm(*[t.q for t in v])
    v=sp.Matrix([int(x*lcm) for x in v])
    vecs.append(v)

def scalar_eig(L,v):
    w=L*v
    for a,b in zip(list(v),list(w)):
        if a!=0:
            return sp.Rational(b,a)
    raise ValueError('zero vector')

P=[]
for v in vecs:
    row=[scalar_eig(Ls[i],v) for i in range(5)]
    P.append(row)

krow=[sp.Integer(x) for x in k.tolist()]
triv_idx=[i for i,r in enumerate(P) if r==krow][0]
order=[triv_idx]+[i for i in range(5) if i!=triv_idx]
Pmat=sp.Matrix([P[i] for i in order])

m_syms=sp.symbols('m0:5')
eqs=[]
for i in range(5):
    for j in range(5):
        lhs=sum(m_syms[r]*Pmat[r,i]*Pmat[r,j] for r in range(5))
        rhs=n*k[i] if i==j else 0
        eqs.append(sp.Eq(lhs,rhs))
sol=sp.solve(eqs, m_syms, dict=True)[0]
m=[int(sol[m_syms[r]]) for r in range(5)]

Qmat = sp.Integer(n) * Pmat.inv()

P_df=pd.DataFrame(np.array(Pmat.tolist(),dtype=object), columns=[f"A{i}" for i in range(5)])
P_df.insert(0,"E_r",[f"E{r}" for r in range(5)])
P_df["mult"]=m
P_df.to_csv(HERE/'P_eigenmatrix.csv', index=False)

Q_df=pd.DataFrame(np.array(Qmat.tolist(),dtype=object), columns=[f"E{r}" for r in range(5)])
Q_df.insert(0,"A_i",[f"A{i}" for i in range(5)])
Q_df.to_csv(HERE/'Q_dual_eigenmatrix.csv', index=False)

print("n =", n)
print("valencies =", k.tolist())
print("multiplicities =", m)
