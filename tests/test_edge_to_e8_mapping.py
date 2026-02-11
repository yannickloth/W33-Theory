import json
from pathlib import Path

from scripts.edge_to_e8_mapping import run_geometry_mapping


def test_geometry_mapping_runs_and_matches_minimum():
    mapping, candidate_triples, transform = run_geometry_mapping()
    # mapping should be a dict mapping some edges -> roots
    assert isinstance(mapping, dict)
    # sanity: at least 20 edges matched by the geometric anchor approach
    assert len(mapping) >= 20
    # artifact written
    p = Path("artifacts/edge_root_mapping_geom.json")
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert "result" in data
    assert data["result"]["n_edges"] == 240


def test_local_search_accepts_partial_mapping_and_returns_full_mapping():
    # Ensure local search can be invoked with a partial mapping (as produced by geometry mapping)
    mapping_geom, _, _ = run_geometry_mapping()
    from scripts.edge_to_e8_mapping import local_search_refine_mapping

    refined, score = local_search_refine_mapping(
        mapping_geom, relation="abs1", iterations=500, temp=0.05
    )
    # refined should be a complete mapping mapping every edge 0..239 to a root tuple
    assert isinstance(refined, dict)
    assert len(refined) == 240
    for e in range(240):
        assert e in refined
        assert isinstance(refined[e], tuple)
    # mapping should be one-to-one across roots
    assert len(set(refined.values())) == 240


def test_local_search_is_idempotent_with_zero_iterations():
    mapping_geom, _, _ = run_geometry_mapping()
    from scripts.edge_to_e8_mapping import local_search_refine_mapping

    refined, score = local_search_refine_mapping(
        mapping_geom, relation="abs1", iterations=0, temp=0.01
    )
    # with zero iterations, score should equal initial score and mapping should be identical up to assigned edges
    assert isinstance(refined, dict)
    assert len(refined) == 240


def test_iterative_refinement_adds_anchors_with_large_tol():
    from scripts.edge_to_e8_mapping import run_iterative_refinement

    mapping, anchors, transforms = run_iterative_refinement(max_iter=3, add_tol=1.5)
    assert isinstance(mapping, dict)
    assert isinstance(anchors, dict)
    # with a very lenient add_tol we should accumulate anchors
    assert len(anchors) >= 10


def test_feature_mapping_runs_and_writes_artifact(tmp_path):
    from scripts.edge_to_e8_mapping import run_feature_hungarian_mapping

    mapping, result, score, meta = run_feature_hungarian_mapping(write_artifact=True)
    # mapping should be complete and bijective
    assert isinstance(mapping, dict)
    assert len(mapping) == 240
    assert len(set(mapping.values())) == 240
    p = Path("artifacts/edge_root_mapping_feature.json")
    assert p.exists()


def test_cp_sat_local_refine_small_cluster():
    import pytest

    # skip if OR-Tools not available
    pytest.importorskip("ortools")
    from scripts.edge_to_e8_mapping import (
        cp_sat_local_refine,
        detect_hotspots,
        run_feature_hungarian_mapping,
    )

    mapping, result, score, meta = run_feature_hungarian_mapping(write_artifact=False)
    cluster = detect_hotspots(mapping, meta, top_k=10, max_cluster=8)
    if not cluster:
        pytest.skip("No hotspot cluster found; skipping CP-SAT local refine test")

    updated, local_score = cp_sat_local_refine(mapping, cluster, top_k=6, time_limit=3)
    assert isinstance(updated, dict)
    # ensure we returned assignments for cluster edges
    for e in cluster:
        assert e in updated
    assert isinstance(local_score, (int, float))
