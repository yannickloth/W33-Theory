from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_e8_e6_a2_orbit_and_ladder_structure():
    repo_root = Path(__file__).resolve().parents[1]

    compute_double_sixes = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )
    fusion = _load_module(repo_root / "tools" / "e8_e6_a2_fusion.py", "e8_e6_a2_fusion")

    roots = compute_double_sixes.construct_e8_roots()
    orbits = compute_double_sixes.compute_we6_orbits(roots)

    # W(E6) orbit structure: 240 = 72 + 6×27 + 6×1
    sizes = sorted((len(o) for o in orbits), reverse=True)
    assert sizes == [72] + [27] * 6 + [1] * 6

    # A2 simple roots form Cartan matrix of type A2
    alpha = fusion.SU3_ALPHA
    beta = fusion.SU3_BETA
    assert float(np.dot(alpha, alpha)) == 2.0
    assert float(np.dot(beta, beta)) == 2.0
    assert float(np.dot(alpha, beta)) == -1.0

    # Orbit labels via (d1,d2) = (r·alpha, r·beta)
    def w(idx: int) -> tuple[int, int]:
        r = roots[idx]
        return (int(round(float(np.dot(r, alpha)))), int(round(float(np.dot(r, beta)))))

    orbit_weights = [w(orb[0]) for orb in orbits]
    mix_weights = sorted(
        {orbit_weights[i] for i, orb in enumerate(orbits) if len(orb) == 27}
    )
    a2_weights = sorted(
        {orbit_weights[i] for i, orb in enumerate(orbits) if len(orb) == 1}
    )

    assert mix_weights == [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]
    assert a2_weights == [(-2, 1), (-1, -1), (-1, 2), (1, -2), (1, 1), (2, -1)]

    # Ladder action: each A2 root moves between MIX27 orbits in 2 clean 27-to-27 maps,
    # and the orbit-weight addition is linear: w(dst) = w(src) + w(delta).
    root_to_index = {fusion.root_key(roots[i]): i for i in range(len(roots))}

    idx_orb = {}
    for oi, orb in enumerate(orbits):
        for vi in orb:
            idx_orb[vi] = oi

    mix_orbits = [oi for oi, orb in enumerate(orbits) if len(orb) == 27]
    a2_orbits = [oi for oi, orb in enumerate(orbits) if len(orb) == 1]

    for a2_oi in a2_orbits:
        delta_idx = orbits[a2_oi][0]
        delta_key = fusion.root_key(roots[delta_idx])
        delta_w = orbit_weights[a2_oi]

        transitions = {}
        for src_oi in mix_orbits:
            src_w = orbit_weights[src_oi]
            for r_idx in orbits[src_oi]:
                s = tuple(
                    delta_key[t] + fusion.root_key(roots[r_idx])[t] for t in range(8)
                )
                k = root_to_index.get(s)
                if k is None:
                    continue
                dst_oi = idx_orb[k]
                transitions[(src_oi, dst_oi)] = transitions.get((src_oi, dst_oi), 0) + 1
                assert orbit_weights[dst_oi] == (
                    src_w[0] + delta_w[0],
                    src_w[1] + delta_w[1],
                )

        # Exactly two nonzero orbit-to-orbit transitions, each with multiplicity 27.
        assert sorted(transitions.values()) == [27, 27]
