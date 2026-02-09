#!/usr/bin/env python3
"""Classify z3 candidates by conjugacy class and centralizer size.

Loads a PART_CVII_z3_candidates_*.json (latest by mtime by default) and computes, for each
candidate:
 - permutation order (on 40 vertices)
 - centralizer size in PSp(4,3)
 - conjugacy class size = |G| / |centralizer|

Writes a timestamped JSON to checks/PART_CVII_z3_conjugacy_<ts>.json and logs progress to
checks/z3_conjugacy_run.log. Use --candidates-file to specify a particular candidate file.
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import sys
import time
from pathlib import Path

from w33_full_decomposition import build_psp43_group
from w33_homology import build_w33

# safe json dump
try:
    from utils.json_safe import dump_json
except Exception:
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from utils.json_safe import dump_json


def compose(p, q):
    # p, q are tuples representing permutations on {0..n-1}
    return tuple(p[q[i]] for i in range(len(q)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates-file",
        help="Path to PART_CVII_z3_candidates_*.json (default: latest in checks)",
    )
    parser.add_argument(
        "--log-file",
        default="checks/z3_conjugacy_run.log",
        help="Log file for run output",
    )
    args = parser.parse_args()

    # setup logging
    log_file = Path(args.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file), encoding="utf-8"),
        ],
    )
    log = logging.getLogger("w33_z3_conjugacy")

    try:
        if args.candidates_file:
            cand_file = Path(args.candidates_file)
            if not cand_file.exists():
                log.error("Specified candidates file does not exist: %s", cand_file)
                raise FileNotFoundError(cand_file)
        else:
            files = sorted(
                glob.glob("checks/PART_CVII_z3_candidates_*.json"),
                key=lambda p: Path(p).stat().st_mtime,
            )
            if not files:
                log.error("No candidate file found in checks/")
                raise FileNotFoundError("No candidate file found")
            cand_file = Path(files[-1])

        log.info("Using candidates file: %s", cand_file)
        data = json.loads(cand_file.read_text(encoding="utf-8"))

        n, vertices, adj, edges = build_w33()
        log.info("Built W33 data structures (n=%d vertices).", len(vertices))
        group = build_psp43_group(vertices, edges)
        group_elems = list(group.keys())
        Gsize = len(group_elems)
        log.info("Built PSp(4,3) group (|G|=%d).", Gsize)

        results = []
        for i, cand in enumerate(data.get("candidates", []), start=1):
            vperm = tuple(cand["vertex_perm"])
            # order on vertices
            ord1 = 1
            cur = vperm
            while cur != tuple(range(len(vperm))):
                cur = compose(vperm, cur)
                ord1 += 1
                if ord1 > 200:
                    log.warning("Candidate %d: order exceeded 200, breaking", i)
                    break
            # centralizer size
            cen = 0
            for g in group_elems:
                if compose(vperm, g) == compose(g, vperm):
                    cen += 1
            conj_size = Gsize // cen if cen > 0 else None
            results.append(
                {
                    "index": i,
                    "order_verts": ord1,
                    "centralizer_size": cen,
                    "conj_class_size": conj_size,
                }
            )

        ts = int(time.time())
        out = Path("checks") / f"PART_CVII_z3_conjugacy_{ts}.json"
        dump_json({"file": str(cand_file), "Gsize": Gsize, "results": results}, out)
        log.info("Wrote conjugacy summary: %s", out)

    except Exception as e:  # noqa: BLE001 - top-level handler prints/logs
        log.exception("Exception during conjugacy classification: %s", e)
        raise


if __name__ == "__main__":
    main()
