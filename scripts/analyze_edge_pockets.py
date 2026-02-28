import json, zipfile

# load pockets
globals_pockets = json.load(open('pocket_geometry.json'))['pockets']

# load edge map
edge_map = json.load(open('artifacts/edge_to_rootpair_triple.json'))

with zipfile.ZipFile('TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip') as zf:
    pairs36 = json.loads(zf.read('TOE_E6pair_SRG_triangle_decomp_v01_20260227/e6_antipode_pairs_36.json').decode())['pairs']
pair_to_vertex={frozenset(p):i for i,p in enumerate(pairs36)}

count=0
no_count=0
for idx, triple in edge_map.items():
    verts=[pair_to_vertex[frozenset(rp)] for rp in triple]
    if any(set(verts).issubset(p) for p in globals_pockets):
        count+=1
    else:
        no_count+=1
print('pockets matched',count,'unmatched',no_count)

# list first unmatched
c=0
for idx, triple in edge_map.items():
    verts=[pair_to_vertex[frozenset(rp)] for rp in triple]
    if not any(set(verts).issubset(p) for p in globals_pockets):
        print('unmatched',idx,verts)
        c+=1
        if c>=10: break
