#!/usr/bin/env python3
"""Annotate signed cubic triads with F3 coefficients and Heisenberg geometry.

Input JSON format:
{
  "triads": [{"triad": [a,b,c], "sign": 1}, ...],
  "labels": {"1": {"u": [x,y], "z": z}, ...}
}

Output JSON: list of annotated triads with fields: triad, coeff, geometry, optional u_line and z_profile
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any

from e6_f3_trilinear import HeisenbergLabel, triad_key, sign_to_f3_coeff, classify_triad_geometry, sorted_u_line_for_triad, z_profile_over_u_line


def load_input(path: Path) -> tuple[List[Dict[str, Any]], Dict[int, HeisenbergLabel]]:
    j = json.loads(path.read_text(encoding='utf-8'))
    triads = j.get('triads', [])
    labels_raw = j.get('labels', {})
    labels: Dict[int, HeisenbergLabel] = {}
    for k, v in labels_raw.items():
        kid = int(k)
        if isinstance(v, dict) and 'u' in v and 'z' in v:
            u = tuple(int(x) for x in v['u'])
            z = int(v['z'])
            labels[kid] = HeisenbergLabel(u=u, z=z)
        else:
            raise ValueError(f"Invalid label entry for {k}: {v}")
    return triads, labels


def annotate_triads(triads: List[Dict[str, Any]], labels: Dict[int, HeisenbergLabel]) -> List[Dict[str, Any]]:
    out = []
    for ent in triads:
        tri = tuple(int(x) for x in ent['triad'])
        key = triad_key(tri)
        sign = int(ent.get('sign', 1))
        coeff = sign_to_f3_coeff(sign)
        geom = classify_triad_geometry(key, labels)
        rec: Dict[str, Any] = {'triad': list(key), 'coeff': coeff, 'geometry': geom}
        if geom == 'affine_line':
            u_line = sorted_u_line_for_triad(key, labels)
            rec['u_line'] = [list(u) for u in u_line]
            rec['z_profile'] = list(z_profile_over_u_line(key, labels, u_line))
        out.append(rec)
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--infile', type=Path, required=True)
    p.add_argument('--out-json', type=Path, default=Path('analysis/e6_f3_trilinear_annotated.json'))
    args = p.parse_args(argv)

    triads, labels = load_input(args.infile)
    annotated = annotate_triads(triads, labels)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps({'annotated_triads': annotated}, indent=2), encoding='utf-8')
    print('Wrote annotated triads to', args.out_json)


if __name__ == '__main__':
    main()
