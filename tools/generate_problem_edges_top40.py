#!/usr/bin/env python3
"""Write a missing-edges JSON containing the top N problematic oriented edges."""
from __future__ import annotations

import json
from pathlib import Path

IN = Path('analysis/minimal_commutator_cycles/problem_cycle_edge_tally.json')
OUT = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_problem_edges_top40.json')

j = json.loads(IN.read_text(encoding='utf-8'))
top = j.get('top_edges', [])[:40]
out = {'missing_edges': [{'edge': f"{e['edge_a']},{e['edge_b']}", 'count': e['count']} for e in top]}
OUT.write_text(json.dumps(out, indent=2), encoding='utf-8')
print('Wrote', OUT, 'with', len(out['missing_edges']))
