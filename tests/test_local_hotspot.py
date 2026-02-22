import importlib.util
import json
import sys

import numpy as np


def load_module():
    spec = importlib.util.spec_from_file_location(
        "local_hotspot", "scripts/local_hotspot_feasibility.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules[spec.name] = mod
    return mod


def test_candidates_nonempty():
    mod = load_module()
    X, edges = mod.compute_embedding_matrix()
    roots = mod.generate_scaled_e8_roots()
    E_mat = mod.build_edge_vectors(X, edges)
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(
        roots_arr.astype(float), axis=1, keepdims=True
    )
    K = 10
    cost = np.linalg.norm(E_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    candidates = {e: list(np.argsort(cost[e])[:K]) for e in range(len(edges))}
    # pick some hotspot edges that should exist
    assert 37 in candidates
    assert 38 in candidates
    assert len(candidates[37]) > 0
    assert len(candidates[38]) > 0


def test_offset_no_pairs_writes_empty(tmp_path, monkeypatch):
    # choose K small and offset larger than total pair count so no pairs remain
    mod = load_module()
    X, edges = mod.compute_embedding_matrix()
    roots = mod.generate_scaled_e8_roots()
    E_mat = mod.build_edge_vectors(X, edges)
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(
        roots_arr.astype(float), axis=1, keepdims=True
    )
    K = 6
    cost = np.linalg.norm(E_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    candidates = {e: list(np.argsort(cost[e])[:K]) for e in range(len(edges))}
    pairs_count = len(candidates[37]) * len(candidates[38])
    offset = pairs_count + 5

    checks = tmp_path / "checks"
    checks.mkdir()

    # run the script with a large offset and verify it writes an output file with empty tests
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONUNBUFFERED", "1")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/local_hotspot_feasibility.py",
            "--edges",
            "37",
            "38",
            "--k",
            str(K),
            "--offset",
            str(offset),
            "--time-limit",
            "1",
            "--log-dir",
            str(checks),
        ],
    )

    # import fresh module and run
    import importlib

    importlib.reload(mod)
    mod.main()

    out_files = list(
        checks.glob("PART_CVII_local_hotspot_feasibility_37_38_offset*_limit*_*.json")
    )
    assert out_files, "no output file written"
    j = json.loads(out_files[-1].read_text(encoding="utf-8"))
    assert j.get("tests") == []


def test_slice_pairs_helper():
    mod = load_module()
    pairs = [(1, 2, 3, 4) for _ in range(100)]
    out = mod.slice_pairs(pairs, offset=10, limit=5)
    assert len(out) == 5
    out2 = mod.slice_pairs(pairs, offset=200, limit=10)
    assert out2 == []
    out3 = mod.slice_pairs(pairs, offset=0, limit=5)
    assert len(out3) == 5
