#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.suggest_missing_edge_candidates import generate_report

report = generate_report(Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_problem_edges_top20.json'), top_n=40, candidates_per_edge=20, out_dir=Path('analysis/minimal_commutator_cycles'))
print('report edges:', len(report['edges']))
for ent in report['edges'][:10]:
    print(ent['edge'], 'direct=', ent['num_direct_candidates'], 'top=', ent['candidates'][0]['vector'] if ent['candidates'] else None)
