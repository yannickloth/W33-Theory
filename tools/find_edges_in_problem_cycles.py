#!/usr/bin/env python3
"""Find oriented edges that appear most often in cycles where some A2s are divisible but none match s_mod3==k."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

DEFAULT_IN = Path('analysis/minimal_commutator_cycles/e8_det1_combined_aggregated_summary.csv')
DEFAULT_OUT_JSON = Path('analysis/minimal_commutator_cycles/problem_cycle_edge_tally.json')
DEFAULT_OUT_CSV = Path('analysis/minimal_commutator_cycles/problem_cycle_edge_tally.csv')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='in_path', type=Path, default=DEFAULT_IN, help='Aggregated summary CSV path')
    ap.add_argument('--out-json', type=Path, default=DEFAULT_OUT_JSON, help='Output JSON path')
    ap.add_argument('--out-csv', type=Path, default=DEFAULT_OUT_CSV, help='Output CSV path')
    ap.add_argument('--top-n', type=int, default=40, help='Number of edges to write')
    args = ap.parse_args()

    in_path: Path = args.in_path
    out_json: Path = args.out_json
    out_csv: Path = args.out_csv

    rows = []
    # The aggregated CSV writes the cycle as unquoted comma-separated integers which
    # causes csv.DictReader to split the cycle across multiple columns. Read lines
    # and parse tokens manually: idx, [cycle...], k, any_divisible, any_match, divisible_count, match_count
    with in_path.open('r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]
        if not lines:
            print('No rows found in', in_path)
            raise SystemExit(1)
        # skip header
        for line in lines[1:]:
            tokens = [t for t in line.split(',')]
            if len(tokens) < 7:
                continue
            try:
                idx = int(tokens[0])
            except Exception:
                continue
            # last 4 tokens: any_divisible, any_match, divisible_count, match_count
            any_div = tokens[-4].strip() in ('1', 'True', 'true', 'TRUE', 'Yes', 'yes')
            any_match = tokens[-3].strip() in ('1', 'True', 'true', 'TRUE', 'Yes', 'yes')
            try:
                divisible_count = int(tokens[-2])
            except Exception:
                divisible_count = 0
            try:
                match_count = int(tokens[-1])
            except Exception:
                match_count = 0
            try:
                k = int(tokens[-5])
            except Exception:
                k = None
            cycle_tokens = tokens[1:-5]
            cycle = [int(x) for x in cycle_tokens if x.strip()]
            rows.append({'idx': idx, 'cycle': cycle, 'k': k, 'any_divisible': any_div, 'any_match': any_match, 'divisible_count': divisible_count, 'match_count': match_count})

    problem_cycles = []
    for r in rows:
        any_div = r.get('any_divisible', False)
        any_match = r.get('any_match', False)
        if any_div and not any_match:
            cyc = r.get('cycle', [])
            problem_cycles.append((int(r.get('idx', -1)), cyc))

    edge_counter = Counter()
    for idx, cyc in problem_cycles:
        n = len(cyc)
        for i in range(n):
            a = cyc[i]; b = cyc[(i+1)%n]
            edge_counter[(a,b)] += 1

    # produce top edges
    top = edge_counter.most_common(int(args.top_n))

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({'num_problem_cycles': len(problem_cycles), 'top_edges': [{'edge_a': a, 'edge_b': b, 'count': c} for (a,b), c in top]}, indent=2), encoding='utf-8')

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open('w', encoding='utf-8', newline='') as f:
        f.write('edge_a,edge_b,count\n')
        for (a,b), c in top:
            f.write(f"{a},{b},{c}\n")

    print('Found', len(problem_cycles), 'problem cycles; wrote top edges to', out_json, out_csv)


if __name__ == '__main__':
    main()
