#!/usr/bin/env python3
import json, csv
from collections import defaultdict, Counter

# load H elements (same file as in earlier notebook)
with open('axis_line_stabilizer_192.json') as f:
    H_perms = json.load(f)['elements']

# load flag orbit partition under symmetry96
orbit96 = {}
with open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_orbits_under_symmetry96.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        orbit96[int(row['flag_index'])] = int(row['orbit96'])

# build regular perms for H
H_index = { (tuple(g['perm']),tuple(g['signs'])):i for i,g in enumerate(H_perms)}
H_regular = []
for g in H_perms:
    img=[]
    for h in H_perms:
        perm1,sign1=g['perm'],g['signs']
        perm2,sign2=h['perm'],h['signs']
        newperm=[None]*7; newsign=[None]*7
        for i in range(7):
            j=perm2[i]-1
            newperm[i]=perm1[j]
            newsign[i]=sign1[j]*sign2[i]
        img.append(H_index[(tuple(newperm),tuple(newsign))])
    H_regular.append(tuple(img))

# filter subgroup of order 96 preserving orbit partition
sym96 = []
for idx,perm in enumerate(H_regular):
    ok=True
    for f,orb in orbit96.items():
        if orbit96[perm[f]]!=orb:
            ok=False; break
    if ok:
        sym96.append(idx)

print('sym96 count', len(sym96))

# load flag adjacency perms
flag_adj = json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
r0=flag_adj['r0']; r1=flag_adj['r1']; r2=flag_adj['r2']; r3=flag_adj['r3']

# compute edge orbits under r0,r2,r3
edges=[]
visited=set()
def orbit_under(f, gens):
    O=set([f])
    stack=[f]
    while stack:
        u=stack.pop()
        for g in gens:
            v=g[u]
            if v not in O:
                O.add(v); stack.append(v)
    return O

for f in range(192):
    if f in visited: continue
    orb=orbit_under(f, [r0,r2,r3])
    for u in orb: visited.add(u)
    edges.append(sorted(orb))

print('number of edges',len(edges),'sizes',Counter(len(o) for o in edges))

# compute induced permutation on edges by r1 (should permute 12 items)
edge_perm_r1=[]
for ei,orb in enumerate(edges):
    image = r1[orb[0]]
    for ej,o2 in enumerate(edges):
        if image in o2:
            edge_perm_r1.append(ej)
            break
print('r1 induced on edges', edge_perm_r1)

# load published tomotope perms p0..p3
p = json.load(open('data/maniplex_tables/tomotope_permutation_summary.json'))['parsed_generators']
p_maps={}
for name,mp in p.items():
    perm=[mp.get(str(i+1),i+1)-1 for i in range(12)]
    p_maps[name]=perm
print('tomotope p0..p3',p_maps)

# maybe r1 corresponds to one of the p's up to relabeling

