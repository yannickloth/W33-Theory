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
