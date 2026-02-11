import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import argparse
from pathlib import Path

from scripts.edge_to_e8_mapping import (
    cp_sat_local_refine,
    detect_hotspots,
    plot_adj_preservation,
    plot_feature_embeddings,
    run_feature_hungarian_mapping,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refine", action="store_true", help="Run CP-SAT local refinement on hotspots"
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=5.0,
        help="CP-SAT time limit per cluster (seconds)",
    )
    parser.add_argument(
        "--cluster-size", type=int, default=8, help="Max cluster size for CP-SAT"
    )
    args = parser.parse_args()

    mapping, result, score_matrix, meta = run_feature_hungarian_mapping(
        write_artifact=True
    )
    print("Feature mapping completed, adj_score=", result.get("adj_score"))

    # generate figures
    fig1 = plot_feature_embeddings(mapping, score_matrix, meta)
    fig2 = plot_adj_preservation(mapping, meta)
    if fig1:
        print("Wrote", fig1)
    if fig2:
        print("Wrote", fig2)

    if args.refine:
        clusters = []
        # attempt to detect multiple disjoint hotspots
        first = detect_hotspots(mapping, meta, top_k=20, max_cluster=args.cluster_size)
        if first:
            clusters.append(first)
        for c in clusters:
            print("Refining cluster:", c)
            mapping, local_score = cp_sat_local_refine(
                mapping, c, top_k=6, time_limit=args.time_limit
            )
            print("Cluster local_score:", local_score)
        # write refined mapping artifact
        outp = Path("artifacts") / "edge_root_mapping_feature_refined.json"
        outp.parent.mkdir(parents=True, exist_ok=True)
        import json

        with outp.open("w", encoding="utf-8") as f:
            json.dump({"sample": list(mapping.items())[:50]}, f, indent=2)
        print("Wrote", outp)
