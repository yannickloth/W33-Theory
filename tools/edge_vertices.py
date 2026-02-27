import json
from pathlib import Path

data=json.loads((Path('artifacts')/'edge_to_e8_root.json').read_text())
verts=set()
for k in data.keys():
    a,b=eval(k)
    verts.add(a); verts.add(b)
print('vertices used count',len(verts))
print('min,max',min(verts),max(verts))
print('sorted first 20',sorted(verts)[:20])
