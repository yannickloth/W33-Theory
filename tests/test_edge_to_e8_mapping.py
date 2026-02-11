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
