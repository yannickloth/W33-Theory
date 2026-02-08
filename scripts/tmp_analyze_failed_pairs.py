import json
from collections import Counter
j=json.load(open('checks/PART_CVII_failed_triangles_1770516589.json','r'))
pairs=Counter()
for f in j['failed_tris']:
    e=sorted(f['edges'])
    for i in range(3):
        for k in range(i+1,3):
            pairs[(e[i],e[k])]+=1
print('Top edge pairs (count):')
for p,c in pairs.most_common(20):
    print(p,c)
