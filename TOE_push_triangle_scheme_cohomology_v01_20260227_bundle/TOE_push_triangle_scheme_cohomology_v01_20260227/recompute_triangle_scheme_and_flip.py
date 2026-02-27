#!/usr/bin/env python3
import json, numpy as np, pandas as pd, collections
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
E6DIR = BASE / "TOE_E6pair_SRG_triangle_decomp_v01_20260227"
HOLDIR = BASE / "TOE_holonomy_Z2_flatZ3_v01_20260227"

A36 = np.load(E6DIR/"e6pair_srg_adj_36x36.npy")
w33map = json.load(open(E6DIR/"w33_line_to_e6pair_triangles.json"))
df = pd.read_csv(HOLDIR/"edgepair_transport_D6.csv")

edgepair_to_tri = {}
for rec in w33map:
    for eid, tri in zip(rec["edgepair_ids"], rec["triangle_blocks"]):
        edgepair_to_tri[eid] = tuple(tri)

def cross_edges(t1,t2):
    return int(sum(A36[a,b] for a in t1 for b in t2))

def relation(i,j):
    t1=set(edgepair_to_tri[i]); t2=set(edgepair_to_tri[j])
    inter=len(t1&t2)
    if inter==1: return 2
    assert inter==0
    c=cross_edges(edgepair_to_tri[i], edgepair_to_tri[j])
    if c==0: return 1
    if c==6: return 3
    if c==4: return 4
    raise RuntimeError(c)

R=np.zeros((120,120),dtype=np.int8)
for i in range(120):
    for j in range(i+1,120):
        r=relation(i,j)
        R[i,j]=R[j,i]=r

# valencies
vals={r:int((R==r).sum(axis=1)[0]) for r in [1,2,3,4]}
print("valencies", vals)

# build intersection numbers pijk
neighbors={r:[set(np.where(R[i]==r)[0]) for i in range(120)] for r in [1,2,3,4]}
rep_y={0:0}
for k in [1,2,3,4]:
    rep_y[k]=int(np.where(R[0]==k)[0][0])

def count_z(x,y,r,s):
    Z1={x} if r==0 else neighbors[r][x]
    Z2={y} if s==0 else neighbors[s][y]
    return len(Z1&Z2)

pijk=np.zeros((5,5,5),dtype=int)
for r in range(5):
    for s in range(5):
        for k in range(5):
            x=0; y=rep_y[k]
            pijk[r,s,k]=count_z(x,y,r,s)
print("A1^2 coeffs", pijk[1,1,:].tolist())
print("A1*A2 coeffs", pijk[1,2,:].tolist())

# Z2 gauge obstruction quick check: any 2-step loop?
pair_perm={}
flip={}
for g in sorted(df.gen.unique()):
    sub=df[df.gen==g].sort_values("edgepair_id")
    pair_perm[g]=sub.edgepair_image.astype(int).to_numpy()
    flip[g]=sub.flip_Z2.astype(int).to_numpy() & 1

found=0
for x in range(120):
    for i in range(10):
        y=int(pair_perm[i][x]); fi=int(flip[i][x])
        for j in range(10):
            if int(pair_perm[j][y])==x:
                hol=fi ^ int(flip[j][y])
                if hol==1:
                    print("nontriv len-2 loop at", x, "word", [i,j], "via", y)
                    found+=1
                    raise SystemExit(0)
print("no nontriv len-2 loops??", found)
