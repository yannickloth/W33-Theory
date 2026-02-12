import json
from pathlib import Path

import pytest

from tools import construct_w33_e8_bijection as bij


def test_construct_w33_e8_bijection_creates_artifact(tmp_path):
    # run the construction routine (fast, deterministic)
    vertices, edges, adjacency, e8_roots = bij.main()

    # basic structural checks
    assert len(vertices) == 40
    assert len(edges) == 240
    assert len(e8_roots) == 240

    # artifact file should exist
    p = Path("w33_e8_bijection_data.json")
    assert p.exists(), "artifact w33_e8_bijection_data.json not created"

    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("w33_vertices")
    assert data.get("w33_edges")
    assert data.get("e8_roots")

    # counts in artifact
    assert len(data["w33_vertices"]) == 40
    assert len(data["w33_edges"]) == 240
    assert len(data["e8_roots"]) == 240
