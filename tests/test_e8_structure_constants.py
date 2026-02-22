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


def test_kind_level_fusion_and_mixed_cubic_selection_rules():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)

    # SU(3) simple roots used in this project.
    su3_alpha = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    su3_beta = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

    # Orbit index lookup.
    idx_orb = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    orbit_sizes = [len(o) for o in orbits]
    kinds = {}
    weights = {}
    for oi, orb in enumerate(orbits):
        sz = orbit_sizes[oi]
        if sz == 72:
            kinds[oi] = "E6"
        elif sz == 1:
            kinds[oi] = "A2"
        elif sz == 27:
            kinds[oi] = "MIX27"
        else:
            raise AssertionError(f"Unexpected orbit size: {sz}")
        r = roots[orb[0]]
        weights[oi] = (
            int(round(float(np.dot(r, su3_alpha)))),
            int(round(float(np.dot(r, su3_beta)))),
        )

    # Build fast integer-key lookup for root addition.
    keys = np.array(
        [[int(round(2 * float(x))) for x in roots[i]] for i in range(len(roots))],
        dtype=int,
    )
    root_index = {tuple(keys[i].tolist()): i for i in range(len(roots))}

    # Kind-level fusion table: oriented pairs (i,j) with i != j.
    kind_fusion = {}
    for i in range(len(roots)):
        ki = keys[i]
        oi = idx_orb[i]
        for j in range(len(roots)):
            if i == j:
                continue
            s = tuple((ki + keys[j]).tolist())
            k = root_index.get(s)
            if k is None:
                continue
            ok = idx_orb[k]
            a = kinds[oi]
            b = kinds[idx_orb[j]]
            c = kinds[ok]
            kind_fusion.setdefault(a, {}).setdefault(b, {}).setdefault(c, 0)
            kind_fusion[a][b][c] += 1

    assert kind_fusion["E6"]["E6"] == {"E6": 1440}
    assert kind_fusion["A2"]["A2"] == {"A2": 12}
    assert (
        kind_fusion.get("E6", {}).get("A2", {}) == {}
    )  # direct sum: no roots of the form E6 + A2
    assert kind_fusion.get("A2", {}).get("E6", {}) == {}
    assert kind_fusion["A2"]["MIX27"] == {"MIX27": 324}
    assert kind_fusion["MIX27"]["A2"] == {"MIX27": 324}
    assert kind_fusion["E6"]["MIX27"] == {"MIX27": 2592}
    assert kind_fusion["MIX27"]["E6"] == {"MIX27": 2592}
    assert kind_fusion["MIX27"]["MIX27"] == {"MIX27": 3240, "A2": 324, "E6": 2592}

    # Mixed cubic selection rule: α+β+γ=0 among MIX27 roots.
    mix_orb_indices = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    mix_indices = [i for i in range(len(roots)) if idx_orb[i] in mix_orb_indices]

    def rep(w):
        weights_3 = {(1, 0), (-1, 1), (0, -1)}
        weights_3bar = {(0, 1), (1, -1), (-1, 0)}
        if w in weights_3:
            return "3"
        if w in weights_3bar:
            return "3bar"
        return "?"

    triple_rep_types = {}
    triple_orbit_multisets = {}
    triple_wsum = {}

    for a_pos, i in enumerate(mix_indices):
        wi = weights[idx_orb[i]]
        ri = rep(wi)
        ki = keys[i]
        for j in mix_indices[a_pos:]:
            wj = weights[idx_orb[j]]
            rj = rep(wj)
            need = tuple((-(ki + keys[j])).tolist())
            k = root_index.get(need)
            if k is None or idx_orb[k] not in mix_orb_indices:
                continue
            wk = weights[idx_orb[k]]
            rk = rep(wk)

            wsum = (wi[0] + wj[0] + wk[0], wi[1] + wj[1] + wk[1])
            triple_wsum[wsum] = triple_wsum.get(wsum, 0) + 1

            rep_key = tuple(sorted((ri, rj, rk)))
            triple_rep_types[rep_key] = triple_rep_types.get(rep_key, 0) + 1

            orb_key = tuple(sorted((idx_orb[i], idx_orb[j], idx_orb[k])))
            triple_orbit_multisets[orb_key] = triple_orbit_multisets.get(orb_key, 0) + 1

    assert triple_wsum == {(0, 0): 1620}
    assert triple_rep_types == {("3", "3", "3"): 810, ("3bar", "3bar", "3bar"): 810}

    # Exactly one orbit-triple for 3 and one for 3bar (up to permutation).
    assert set(triple_orbit_multisets.values()) == {810}
    assert len(triple_orbit_multisets) == 2
