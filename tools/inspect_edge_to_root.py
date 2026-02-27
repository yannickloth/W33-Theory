import json, ast
from pathlib import Path

edge_to_root=json.loads((Path('artifacts')/'edge_to_e8_root.json').read_text())
for idx,k in enumerate(edge_to_root.keys()):
    if idx<20:
        print(k, '->', edge_to_root[k])
    else:
        break
