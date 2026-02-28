import json
pg=json.load(open('pocket_geometry.json'))
pockets=pg['pockets']
so=pg['silent_of_pocket']
for i in [0,1,2,3,18,19]:
    key=str(pockets[i])
    print('pocket',i,'silent',so.get(key))
