#!/usr/bin/env python3
import json, random, math
import numpy as np
from collections import defaultdict

# load generators and pi
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
r=[tuple(axis_adj[f'r{i}']) for i in range(4)]
pi=tuple(json.load(open('pi_mapping.json')))

# generate group elements (permutations of 192)
G=[tuple(range(192))]
changed=True
while changed:
    changed=False
    for g in list(G):
        for h in r:
            comp=tuple(g[h[i]] for i in range(192))
            if comp not in G:
                G.append(comp); changed=True
print('group size',len(G))

# compute inverses for permutations
inv = {}
def invert(p):
    ip=[0]*len(p)
    for i,v in enumerate(p): ip[v]=i
    return tuple(ip)
for g in G:
    inv[g]=invert(g)

# compute conjugacy classes correctly
cls=[]
rep_to_cls={}
for g in G:
    if g in rep_to_cls: continue
    this=[g]
    for h in G:
        h_inv=inv[h]
        # conjugate = h * g * h^{-1}
        cg = tuple(h[g[h_inv[i]]] for i in range(192))
        if cg not in this:
            this.append(cg)
    for x in this: rep_to_cls[x]=len(cls)
    cls.append(this)
print('classes',len(cls))

# permutation matrices will be used for eigen decomposition

# create random linear combination of elements (not classes) for genericity
weights_elem=[random.random() for _ in G]
M=np.zeros((192,192),dtype=float)
for g,w in zip(G,weights_elem):
    for i in range(192):
        M[i,g[i]] += w

# symmetrize
M=(M+M.T)/2

# symmetrize
M=(M+M.T)/2
# eigen decompose
vals,vecs=np.linalg.eigh(M)
# cluster eigenvalues using tolerance
clusters=defaultdict(list)
tol=1e-6
for idx,val in enumerate(vals):
    found=False
    for key in list(clusters.keys()):
        if abs(val-key) < tol:
            clusters[key].append(idx)
            found=True
            break
    if not found:
        clusters[val].append(idx)
print('eigencluster dims',[(key,len(idxs)) for key,idxs in clusters.items()])

# map each eigenvector index to cluster label
eig_to_cluster={idx:key for key,idxs in clusters.items() for idx in idxs}

# compute effect of pi on eigenvectors: represent Pi as permutation matrix
Pi=np.zeros((192,192))
for i in range(192): Pi[pi[i],i]=1

# for each cluster compute how Pi permutes the subspace
cluster_map=defaultdict(lambda: defaultdict(int))
for idx in range(192):
    v=vecs[:,idx]
    w=Pi.dot(v)
    # express w in eigenbasis: coordinates = vecs.T * w
    coeffs=vecs.T.dot(w)
    j=np.argmax(np.abs(coeffs))
    cluster_map[eig_to_cluster[idx]][eig_to_cluster[j]] += 1

print('cluster_map (counts of basis mapping)')
for c,mp in cluster_map.items():
    print(c,dict(mp))

# analyze connected components of cluster_map
comp=[]
visited=set()
for c in cluster_map:
    if c in visited: continue
    stack=[c]; comp_nodes=set()
    while stack:
        x=stack.pop()
        if x in comp_nodes: continue
        comp_nodes.add(x)
        visited.add(x)
        for y in cluster_map[x]:
            if y not in comp_nodes: stack.append(y)
        # also look for incoming edges
        for u,vmap in cluster_map.items():
            if x in vmap and u not in comp_nodes:
                stack.append(u)
    comp.append(comp_nodes)
print('components of cluster permutation:')
for comp_nodes in comp:
    dims=[len(clusters[c]) for c in comp_nodes]
    print(comp_nodes,'dims',dims)

# also list cluster dims sorted
for c in sorted(clusters.keys(), key=lambda k: len(clusters[k])):
    print('cluster',c,'dim',len(clusters[c]))

# identify clusters of dimension 8
print('clusters with dim 8')
for c in clusters:
    if len(clusters[c])==8: print(c)
