#!/usr/bin/env python3
import json
p='artifacts/edge_root_bijection_canonical.json'
D=json.load(open(p,'r',encoding='utf-8'))
print('entries:',len(D))
s=set()
for d in D:
    s.add(tuple(sorted((int(d['v_i']),int(d['v_j'])))))
print('unique unordered edges:',len(s))
# show a random sample
print('sample entries:', D[:3])
