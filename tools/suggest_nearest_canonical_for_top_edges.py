#!/usr/bin/env python3
"""Suggest candidate canonical-root replacements for high-leverage edges.

For each top problem edge (from problem_cycle_edge_tally.json), find the nearest
canonical root vectors (by L2 distance) that are not identical to the current
assignment and compute how many cycles would become fully covered (fixed) if
we applied the candidate. Emit a JSON/CSV report and an apply CSV for candidates
that fix >= threshold cycles.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def load_combined_map(path: Path) -> Dict[Tuple[int, int], Tuple[int, ...]]:
    data = json.loads(path.read_text(encoding='utf-8'))
    m: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    for k, coords in data.items():
        if isinstance(k, str) and k.startswith('('):
            s = k.strip()[1:-1]
            a_s, b_s = s.split(',')
            a = int(a_s.strip()); b = int(b_s.strip())
            m[(a, b)] = tuple(int(x) for x in coords)
    return m


def load_cycles(path: Path) -> List[List[int]]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data, dict):
        cycles = data.get('canonical_cycles') or data.get('cycles') or []
    else:
        cycles = data
    out = []
    for c in cycles:
        if isinstance(c, dict) and 'cycle' in c:
            out.append([int(x) for x in c['cycle']])
        elif isinstance(c, list):
            out.append([int(x) for x in c])
        elif isinstance(c, dict) and 'cycle_vertices' in c:
            out.append([int(x) for x in c['cycle_vertices'].split(',')])
    return out


def build_edge_to_cycle_index(cycles: List[List[int]]) -> Dict[Tuple[int, int], List[int]]:
    edge_to_cycles: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for idx, cyc in enumerate(cycles):
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            edge_to_cycles[(a, b)].append(idx)
    return edge_to_cycles


def load_top_edges(path: Path, top_n: int = 20) -> List[Tuple[int, int]]:
    j = json.loads(path.read_text(encoding='utf-8'))
    top = j.get('top_edges', [])[:top_n]
    return [(e['edge_a'], e['edge_b']) for e in top]


def load_canonical_roots(path: Path) -> List[Tuple[int, ...]]:
    data = json.loads(path.read_text(encoding='utf-8'))
    roots: List[Tuple[int, ...]] = []
    if isinstance(data, list):
        for ent in data:
            coords = ent.get('root_coords')
            if coords:
                roots.append(tuple(int(x) for x in coords))
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict) and 'root_coords' in v:
                coords = v['root_coords']
                roots.append(tuple(int(x) for x in coords))
            else:
                # try parsing key
                s = k.strip()
                if s.startswith('(') or s.startswith('['):
                    inner = s.strip('()[]')
                    parts = [p.strip() for p in inner.split(',') if p.strip()]
                    try:
                        coords = tuple(int(x) for x in parts)
                        roots.append(coords)
                    except Exception:
                        continue
    return roots


def dist2(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return sum((int(a) - int(b)) ** 2 for a, b in zip(u, v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top-edges-json', type=Path, default=Path('analysis/minimal_commutator_cycles/problem_cycle_edge_tally.json'))
    ap.add_argument('--top-n', type=int, default=20)
    ap.add_argument('--combined-map', type=Path, default=Path('artifacts/edge_to_e8_root_combined.json'))
    ap.add_argument('--cycles-json', type=Path, default=Path('analysis/minimal_commutator_cycles/det1_orbit_cycles.json'))
    ap.add_argument('--canonical-root-file', type=Path, default=Path('artifacts/edge_root_bijection_canonical.json'))
    ap.add_argument('--candidate-limit', type=int, default=50)
    ap.add_argument('--top-candidates', type=int, default=12)
    ap.add_argument('--apply-threshold', type=int, default=2)
    ap.add_argument('--out-json', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_candidates.json'))
    ap.add_argument('--out-csv', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_candidates.csv'))
    ap.add_argument('--apply-csv', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_apply.csv'))
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    combined_map = load_combined_map(args.combined_map)
    cycles = load_cycles(args.cycles_json)
    edge_to_cycles = build_edge_to_cycle_index(cycles)
    top_edges = load_top_edges(args.top_edges_json, top_n=args.top_n)
    canonical_roots = load_canonical_roots(args.canonical_root_file)

    assigned_vectors = set(combined_map.values())

    report = {'top_edges': [], 'candidate_limit': args.candidate_limit, 'apply_threshold': args.apply_threshold}
    apply_rows = []

    for a,b in top_edges:
        key = (a,b)
        current = combined_map.get(key)
        # find nearest canonical roots
        neighbors = sorted(canonical_roots, key=lambda r: dist2(r, current) if current else 0)[:args.candidate_limit]
        candidates = []
        cyc_indices = edge_to_cycles.get((a,b), [])
        for r in neighbors[:args.top_candidates]:
            if current and tuple(r) == tuple(current):
                continue
            # simulate fixed cycles: cycles containing (a,b) where all other edges have assigned roots
            fixed = 0
            for idx in cyc_indices:
                cyc = cycles[idx]
                all_present = True
                for i in range(len(cyc)):
                    x=cyc[i]; y=cyc[(i+1)%len(cyc)]
                    if (x,y) == key:
                        continue
                    if (x,y) not in combined_map:
                        all_present = False
                        break
                if all_present:
                    fixed += 1
            # add candidate
            candidates.append({'vector': list(r), 'score': 0, 'fixed_cycles': fixed})
            if fixed >= args.apply_threshold:
                apply_rows.append({'edge_a': a, 'edge_b': b, 'vector': json.dumps(list(r)), 'score': 0, 'fixed_cycles': fixed})

        candidates.sort(key=lambda c: (-c['fixed_cycles']))
        report['top_edges'].append({'edge': f'{a},{b}', 'num_cycles': len(cyc_indices), 'candidates': candidates[:args.top_candidates]})

    args.out_json.write_text(json.dumps(report, indent=2), encoding='utf-8')
    with args.out_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['edge','num_cycles','top_candidate_vector','top_fixed_cycles'])
        for ent in report['top_edges']:
            top = ent['candidates'][0] if ent['candidates'] else None
            w.writerow([ent['edge'], ent['num_cycles'], json.dumps(top['vector']) if top else '', top['fixed_cycles'] if top else 0])

    print('Wrote nearest canonical candidate JSON/CSV')

    if not args.dry_run and apply_rows:
        with args.apply_csv.open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['edge_a','edge_b','count','candidate_idx','vector','score','confidence','tag','source','note','derived_from','suggested_apply','apply','comment'])
            for r in apply_rows:
                w.writerow([r['edge_a'], r['edge_b'], 0, 0, r['vector'], r['score'], 'auto', 'canon_nn', 'nearest_canonical', 'auto-infer', '', 'yes', 'yes', f"fixed_{r['fixed_cycles']}"])
        print('Wrote apply CSV to', args.apply_csv)


if __name__ == '__main__':
    main()
