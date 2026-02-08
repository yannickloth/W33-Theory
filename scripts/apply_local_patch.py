#!/usr/bin/env python3
"""Apply a local CP-SAT patch to the global bijection and report triangle exactness delta.

Usage:
  python scripts/apply_local_patch.py --bij checks/PART_CVII_e8_bijection.json --local checks/PART_CVII_e8_bijection_local_seed_20260207T184002Z.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import time
from pathlib import Path

from optimize_bijection_cocycle import triangle_exact, build_triangles
from e8_embedding_group_theoretic import build_w33, generate_e8_roots


def find_latest_local(pattern='checks/PART_CVII_e8_bijection_local_seed_*.json'):
    files = glob.glob(pattern)
    if not files:
        return None
    files = sorted(files, key=os.path.getmtime, reverse=True)
    return files[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bij', default='checks/PART_CVII_e8_bijection.json')
    parser.add_argument('--local', default=None)
    parser.add_argument('--auto-commit', action='store_true', help='If set, commit patched bijection to git')
    parser.add_argument('--commit-branch', type=str, default=None, help='Branch to push commits to when --push is used')
    parser.add_argument('--push', action='store_true', help='Push commits after creating them')
    parser.add_argument('--commit-msg', type=str, default=None, help='Custom commit message')
    args = parser.parse_args()

    local_file = args.local or find_latest_local()
    if not local_file:
        raise SystemExit('No local CP-SAT result file found')

    bij_file = Path(args.bij)
    if not bij_file.exists():
        raise SystemExit(f'Bijection file not found: {bij_file}')

    seed = json.loads(open(local_file, encoding='utf-8').read())
    if not seed.get('assignments'):
        raise SystemExit('Local result has no assignments')

    local_assign = {int(k): int(v) for k, v in seed['assignments'].items()}

    bij_json = json.loads(bij_file.read_text(encoding='utf-8'))
    bij0 = {int(k): int(v) for k, v in bij_json.get('bijection', {}).items()}

    # compute triangles exactness before
    n, vertices, adj, edges = build_w33()
    roots = generate_e8_roots()
    tri_list = build_triangles(n, adj)
    before_exact = sum(1 for t in tri_list if triangle_exact(roots, bij0, edges, t))

    # apply local assignments
    bij_new = dict(bij0)
    for e, r in local_assign.items():
        bij_new[int(e)] = int(r)

    # check uniqueness
    if len(set(bij_new.values())) != len(bij_new.values()):
        # warn, but continue
        print('Warning: duplicate root assignments after patch')

    after_exact = sum(1 for t in tri_list if triangle_exact(roots, bij_new, edges, t))

    delta = after_exact - before_exact

    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    outpath = Path.cwd() / 'checks' / f'PART_CVII_e8_bijection_patched_{stamp}.json'
    out = {
        'patched_from': str(bij_file),
        'local': str(local_file),
        'delta_exact': int(delta),
        'before_exact': int(before_exact),
        'after_exact': int(after_exact),
        'changed_edges': len(local_assign),
        'bijection': {str(k): int(v) for k, v in bij_new.items()},
    }
    outpath.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'Wrote patched bijection to {outpath}')
    print(f'Before exact: {before_exact}  After exact: {after_exact}  Delta: {delta}')

    # Mirror artifact to tracked artifacts/ folder (useful when checks/ is git-ignored)
    # write to a tracked artifacts folder unless you prefer otherwise
    artifact_out = Path.cwd() / 'committed_artifacts' / outpath.name
    artifact_out.parent.mkdir(parents=True, exist_ok=True)
    artifact_out.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print('Also wrote committed artifact to', artifact_out)

    # Optional auto-commit of the patched bijection and generated seed
    if getattr(args, 'auto_commit', False):
        try:
            import subprocess
            import git_auto_keep

            commit_msg = args.commit_msg or f'Apply local bijection patch: delta={delta} [{stamp}]'
            ok, msg = git_auto_keep.git_add_commit([str(artifact_out)], commit_msg, branch=args.commit_branch, push=args.push)
            print('Auto-commit:', ok, msg)

            # Generate seed from patched bijection and commit the artifact seed as well
            seed_out = Path.cwd() / 'checks' / f'PART_CVII_e8_bijection_seed_patched_{stamp}.json'
            artifact_seed = Path.cwd() / 'committed_artifacts' / seed_out.name
            subprocess.run([
                'py', '-3', '-X', 'utf8', 'scripts/write_seed_from_bijection.py',
                '--in', str(outpath), '--out', str(seed_out)
            ], check=False)
            artifact_seed.parent.mkdir(parents=True, exist_ok=True)
            artifact_seed.write_text(seed_out.read_text(encoding='utf-8'), encoding='utf-8')
            ok2, msg2 = git_auto_keep.git_add_commit([str(artifact_seed)], f'Seed from patched bijection: {stamp}', branch=args.commit_branch, push=args.push)
            print('Seed auto-commit:', ok2, msg2)
        except Exception as e:
            print('Auto-commit failed:', e)


if __name__ == '__main__':
    main()
