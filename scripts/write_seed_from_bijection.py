#!/usr/bin/env python3
"""Write a seed JSON ('seed_edges') from a bijection JSON file.

Usage:
  python scripts/write_seed_from_bijection.py --in checks/PART_CVII_e8_bijection_patched_20260207T184058Z.json --out checks/PART_CVII_e8_bijection_seed_patched_20260207T184058Z.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inpath", required=True)
    parser.add_argument("--out", dest="outpath", required=True)
    parser.add_argument(
        "--auto-commit", action="store_true", help="If set, commit seed to git"
    )
    parser.add_argument(
        "--commit-branch",
        type=str,
        default=None,
        help="Branch to push commits to when --push is used",
    )
    parser.add_argument(
        "--push", action="store_true", help="Push commits after creating them"
    )
    args = parser.parse_args()

    inp = Path(args.inpath)
    outp = Path(args.outpath)
    j = json.loads(inp.read_text(encoding="utf-8"))
    bij = j.get("bijection") or j.get("bijection", {})
    if not bij:
        print("No bijection mapping found in input")
        return
    seed_edges = []
    for k, v in bij.items():
        seed_edges.append({"edge_index": int(k), "root_index": int(v)})
    out = {"seed_edges": seed_edges, "rotation": None}
    outp.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote seed to", outp)

    if getattr(args, "auto_commit", False):
        try:
            import git_auto_keep

            # write a tracked artifact copy
            artifact_out = Path.cwd() / "committed_artifacts" / outp.name
            artifact_out.parent.mkdir(parents=True, exist_ok=True)
            artifact_out.write_text(outp.read_text(encoding="utf-8"), encoding="utf-8")
            ok, msg = git_auto_keep.git_add_commit(
                [str(artifact_out)],
                f"Write seed from bijection: {artifact_out.name}",
                branch=args.commit_branch,
                push=args.push,
            )
            print("Seed auto-commit:", ok, msg)
        except Exception as e:
            print("Seed auto-commit failed:", e)


if __name__ == "__main__":
    main()
