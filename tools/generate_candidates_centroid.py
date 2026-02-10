#!/usr/bin/env python3
"""Generate centroid-based nearest canonical candidates for top problem edges.

Writes:
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_candidates_centroid.json
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_candidates_centroid.csv
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_apply_centroid.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def dist2(u: Tuple[int, ...], v: Tuple[float, ...]) -> float:
    return sum((float(a) - float(b)) ** 2 for a, b in zip(u, v))


def main():
    top_edges_j = load_json(Path('analysis/minimal_commutator_cycles/problem_cycle_edge_tally.json'))
    top_edges = top_edges_j.get('top_edges', [])[:20]

    combined = load_json(Path('artifacts/edge_to_e8_root_combined.json'))
    combined_map: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    for k, coords in combined.items():
        if isinstance(k, str) and k.startswith('('):
            s = k.strip()[1:-1]
            a_s, b_s = s.split(',')
            combined_map[(int(a_s), int(b_s))] = tuple(int(x) for x in coords)

    canonical = load_json(Path('artifacts/edge_root_bijection_canonical.json'))
    canonical_roots: List[Tuple[int, ...]] = []
    if isinstance(canonical, list):
        for ent in canonical:
            coords = ent.get('root_coords')
            if coords:
                canonical_roots.append(tuple(int(x) for x in coords))
    elif isinstance(canonical, dict):
        for k, v in canonical.items():
            if isinstance(v, dict) and 'root_coords' in v:
                canonical_roots.append(tuple(int(x) for x in v['root_coords']))
            else:
                s = k.strip()
                if s.startswith('(') or s.startswith('['):
                    inner = s.strip('()[]')
                    parts = [p.strip() for p in inner.split(',') if p.strip()]
                    try:
                        canonical_roots.append(tuple(int(x) for x in parts))
                    except Exception:
                        pass

    cycles_j = load_json(Path('analysis/minimal_commutator_cycles/det1_orbit_cycles.json'))
    cycles = cycles_j.get('canonical_cycles') or cycles_j.get('cycles') or []
    cycles_list = [[int(x) for x in c['cycle']] for c in cycles]

    # build edge->cycle index
    edge_to_cycles = {}
    for idx, cyc in enumerate(cycles_list):
        n = len(cyc)
        for i in range(n):
            a = cyc[i]; b = cyc[(i+1) % n]
            edge_to_cycles.setdefault((a,b), []).append(idx)

    report = {'top_edges': [], 'candidate_limit': 50}
    apply_rows = []

    for ent in top_edges:
        a = ent['edge_a']; b = ent['edge_b']; count = ent['count']
        key = (a,b)
        # compute centroid from neighbors of a and b
        neighbor_vecs = []
        for (x,y), vec in combined_map.items():
            if x == a or y == a or x == b or y == b:
                if (x,y) in [(a,b),(b,a)]:
                    continue
                neighbor_vecs.append(tuple(float(v) for v in vec))
        centroid = None
        if neighbor_vecs:
            m = len(neighbor_vecs)
            centroid = [sum(vec[i] for vec in neighbor_vecs) / m for i in range(8)]
        else:
            centroid = [0.0]*8
        # find nearest canonical roots to centroid
        neighbors = sorted(canonical_roots, key=lambda r: dist2(r, centroid))[:50]
        candidates = []
        cyc_indices = edge_to_cycles.get(key, [])
        for r in neighbors[:12]:
            # compute fixed cycles: cycles containing (a,b) where all other edges have assigned roots
            fixed = 0
            for idx in cyc_indices:
                cyc = cycles_list[idx]
                all_present = True
                for i in range(len(cyc)):
                    x = cyc[i]; y = cyc[(i+1)%len(cyc)]
                    if (x,y) == key: continue
                    if (x,y) not in combined_map:
                        all_present = False; break
                if all_present:
                    fixed += 1
            candidates.append({'vector': list(r), 'score': -dist2(r, centroid), 'fixed_cycles': fixed})
            if fixed >= 2:
                apply_rows.append({'edge_a': a, 'edge_b': b, 'vector': json.dumps(list(r)), 'score': int(-dist2(r, centroid)), 'fixed_cycles': fixed})

        candidates.sort(key=lambda c: (-c['fixed_cycles'], -c['score']))
        report['top_edges'].append({'edge': f'{a},{b}', 'count': count, 'num_cycles': len(cyc_indices), 'candidates': candidates})

    out_json = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_candidates_centroid.json')
    out_csv = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_candidates_centroid.csv')
    out_apply = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_nearest_canonical_apply_centroid.csv')

    out_json.write_text(json.dumps(report, indent=2), encoding='utf-8')

    with out_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['edge','count','num_cycles','top_candidate_vector','top_fixed_cycles','top_score'])
        for ent in report['top_edges']:
            top = ent['candidates'][0] if ent['candidates'] else None
            w.writerow([ent['edge'], ent['count'], ent['num_cycles'], json.dumps(top['vector']) if top else '', top['fixed_cycles'] if top else 0, top['score'] if top else ''])

    with out_apply.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['edge_a','edge_b','count','candidate_idx','vector','score','confidence','tag','source','note','derived_from','suggested_apply','apply','comment'])
        for r in apply_rows:
            w.writerow([r['edge_a'], r['edge_b'], 0, 0, r['vector'], r['score'], 'auto', 'canon_nn', 'centroid', 'auto-generated', '', 'yes', 'no', f"fixed_{r['fixed_cycles']}"])

    print('Wrote centroid nearest canonical candidates JSON/CSV and apply CSV (suggest-only)')


if __name__ == '__main__':
    main()
