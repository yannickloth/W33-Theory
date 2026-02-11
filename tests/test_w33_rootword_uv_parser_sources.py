import json
from pathlib import Path

from tools.w33_rootword_uv_parser import W33RootwordParser


def test_we6_orbit_source_present():
    p = W33RootwordParser()
    # vector from artifacts/edge_to_e8_root_we6_orbits.json for key "(4, 7)" scaled by 2 -> (-2,0,0,0,0,-2,0,0)
    vec = (-2, 0, 0, 0, 0, -2, 0, 0)
    assert vec in p.vec_to_edges_map
    entries = p.vec_to_edges_map[vec]
    # expect at least one candidate edge corresponding to (5, 8) (1-based)
    assert any(e == (5, 8) for (e, tag) in entries)


def test_e8_root_to_w33_edge_source_present():
    p = W33RootwordParser()
    # check a simple root key '[1, 0, 0, 0, 0, 0, 0, 0]' present from artifacts/e8_root_to_w33_edge.json
    vec = (1, 0, 0, 0, 0, 0, 0, 0)
    assert vec in p.vec_to_edges_map
    entries = p.vec_to_edges_map[vec]
    # expect at least one candidate edge corresponding to (1, 2) (1-based)
    assert any(e == (1, 2) for (e, tag) in entries)
