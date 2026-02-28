import json
from itertools import product

def compose(p,q): return tuple(p[i] for i in q)
def perm_order(p):
    idp=tuple(range(len(p)))
    cur=p; k=1
    while cur!=idp:
        cur=compose(p,cur); k+=1
    return k

axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_r=[tuple(axis_adj[f'r{i}']) for i in range(4)]
trans=json.load(open('transported_r_generators.json'))
trans_r=[tuple(trans[f'r{i}']) for i in range(4)]

print("axis adjacent orders:")
for i,j in [(0,1),(1,2),(2,3)]:
    print(i,j,perm_order(compose(axis_r[i],axis_r[j])))
print("tomotope->axis adjacent orders (transported):")
for i,j in [(0,1),(1,2),(2,3)]:
    print(i,j,perm_order(compose(trans_r[i],trans_r[j])))

# true tomotope original orders in bundle
import zipfile
with zipfile.ZipFile('TOE_tomotope_true_flag_model_v02_20260228_bundle.zip') as zf:
    tomo_adj=json.loads(zf.read('tomotope_r_generators_192.json'))
    tomo_r=[tuple(tomo_adj[f'r{i}']) for i in range(4)]
print("true tomotope orders:")
for i,j in [(0,1),(1,2),(2,3)]:
    print(i,j,perm_order(compose(tomo_r[i],tomo_r[j])))
