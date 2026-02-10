#!/usr/bin/env python3
"""Suggest candidate E8 root vectors for missing W33 edge->root mappings.

Output:
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.json
 - analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.csv

Heuristics used:
 - Direct candidates from the parser's aggregated vec->edges map
 - Reversed-orientation fallback if a reversed edge has candidates
 - Centroid of incident edge vectors (rounded) and nearest neighbor suggestions
 - Nearest neighbor search across all existing mapped vectors

Usage:
  python tools/suggest_missing_edge_candidates.py [--missing-json PATH] [--top-n 40] [--candidates-per-edge 5]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Local import
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.w33_rootword_uv_parser import W33RootwordParser


TAG_PRIORITY = {
    "canon": 6,
    "raw": 5,
    "we6": 4,
    "e8root": 4,
    "e8root_to_edge": 4,
    "raw-offset": 3,
    "fallback": 2,
    "archive": 1,
}


def parse_missing_edges(path: Path) -> List[Tuple[int, int, int]]:
    """Return list of tuples (a,b,count) for missing edges."""
    if not path.exists():
        raise FileNotFoundError(f"Missing edges file not found: {path}")
    data = json.loads(path.read_text(encoding='utf-8'))
    if 'missing_edges' in data:
        out = []
        for ent in data['missing_edges']:
            edge = ent.get('edge')
            if not edge:
                continue
            a_s, b_s = edge.split(',')
            out.append((int(a_s), int(b_s), int(ent.get('count', 1))))
        return out
    # fallback: if it's a list of rows
    if isinstance(data, list):
        out = []
        for ent in data:
            edge = ent.get('missing_edge') or ent.get('edge')
            if not edge:
                continue
            if isinstance(edge, str) and ',' in edge:
                a_s, b_s = edge.split(',')
                out.append((int(a_s), int(b_s), int(ent.get('count', 1))))
        return out
    raise RuntimeError('Unsupported missing edges JSON format')


def dist2(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return sum((int(a) - int(b)) ** 2 for a, b in zip(u, v))


def round_vec(vec: List[float]) -> Tuple[int, ...]:
    return tuple(int(round(x)) for x in vec)


def build_inverse_vec_map(p: W33RootwordParser) -> Dict[Tuple[int, int], List[Tuple[Tuple[int, ...], str]]]:
    """Build edge -> candidate vectors mapping from parser.vec_to_edges_map."""
    edge_map: Dict[Tuple[int, int], List[Tuple[Tuple[int, ...], str]]] = defaultdict(list)
    for vec, entries in getattr(p, 'vec_to_edges_map', {}).items():
        for (edge, tag) in entries:
            edge_map[edge].append((tuple(vec), tag))
    return edge_map


def get_incident_vectors(edge_to_root: Dict[Tuple[int, int], Tuple[int, ...]], vertex: int) -> List[Tuple[int, ...]]:
    out = []
    for (a, b), v in edge_to_root.items():
        if a == vertex or b == vertex:
            out.append(tuple(v))
    return out


def propose_candidates_for_edge(a: int, b: int, p: W33RootwordParser, edge_candidates_map: Dict[Tuple[int, int], List[Tuple[Tuple[int, ...], str]]], existing_edge_to_root: Dict[Tuple[int, int], Tuple[int, ...]], all_mapped_vectors: List[Tuple[Tuple[int, ...], Tuple[int, int], str]], candidates_per_edge: int = 5) -> List[Dict[str, Any]]:
    """Return ranked candidates for oriented edge (a,b)."""
    candidates: List[Dict[str, Any]] = []

    # 1) Direct candidates from vec->edges aggregation
    direct = edge_candidates_map.get((a, b), [])
    for vec, tag in direct:
        score = 100 + TAG_PRIORITY.get(tag, 0)
        candidates.append({
            'vector': list(vec),
            'tag': tag,
            'score': score,
            'source': 'direct',
            'note': 'vec_to_edges_map direct candidate',
            'derived_from': [],
        })

    # 1b) reversed-oriented candidates if the reversed edge has entries
    rev = edge_candidates_map.get((b, a), [])
    for vec, tag in rev:
        # flip sign to orient for (a,b)
        vec_neg = tuple(-int(x) for x in vec)
        score = 80 + TAG_PRIORITY.get(tag, 0)
        candidates.append({
            'vector': list(vec_neg),
            'tag': tag,
            'score': score,
            'source': 'reversed',
            'note': f'reversed candidate from ({b},{a})',
            'derived_from': [(vec, (b, a), tag)],
        })

    # 2) Incident-centroid heuristic
    incident_a = get_incident_vectors(existing_edge_to_root, a)
    incident_b = get_incident_vectors(existing_edge_to_root, b)
    incident = incident_a + incident_b
    if incident:
        n = len(incident)
        mean_vec = [sum(v[i] for v in incident) / n for i in range(len(incident[0]))]
        cent = round_vec(mean_vec)
        # if centroid matches a known mapped vector or vec->edges_map, propose it
        if cent in getattr(p, 'vec_to_edges_map', {}):
            candidates.append({
                'vector': list(cent),
                'tag': 'centroid',
                'score': 70,
                'source': 'centroid',
                'note': 'centroid matched existing vec_to_edges_map',
                'derived_from': [],
            })
        else:
            # propose nearest neighbors to centroid from known mapped vectors
            nn = sorted(all_mapped_vectors, key=lambda t: dist2(t[0], cent))[:candidates_per_edge]
            rank = 1
            for vec, mapped_edge, tag in nn:
                d2 = dist2(vec, cent)
                score = max(60 - int(d2), 10)
                candidates.append({
                    'vector': list(vec),
                    'tag': tag if tag else 'nn',
                    'score': score,
                    'source': 'centroid_nn',
                    'note': f'neighbor to centroid (dist2={d2}) mapped currently to {mapped_edge}',
                    'derived_from': [({'centroid': list(cent)}, mapped_edge, tag)],
                })
                rank += 1

    # 3) Global nearest neighbor fallback
    # use centroid if present else average zero
    basis = round_vec(mean_vec) if incident else None
    if not incident:
        # use simple fallback => look globally for nearest mapped vectors
        nn = sorted(all_mapped_vectors, key=lambda t: dist2(t[0], (0,) * len(t[0])))[:candidates_per_edge]
        for vec, mapped_edge, tag in nn:
            d2 = dist2(vec, (0,) * len(vec))
            score = max(40 - int(d2), 5)
            candidates.append({
                'vector': list(vec),
                'tag': tag if tag else 'nn',
                'score': score,
                'source': 'global_nn',
                'note': f'global neighbor to zero (dist2={d2}) mapped to {mapped_edge}',
                'derived_from': [((0,) * len(vec), mapped_edge, tag)],
            })

    # 4) Deduplicate candidates by vector and keep best score
    by_vec: Dict[Tuple[int, ...], Dict[str, Any]] = {}
    for c in candidates:
        vt = tuple(int(x) for x in c['vector'])
        cur = by_vec.get(vt)
        if cur is None or c['score'] > cur['score']:
            by_vec[vt] = c

    # Format sorted list
    final = sorted(by_vec.values(), key=lambda d: d['score'], reverse=True)[:candidates_per_edge]

    # Add some confidence flags
    for c in final:
        s = c['score']
        if s >= 100:
            c['confidence'] = 'high'
        elif s >= 70:
            c['confidence'] = 'medium'
        else:
            c['confidence'] = 'low'
    return final


def build_all_mapped_vectors(p: W33RootwordParser) -> List[Tuple[Tuple[int, ...], Tuple[int, int], str]]:
    out = []
    for edge, vec in getattr(p, 'edge_to_root', {}).items():
        tvec = tuple(int(x) for x in vec)
        # find tag by scanning vec_to_edges_map entries for this vector (cheap)
        tag = None
        entries = getattr(p, 'vec_to_edges_map', {}).get(tvec)
        if entries:
            # pick highest priority tag among entries listing this edge
            for (e, tg) in entries:
                if e == edge:
                    tag = tg
                    break
            if not tag:
                tag = entries[0][1]
        out.append((tvec, edge, tag))
    return out


def generate_report(missing_json: Path, top_n: int = 40, candidates_per_edge: int = 5, out_dir: Path = Path('analysis/minimal_commutator_cycles')) -> Dict[str, Any]:
    p = W33RootwordParser()

    missing = parse_missing_edges(missing_json)
    missing_sorted = sorted(missing, key=lambda x: -x[2])[:top_n]

    edge_candidates_map = build_inverse_vec_map(p)
    existing_edge_to_root = getattr(p, 'edge_to_root', {})

    # precompute all mapped vectors
    all_mapped = build_all_mapped_vectors(p)

    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'missing_json': str(missing_json),
        'top_n': top_n,
        'candidates_per_edge': candidates_per_edge,
        'edges': [],
    }

    for a, b, count in missing_sorted:
        cands = propose_candidates_for_edge(a, b, p, edge_candidates_map, existing_edge_to_root, all_mapped, candidates_per_edge=candidates_per_edge)
        report['edges'].append({
            'edge': f'{a},{b}',
            'count': count,
            'num_direct_candidates': len(edge_candidates_map.get((a, b), [])),
            'candidates': cands,
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    jpath = out_dir / 'w33_uv_parser_det1_missing_edges_candidates.json'
    cpath = out_dir / 'w33_uv_parser_det1_missing_edges_candidates.csv'
    jpath.write_text(json.dumps(report, indent=2), encoding='utf-8')

    # write CSV summary
    with cpath.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['edge_a', 'edge_b', 'count', 'num_direct_candidates', 'top_candidate_vector', 'top_candidate_score', 'top_candidate_confidence'])
        for ent in report['edges']:
            a_s, b_s = ent['edge'].split(',')
            top = ent['candidates'][0] if ent['candidates'] else None
            top_vec = json.dumps(top['vector']) if top else ''
            top_score = top['score'] if top else ''
            top_conf = top['confidence'] if top else ''
            w.writerow([a_s, b_s, ent['count'], ent['num_direct_candidates'], top_vec, top_score, top_conf])

    # print short summary
    for ent in report['edges'][:min(20, len(report['edges']))]:
        top = ent['candidates'][0] if ent['candidates'] else None
        print(f"Edge {ent['edge']} (count={ent['count']}): direct={ent['num_direct_candidates']}, top={top['vector'] if top else None} score={top['score'] if top else None} conf={top['confidence'] if top else None}")

    print('\nWrote', jpath, cpath)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--missing-json', type=Path, default=Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges.json'))
    ap.add_argument('--top-n', type=int, default=40)
    ap.add_argument('--candidates-per-edge', type=int, default=5)
    ap.add_argument('--out-dir', type=Path, default=Path('analysis/minimal_commutator_cycles'))
    args = ap.parse_args()

    report = generate_report(args.missing_json, top_n=args.top_n, candidates_per_edge=args.candidates_per_edge, out_dir=args.out_dir)

    # friendly exit
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
