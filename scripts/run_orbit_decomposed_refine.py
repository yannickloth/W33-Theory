#!/usr/bin/env python3
"""Orbit-decomposed CP-SAT refine: break edges into Aut(W33) orbits and solve per-orbit.

This greedily refines mapping by solving CP-SAT on each orbit in turn (excluding roots
already used by previous orbits). It's a symmetry-aware, reduced-search strategy.
"""

import argparse
import json
from pathlib import Path

from scripts.edge_to_e8_mapping import (
    run_feature_hungarian_mapping,
    compute_edge_orbit_ids,
    select_candidate_roots_by_compatibility,
    cp_sat_local_refine_with_candidates,
    compute_adjacency_score,
    plot_feature_embeddings,
    plot_adj_preservation,
)


def run_orbit_decomposed_refine(
    weights=None,
    use_orbit_features=False,
    orbit_max_size=20,
    top_k=12,
    top_m=200,
    time_limit=120,
    write_artifact=True,
):
    mapping, result, score_matrix, meta = run_feature_hungarian_mapping(
        weights=weights, write_artifact=False, use_orbit_features=use_orbit_features
    )
    initial_score = result.get("adj_score")
    print("Initial adj score:", initial_score)

    edge_to_orbit, orbit_sizes = compute_edge_orbit_ids()
    # group orbit -> edges
    orbits = {}
    for e, oid in enumerate(edge_to_orbit):
        orbits.setdefault(oid, []).append(e)

    # sort orbits by size (largest first)
    orbit_list = sorted(orbits.items(), key=lambda x: len(x[1]), reverse=True)

    used_roots = set()

    for oid, edges in orbit_list:
        if len(edges) > orbit_max_size:
            continue
        print(f"Processing orbit {oid} size={len(edges)}")
        # construct candidate lists excluding used roots
        candid_raw = select_candidate_roots_by_compatibility(score_matrix, mapping, edges, meta, top_m=top_m, top_k=max(top_k, 24), adjacency_weight=1.0)
        # filter candidates to exclude used roots; if too small, fall back to raw candidates
        candid_filtered = []
        for lst in candid_raw:
            fl = [r for r in lst if r not in used_roots]
            if not fl:
                fl = [r for r in lst[:top_k]]
            candid_filtered.append(fl[:top_k])

        mapping_new, local_score = cp_sat_local_refine_with_candidates(mapping, edges, candid_filtered, time_limit=time_limit)
        global_before = compute_adjacency_score(mapping)
        global_after = compute_adjacency_score(mapping_new)
        print(f"Orbit {oid} global before={global_before} after={global_after}")
        if global_after > global_before:
            print("Adopting improved mapping for orbit", oid)
            mapping = mapping_new
            # update used_roots
            for e in edges:
                used_roots.add(tuple(mapping[e]))

    final_score = compute_adjacency_score(mapping)
    if write_artifact:
        out = Path("artifacts") / "edge_root_mapping_orbit_decomp_refined.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            json.dump({"initial_adj_score": initial_score, "final_adj_score": final_score}, f, indent=2, default=str)
        print("Wrote", out)

    try:
        plot_feature_embeddings(mapping, score_matrix, meta)
        plot_adj_preservation(mapping, meta)
    except Exception:
        pass

    return mapping, initial_score, final_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", type=float, nargs=3, default=[0.005, 0.0, 0.995])
    parser.add_argument("--use-orbit-features", action="store_true")
    parser.add_argument("--orbit-max-size", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--top-m", type=int, default=200)
    parser.add_argument("--time-limit", type=float, default=120)
    parser.add_argument("--no-write-artifact", action="store_true")
    args = parser.parse_args()

    weights = {"emb": args.weights[0], "geom": args.weights[1], "meta": args.weights[2]}
    mapping, init, final = run_orbit_decomposed_refine(
        weights=weights,
        use_orbit_features=args.use_orbit_features,
        orbit_max_size=args.orbit_max_size,
        top_k=args.top_k,
        top_m=args.top_m,
        time_limit=args.time_limit,
        write_artifact=not args.no_write_artifact,
    )
    print("Orbit-decomp refine complete: initial_adj=", init, "final_adj=", final)


if __name__ == "__main__":
    main()
