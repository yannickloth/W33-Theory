from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT_PATHS = [
    "scripts/analyze_infeasible_blocks.py",
    "scripts/analyze_particle_group_adjacency.py",
    "scripts/apply_local_patch.py",
    "scripts/attempt_backtrack_pruned.py",
    "scripts/auto_post_sweep.py",
    "scripts/auto_repair_daemon.py",
    "scripts/backtrack_candidate_search.py",
    "scripts/build_manual_top_gap_seed.py",
    "scripts/check_forbid_pairs_bruteforce.py",
    "scripts/check_seed_consistency.py",
    "scripts/cluster_neighbor_vectors.py",
    "scripts/compute_graph_automorphism_orbits.py",
    "scripts/convert_edge_to_pos.py",
    "scripts/e8_obstruction_analysis.py",
    "scripts/local_repair_matching.py",
    "scripts/partial_to_seed.py",
    "scripts/run_seed_sweep.py",
    "scripts/scan_grid_artifacts.py",
    "scripts/seed_from_z3_candidate.py",
    "scripts/seed_top_gap_edges.py",
    "scripts/slice_seed.py",
    "scripts/solve_e8_embedding_cpsat.py",
    "scripts/solve_e8_embedding_cpsat_symmetry_pruned.py",
    "scripts/w33_commutant_split.py",
    "scripts/w33_complex_type_check.py",
    "scripts/w33_full_decomposition.py",
    "scripts/w33_h1_decomposition.py",
    "scripts/w33_hodge.py",
    "scripts/w33_representation_theory.py",
    "scripts/w33_split_90.py",
    "scripts/wl_refinement.py",
    "tools/toe_coupling_atlas_sweep.py",
]


def test_json_safe_touched_scripts_compile() -> None:
    for rel in SCRIPT_PATHS:
        path = ROOT / rel
        assert path.exists(), f"Missing script: {rel}"
        py_compile.compile(str(path), doraise=True)
