#!/usr/bin/env python3
import json
D=json.load(open('analysis/w33_bundle_temp/analysis/AGL23_lifts.json','r',encoding='utf-8'))
for ent in D['entries']:
    mat=ent['mat']
    det=(mat[0]*mat[3]-mat[1]*mat[2])%3
    if det==2:
        print('found mat',mat,'dx',ent.get('dx'),'dy',ent.get('dy'))
        print('perm_40 sample',ent.get('perm_40')[:10])
        break
else:
    print('none found')
