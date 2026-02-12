#!/usr/bin/env python3
"""Run a heavy CP-SAT local refinement campaign on top feature-driven mappings.

This script seeds a Hungarian mapping with the given weights and runs CP-SAT local
refinements on detected hotspots. Useful to give CP-SAT a long time budget per cluster.
"""

import argparse
import json
from pathlib import Path

from scripts.edge_to_e8_mapping import (
    run_feature_hungarian_mapping,
    detect_hotspots,
    cp_sat_local_refine,
    
    compute_adjacency_score,
    plot_feature_embeddings,
    plot_adj_preservation,
)


def run_heavy_refine(
    weights=None,
    use_orbit_features=False,
    time_limit=300,
    cluster_size=20,
    top_k=12,
    max_clusters=1,
    write_artifact=True,
):
    """Run heavy CP-SAT refine and return (mapping, initial_score, final_score)."""
    mapping, result, score_matrix, meta = run_feature_hungarian_mapping(
        weights=weights, write_artifact=write_artifact, use_orbit_features=use_orbit_features
    )
    initial_score = result.get("adj_score")
    print("Initial adj_score:", initial_score)

    clusters = []
    blocked = set()

    for i in range(max_clusters):
        c = detect_hotspots(mapping, meta, top_k=40, max_cluster=cluster_size)
        if not c:
            break
        # filter out already-processed edges
        c = [e for e in c if e not in blocked]
        if not c:
            break
        clusters.append(c)
        for e in c:
            blocked.add(e)
        print(f"Refining cluster {len(clusters)} size={len(c)} with CP-SAT time_limit={time_limit}s")
        mapping_new, local_score = cp_sat_local_refine(
            mapping, c, top_k=top_k, time_limit=time_limit
        )
        precluster_score = compute_adjacency_score({e: mapping[e] for e in c})
        print("Cluster local score before:", precluster_score, "after:", local_score)
        # adopt mapping_new for cluster edges
        for e in c:
            mapping[e] = mapping_new[e]

        # check global effect and, if no improvement, try adjacency-aware candidates + CP-SAT
        global_before = compute_adjacency_score(mapping)
        global_after = compute_adjacency_score(mapping)
        print("Global adj before attempt:", global_before, "after attempt:", global_after)
        if global_after <= global_before:
            print("No global improvement from CP-SAT; trying adjacency-aware candidate generation and CP-SAT")
            try:
                # build candidate lists emphasizing adjacency compatibility
                from scripts.edge_to_e8_mapping import (
                    select_candidate_roots_by_compatibility,
                    cp_sat_local_refine_with_candidates,
                )
                candid_roots = select_candidate_roots_by_compatibility(
                    score_matrix, mapping, c, meta, top_m=200, top_k=top_k, adjacency_weight=1.0
                )
                mapping2, local_score2 = cp_sat_local_refine_with_candidates(
                    mapping, c, candid_roots, time_limit=time_limit
                )
                global_after2 = compute_adjacency_score(mapping2)
                print("Candidate CP-SAT global after:", global_after2, "local_score:", local_score2)
                if global_after2 > global_after:
                    print("Candidate CP-SAT improved global score — adopting new mapping")
                    mapping = mapping2
            except Exception as e:
                print("Candidate CP-SAT fallback failed:", type(e).__name__, e)

    final_score = compute_adjacency_score(mapping)

    if write_artifact:
        out = Path("artifacts") / "edge_root_mapping_feature_heavy_refine.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "initial_adj_score": initial_score,
                    "final_adj_score": final_score,
                    "clusters": clusters,
                },
                f,
                indent=2,
                default=str,
            )
        print("Wrote", out)

    # regenerate figures
    try:
        plot_feature_embeddings(mapping, score_matrix, meta)
        plot_adj_preservation(mapping, meta)
    except Exception:
        pass

    return mapping, initial_score, final_score


def _parse_weights(slist):
    try:
        if len(slist) == 3:
            return {"emb": float(slist[0]), "geom": float(slist[1]), "meta": float(slist[2])}
    except Exception:
        pass
    raise ValueError("--weights expects three floats: emb geom meta")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--weights",
        type=float,
        nargs=3,
        help="weights: emb geom meta",
        default=[0.005, 0.0, 0.995],
    )
    parser.add_argument("--use-orbit-features", action="store_true")
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--cluster-size", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--max-clusters", type=int, default=1)
    parser.add_argument("--no-write-artifact", action="store_true")
    args = parser.parse_args()

    weights = {"emb": args.weights[0], "geom": args.weights[1], "meta": args.weights[2]}

    mapping, init, final = run_heavy_refine(
        weights=weights,
        use_orbit_features=args.use_orbit_features,
        time_limit=args.time_limit,
        cluster_size=args.cluster_size,
        top_k=args.top_k,
        max_clusters=args.max_clusters,
        write_artifact=not args.no_write_artifact,
    )
    print("Done. initial adj:", init, "final adj:", final)


if __name__ == "__main__":
    main()
