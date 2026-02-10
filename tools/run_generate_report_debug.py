#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.suggest_missing_edge_candidates import generate_report

report = generate_report(Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_problem_edges_top20.json'), top_n=40, candidates_per_edge=20, out_dir=Path('analysis/minimal_commutator_cycles'))
print('Generated report edges:', len(report.get('edges', [])))
for ent in report.get('edges', [])[:10]:
    print(ent['edge'], 'direct=', ent['num_direct_candidates'], 'num_cands=', len(ent['candidates']))
