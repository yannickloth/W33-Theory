#!/usr/bin/env python3
import zipfile, csv, io, json

bundle='TOE_tomotope_triality_weld_v01_20260228_bundle.zip'
with zipfile.ZipFile(bundle) as zf:
    reader=csv.DictReader(io.StringIO(zf.read('TOE_tomotope_triality_weld_v01_20260228/K_orbit_pockets_54.csv').decode()))
    pockets54=[int(r['p']) for r in reader]
geo=json.load(open('pocket_geometry.json'))
silent_map={tuple(int(x) for x in k.strip('[]').split(',')):v for k,v in geo['silent_of_pocket'].items()}

pockets=geo['pockets']
vals=[]
for p in pockets54:
    tup=tuple(pockets[p])
    vals.append(silent_map.get(tup))
print('n pockets',len(vals),'unique silent',set(vals))
print('counts', {v:vals.count(v) for v in set(vals)})
