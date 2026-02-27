from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from w33_homology import build_w33
n, verts, adj, edges = build_w33()
import csv
coord={}
with open('H27_CE2_FUSION_BRIDGE_BUNDLE_v01/pg_point_to_h27_vertex_coords.csv','r') as f:
    rdr=csv.DictReader(f)
    for r in rdr:
        coord[int(r['pg_id'])] = (int(r['x']),int(r['y']),int(r['t']))
count=0
for pid1,v1 in coord.items():
    for pid2,v2 in coord.items():
        if pid1<pid2 and v1[:2]==v2[:2]:
            if pid2 in adj[pid1]:
                count+=1
print('pairs same u in adj:',count)
