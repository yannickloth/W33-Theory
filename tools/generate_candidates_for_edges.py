#!/usr/bin/env python3
"""Generate candidate lists for a given explicit list of edges using parser heuristics."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.suggest_missing_edge_candidates import build_inverse_vec_map, build_all_mapped_vectors, propose_candidates_for_edge
from tools.w33_rootword_uv_parser import W33RootwordParser

IN = Path('analysis/minimal_commutator_cycles/problem_cycle_edge_tally.json')
OUT_JSON = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_problem_edges_top20_candidates.json')
OUT_CSV = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_problem_edges_top20_candidates.csv')

p = W33RootwordParser()
edge_candidates_map = build_inverse_vec_map(p)
existing_edge_to_root = getattr(p, 'edge_to_root', {})
all_mapped = build_all_mapped_vectors(p)

j = json.loads(IN.read_text(encoding='utf-8'))
top = j.get('top_edges', [])[:20]
edges = [(e['edge_a'], e['edge_b'], e['count']) for e in top]

report = {'generated_from': str(IN), 'edges': []}

for a,b,count in edges:
    cands = propose_candidates_for_edge(a, b, p, edge_candidates_map, existing_edge_to_root, all_mapped, candidates_per_edge=20)
    report['edges'].append({'edge': f'{a},{b}', 'count': count, 'num_direct_candidates': len(edge_candidates_map.get((a,b), [])), 'candidates': cands})

OUT_JSON.write_text(json.dumps(report, indent=2), encoding='utf-8')

with OUT_CSV.open('w', encoding='utf-8', newline='') as f:
    f.write('edge_a,edge_b,count,num_direct_candidates,top_candidate_vector,top_candidate_score,top_candidate_confidence\n')
    for ent in report['edges']:
        a,b = ent['edge'].split(',')
        top = ent['candidates'][0] if ent['candidates'] else None
        top_vec = json.dumps(top['vector']) if top else ''
        top_score = top['score'] if top else ''
        top_conf = top['confidence'] if top else ''
        f.write(f"{a},{b},{ent['count']},{ent['num_direct_candidates']},{top_vec},{top_score},{top_conf}\n")

print('Wrote', OUT_JSON, OUT_CSV)
