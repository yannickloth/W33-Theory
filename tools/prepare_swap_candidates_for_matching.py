#!/usr/bin/env python3
"""Prepare swap candidates JSON for greedy matching and write a summary CSV.

Reads:
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates.json
Writes:
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates_for_matching.json
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates_summary.csv
"""
from __future__ import annotations

import argparse
import json
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_IN = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates.json')
DEFAULT_OUT_JSON = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates_for_matching.json')
DEFAULT_OUT_SUM = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates_summary.csv')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='in_path', type=Path, default=DEFAULT_IN, help='Swap candidates JSON to convert')
    ap.add_argument('--out-json', type=Path, default=DEFAULT_OUT_JSON, help='Output candidates JSON (matching format)')
    ap.add_argument('--out-sum', type=Path, default=DEFAULT_OUT_SUM, help='Output summary CSV')
    ap.add_argument('--score-mode', choices=['fixed', 'net'], default='fixed', help='Which score to emit (default: fixed)')
    args = ap.parse_args()

    j = json.loads(args.in_path.read_text(encoding='utf-8'))
    out = {'edges': []}
    rows = []
    for ent in j.get('out_rows', []):
        edge = ent.get('edge')
        count = ent.get('count', 0)
        cands = ent.get('candidates', [])
        new_cands = []
        for c in cands:
            vec = c.get('vector')
            fixed = int(c.get('fixed_matches', 0))
            net = int(c.get('net_matches', fixed))
            score = fixed if args.score_mode == 'fixed' else net
            new_cands.append({'vector': vec, 'score': score, 'tag': 'swap-canon', 'source': 'swap'})
        out['edges'].append({'edge': edge, 'count': count, 'candidates': new_cands})
        top = cands[0] if cands else None
        if top is None:
            rows.append({'edge': edge, 'count': count, 'top_vector': '', 'top_fixed_matches': 0, 'top_net_matches': 0, 'num_candidates': 0})
        else:
            rows.append({
                'edge': edge,
                'count': count,
                'top_vector': json.dumps(top['vector']),
                'top_fixed_matches': int(top.get('fixed_matches', 0)),
                'top_net_matches': int(top.get('net_matches', top.get('fixed_matches', 0))),
                'num_candidates': len(cands),
            })

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')
    with args.out_sum.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['edge', 'count', 'top_vector', 'top_fixed_matches', 'top_net_matches', 'num_candidates', 'score_mode'])
        for r in rows:
            w.writerow([r['edge'], r['count'], r['top_vector'], r['top_fixed_matches'], r['top_net_matches'], r['num_candidates'], args.score_mode])

    print('Wrote', args.out_json, 'and summary CSV')


if __name__ == '__main__':
    main()
