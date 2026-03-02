import json
f=json.loads(open('artifacts/edge_to_e8_root.json').read())
print('has keys',len(f))
print('sample keys', list(f.keys())[:20])
print('(12,22)' in f, '(22,12)' in f)
for k in f:
    if '12' in k and '22' in k:
        print('match',k)
