#!/usr/bin/env python3
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'checks' / 'PART_CVII_e8_local_repair.json'
if not src.exists():
    raise SystemExit('Missing local repair file')
j = json.loads(src.read_text())
edge_to_root = j['edge_to_root']
seed_edges = [{'edge_index':int(k),'root_index':int(v)} for k,v in edge_to_root.items()]
out = {'seed_edges': seed_edges}
out_path = ROOT / 'checks' / 'PART_CVII_e8_embedding_coset_match_repaired_seed.json'
out_path.write_text(json.dumps(out, indent=2), encoding='utf-8')
print('Wrote', out_path, 'entries=', len(seed_edges))
