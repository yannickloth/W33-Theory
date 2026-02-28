#!/usr/bin/env python3
import json, csv, os

bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks=json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
# load block labels
labels={}
with open(os.path.join(bundle,'blocks48_labeled_by_tomotope_edge_face.csv')) as f:
    reader=csv.DictReader(f)
    for row in reader:
        bi=int(row['block']); labels[bi]=(int(row['tE']),int(row['tF']))
# load pocket mapping
block_pockets=json.load(open('block_to_pockets.json'))
# load split stats from holonomy summary
summary=json.load(open('block_holonomy_summary.json'))
split_stats=summary['split_stats']
# load pocket silent info if present
pocket_geom=json.load(open('pocket_geometry.json'))
po_silent=pocket_geom.get('silent_of_pocket',{})

# assemble rows
rows=[]
for bi in range(48):
    tE,tF = labels.get(bi,(None,None))
    pockets = block_pockets.get(str(bi),[])
    silent = [po_silent.get(str(p),'') for p in pockets]
    r1 = split_stats['r1'].get(str(bi),{})
    r2 = split_stats['r2'].get(str(bi),{})
    rows.append({
        'block':bi,'tE':tE,'tF':tF,
        'pockets':pockets,'silent':silent,
        'r1_split':r1,'r2_split':r2
    })
# write csv
with open('block_cocycle_rule.csv','w',newline='') as f:
    fieldnames=['block','tE','tF','pockets','silent','r1_split','r2_split']
    writer=csv.DictWriter(f,fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()})
print('wrote block_cocycle_rule.csv')
