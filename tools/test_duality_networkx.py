import numpy as np
import networkx as nx
from itertools import combinations

# build W33 incidence as in compute_w33_duality
F=[0,1,2]
vecs=[]
for a in F:
    for b in F:
        for c in F:
            for d in F:
                if a==b==c==d==0: continue
                vecs.append(np.array([a,b,c,d],dtype=int))
classes={}
for v in vecs:
    best=None
    for s in (1,2):
        vv=(v*s)%3
        key=tuple(vv.tolist())
        if best is None or key<best: best=key
    classes[best]=np.array(best)
points=list(classes.values())
vec_to_idx={tuple(p.tolist()):i for i,p in enumerate(points)}

# lines
lines_set=set()
for i,j in combinations(range(len(points)),2):
    v=points[i]; w=points[j]
    mat=np.vstack([v,w])%3
    if np.linalg.matrix_rank(mat)<2: continue
    if (v[0]*w[2]-v[2]*w[0]+v[1]*w[3]-v[3]*w[1])%3!=0: continue
    subs=[]
    for a in F:
        for b in F:
            subs.append((a*v+b*w)%3)
    idxs=set()
    for u in subs:
        key=tuple(u.tolist())
        if key in vec_to_idx: idxs.add(vec_to_idx[key]); continue
        for s in (1,2):
            key2=tuple(((u*s)%3).tolist())
            if key2 in vec_to_idx: idxs.add(vec_to_idx[key2]); break
    if len(idxs)==4:
        lines_set.add(tuple(sorted(idxs)))
lines=[list(x) for x in sorted(lines_set)]
print(len(points),len(lines))

# build incidence dictionaries
inc_pt_to_lin = {i:set() for i in range(len(points))}
inc_lin_to_pt = {i:set() for i in range(len(lines))}
for li,L in enumerate(lines):
    for p in L:
        inc_pt_to_lin[p].add(li)
        inc_lin_to_pt[li].add(p)

# Rather than attempting the expensive graph isomorphism directly,
# compare the point-collinearity graph with the line-intersection graph.
# If they have different degree sequences, no duality can exist.

# build point adjacency
Gpt = nx.Graph()
Gln = nx.Graph()
for i in range(40):
    Gpt.add_node(i)
    Gln.add_node(i)
for p in range(40):
    for l in inc_pt_to_lin[p]:
        for q in inc_lin_to_pt[l]:
            if q != p:
                Gpt.add_edge(p, q)
for l1 in range(40):
    for l2 in range(l1+1, 40):
        if inc_lin_to_pt[l1] & inc_lin_to_pt[l2]:
            Gln.add_edge(l1, l2)

print('point graph degrees', sorted(d for _, d in Gpt.degree()))
print('line graph degrees ', sorted(d for _, d in Gln.degree()))

if sorted(d for _, d in Gpt.degree()) != sorted(d for _, d in Gln.degree()):
    print('graphs non-isomorphic; no point-line duality exists')
else:
    print('degree sequences match; further search might be necessary but expensive')
