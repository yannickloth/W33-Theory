import json, pathlib
from math import gcd

ROOT=pathlib.Path()
bundle=ROOT/"TOE_duad_algebra_v06_20260227_bundle"/"TOE_duad_algebra_v05_20260227"

lines=json.loads((bundle/"W33_lines_40.json").read_text())["lines"]
pgpts=json.loads((bundle/"psp43_generators_on_points_40.json").read_text())["generators"]

# build edges
edges=set()
for L in lines:
    for i in range(len(L)):
        for j in range(i+1,len(L)):
            a,b=L[i],L[j]
            edges.add((a,b) if a<b else (b,a))
edges=sorted(edges)
edge_index={e:i for i,e in enumerate(edges)}

# point to edge

def pt_to_edge(pg):
    perm=[]
    for a,b in edges:
        a2=pg[a]; b2=pg[b]
        if a2<b2:
            perm.append(edge_index[(a2,b2)])
        else:
            perm.append(edge_index[(b2,a2)])
    return perm


duad_edge_gens=[pt_to_edge([int(x) for x in perm]) for perm in pgpts]

root_gens=json.loads((ROOT/"SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25"/"sp43_root_perms_fixed.json").read_text())
root_gens=[[int(x) for x in perm] for perm in root_gens]

# order

def order(perm):
    n=len(perm)
    vis=[False]*n
    o=1
    for i in range(n):
        if not vis[i]:
            j=i; cyc=0
            while not vis[j]:
                vis[j]=True; cyc+=1; j=perm[j]
            o=(o*cyc)//gcd(o,cyc)
    return o

print("duad orders", [order(p) for p in duad_edge_gens])
print("root orders", [order(p) for p in root_gens])
