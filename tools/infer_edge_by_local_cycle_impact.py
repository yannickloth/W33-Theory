#!/usr/bin/env python3
"""Infer missing edge -> root candidates by local cycle impact simulation.

For each missing oriented edge from the det=1 missing-edge list, try candidate
vectors and count how many cycles that include that edge would become fully
covered (all edges have a root vector) if we applied that candidate for the
edge. Rank candidates by the number of cycles fixed.

Outputs:
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_inferred_candidates.json
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_inferred_candidates.csv

Options allow an apply-by-threshold mode where candidates that fix >= T cycles
are written to an apply CSV (ready to be applied via vet_candidates_and_apply)
and can optionally be auto-applied with backup.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Any

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
        cycles = data.get('canonical_cycles') or data.get('cycles')
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


def load_missing_edges(path: Path) -> List[Tuple[int, int, int]]:
    data = json.loads(path.read_text(encoding='utf-8'))
    # expected format {'missing_edges':[{'edge': 'a,b', 'count': N}, ...]} or list of rows
    out = []
    if isinstance(data, dict) and 'missing_edges' in data:
        for ent in data['missing_edges']:
            edge = ent.get('edge')
            if not edge:
                continue
            a_s, b_s = edge.split(',')
            out.append((int(a_s), int(b_s), int(ent.get('count', 1))))
    elif isinstance(data, list):
        for ent in data:
            e = ent.get('missing_edge') or ent.get('edge')
            if not e:
                continue
            if isinstance(e, str) and ',' in e:
                a_s, b_s = e.split(',')
                out.append((int(a_s), int(b_s), int(ent.get('count', 1))))
    else:
        raise RuntimeError('Unsupported missing edges format')
    return out


def load_candidate_graph(path: Path) -> Dict[Tuple[int, int], List[Tuple[Tuple[int, ...], str, int]]]:
    # returns mapping edge -> list of (vector, tag, score)
    data = json.loads(path.read_text(encoding='utf-8'))
    edges = data.get('edges', [])
    out: Dict[Tuple[int, int], List[Tuple[Tuple[int, ...], str, int]]] = {}
    for ent in edges:
        a_s, b_s = ent['edge'].split(',')
        a = int(a_s); b = int(b_s)
        cand_list = []
        for c in ent.get('candidates', []):
            vec = tuple(int(x) for x in c['vector'])
            tag = c.get('tag', '')
            score = int(c.get('score', 0))
            cand_list.append((vec, tag, score))
        out[(a, b)] = cand_list
    return out


def load_canonical_roots(src: Path) -> List[Tuple[int, ...]]:
    data = json.loads(src.read_text(encoding='utf-8'))
    roots: List[Tuple[int, ...]] = []
    if isinstance(data, list):
        for ent in data:
            coords = ent.get('root_coords')
            if coords:
                roots.append(tuple(int(x) for x in coords))
    elif isinstance(data, dict):
        # possibly e8_root_to_edge or other structures keyed by root string
        for k in data.keys():
            s = k.strip()
            if s.startswith('(') or s.startswith('['):
                inner = s.strip('()[]')
                parts = [p.strip() for p in inner.split(',') if p.strip()]
                if parts:
                    try:
                        coords = tuple(int(x) for x in parts)
                        roots.append(coords)
                    except Exception:
                        continue
    return roots


def infer_for_edge(a: int, b: int, combined_map: Dict[Tuple[int, int], Tuple[int, ...]], cycles: List[List[int]], edge_to_cycles: Dict[Tuple[int, int], List[int]], candidate_graph: Dict[Tuple[int, int], List[Tuple[Tuple[int, ...], str, int]]], canonical_roots: List[Tuple[int, ...]], candidate_limit: int = 50) -> Dict[str, Any]:
    # Build candidate pool: direct candidates first
    pool: List[Tuple[Tuple[int, ...], str, int]] = []
    direct = candidate_graph.get((a, b), [])
    pool.extend(direct)
    # reversed
    rev = candidate_graph.get((b, a), [])
    for vec, tag, score in rev:
        pool.append((tuple(-int(x) for x in vec), tag + '-rev', score))

    # add some canonical roots not currently in combined_map
    assigned_vectors = set(v for v in combined_map.values())
    extra = [r for r in canonical_roots if r not in assigned_vectors]
    # take first candidate_limit extras
    for r in extra[:candidate_limit]:
        pool.append((r, 'canonical_unassigned', 0))

    # deduplicate pool
    seen = set()
    pool2 = []
    for vec, tag, score in pool:
        if vec in seen:
            continue
        seen.add(vec)
        pool2.append((vec, tag, score))
    pool = pool2

    # list cycles that include (a,b)
    cyc_indices = edge_to_cycles.get((a, b), [])

    results = []

    for vec, tag, score in pool:
        fixed = 0
        parsed = 0
        for idx in cyc_indices:
            cyc = cycles[idx]
            # check every oriented edge in this cycle if mapping exists (taking (a,b) replaced by vec)
            all_present = True
            for i in range(len(cyc)):
                x = cyc[i]; y = cyc[(i + 1) % len(cyc)]
                if (x, y) == (a, b):
                    continue
                if (x, y) not in combined_map:
                    all_present = False
                    break
            if all_present:
                fixed += 1
        results.append({'vector': list(vec), 'tag': tag, 'score': score, 'fixed_cycles': fixed})

    results.sort(key=lambda r: (-r['fixed_cycles'], -r['score']))
    return {'edge': f'{a},{b}', 'num_cycles': len(cyc_indices), 'candidates': results}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--missing-json', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges.json'))
    p.add_argument('--candidates-json', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.json'))
    p.add_argument('--combined-map', type=Path, default=Path('artifacts/edge_to_e8_root_combined.json'))
    p.add_argument('--cycles-json', type=Path, default=Path('analysis/minimal_commutator_cycles/det1_orbit_cycles.json'))
    p.add_argument('--canonical-root-file', type=Path, default=Path('artifacts/edge_root_bijection_canonical.json'))
    p.add_argument('--top-n', type=int, default=40)
    p.add_argument('--candidate-limit', type=int, default=50)
    p.add_argument('--out-json', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_inferred_candidates.json'))
    p.add_argument('--out-csv', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_inferred_candidates.csv'))
    p.add_argument('--apply-threshold', type=int, default=3, help='If a candidate fixes >= this many cycles, include in a apply CSV')
    p.add_argument('--apply-csv', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_inferred_apply.csv'))
    p.add_argument('--dry-run', action='store_true', help='Do not write apply CSV even if candidates meet threshold')
    args = p.parse_args()

    cycles = load_cycles(args.cycles_json)
    edge_to_cycles = build_edge_to_cycle_index(cycles)
    combined_map = load_combined_map(args.combined_map)
    missing = load_missing_edges(args.missing_json)[:args.top_n]

    candidate_graph = {}
    if args.candidates_json.exists():
        candidate_graph = load_candidate_graph(args.candidates_json)

    canonical_roots = load_canonical_roots(args.canonical_root_file)

    report = {
        'generated_from_missing': str(args.missing_json),
        'combined_map': str(args.combined_map),
        'top_n': args.top_n,
        'candidate_limit': args.candidate_limit,
        'applied_threshold': args.apply_threshold,
        'edges': []
    }

    apply_rows = []

    for a, b, cnt in missing:
        res = infer_for_edge(a, b, combined_map, cycles, edge_to_cycles, candidate_graph, canonical_roots, candidate_limit=args.candidate_limit)
        report['edges'].append(res)
        # if top candidate fixes >= threshold cycles, prepare an apply row
        if res['candidates']:
            top = res['candidates'][0]
            if top['fixed_cycles'] >= args.apply_threshold:
                apply_rows.append({'edge_a': a, 'edge_b': b, 'vector': json.dumps(top['vector']), 'score': top['score'], 'fixed_cycles': top['fixed_cycles'], 'tag': top['tag']})

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding='utf-8')

    # CSV summary
    with args.out_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['edge', 'num_cycles', 'top_vector', 'top_score', 'top_fixed_cycles', 'num_candidates'])
        for ent in report['edges']:
            top = ent['candidates'][0] if ent['candidates'] else None
            w.writerow([ent['edge'], ent['num_cycles'], json.dumps(top['vector']) if top else '', top['score'] if top else '', top['fixed_cycles'] if top else '', len(ent['candidates'])])

    print('Wrote inferred candidates JSON to', args.out_json)
    print('Wrote inferred candidates CSV to', args.out_csv)

    if not args.dry_run and apply_rows:
        # write apply CSV
        with args.apply_csv.open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['edge_a', 'edge_b', 'count', 'candidate_idx', 'vector', 'score', 'confidence', 'tag', 'source', 'note', 'derived_from', 'suggested_apply', 'apply', 'comment'])
            for r in apply_rows:
                comment = f"infer_fixed_{r['fixed_cycles']}"
                w.writerow([r['edge_a'], r['edge_b'], 0, 0, r['vector'], r['score'], 'inferred', r['tag'], 'infer', 'inferred candidate', '', 'yes', 'yes', comment])
        print('Wrote inferred apply CSV to', args.apply_csv)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
