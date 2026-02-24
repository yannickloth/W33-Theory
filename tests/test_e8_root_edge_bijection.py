import json
from itertools import product
from pathlib import Path

import pytest


# use the shared geometry builder from the main script rather than
# duplicating logic here; this ensures consistency between the test and
# the code under test.
from scripts.w33_algebra_qca import build_w33_geometry

def build_w33_edges():
    _, edges, *_ = build_w33_geometry()
    return {tuple(sorted(e)) for e in edges}


def test_e8_root_to_w33_edge_bijection():
    p = Path("artifacts_archive/e8_root_to_w33_edge.json")
    if not p.exists():
        pytest.skip(
            "e8_root_to_w33_edge.json not found — run tools/sage_e8_root_edge_bijection.py"
        )

    data = json.loads(p.read_text(encoding="utf-8"))

    root_to_edge = data.get("root_to_edge", {})
    assert len(root_to_edge) == 240

    edges = set()
    for edge in root_to_edge.values():
        assert isinstance(edge, list)
        assert len(edge) == 2
        a, b = edge
        assert a != b
        edges.add(tuple(sorted((a, b))))

    assert len(edges) == 240

    w33_edges = build_w33_edges()
    assert edges == w33_edges

    orbit_map = data.get("orbit_to_w33_vertex", {})
    assert len(orbit_map) == 40

    w33_vertices = data.get("w33_vertices", [])
    assert len(w33_vertices) == 40
