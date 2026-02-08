import importlib.util
import numpy as np


def load_module():
    spec = importlib.util.spec_from_file_location('local_hotspot', 'scripts/local_hotspot_feasibility.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_candidates_nonempty():
    mod = load_module()
    X, edges = mod.compute_embedding_matrix()
    roots = mod.generate_scaled_e8_roots()
    E_mat = mod.build_edge_vectors(X, edges)
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)
    K = 10
    cost = np.linalg.norm(E_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    candidates = {e: list(np.argsort(cost[e])[:K]) for e in range(len(edges))}
    # pick some hotspot edges that should exist
    assert 37 in candidates
    assert 38 in candidates
    assert len(candidates[37]) > 0
    assert len(candidates[38]) > 0
