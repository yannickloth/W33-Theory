from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_e6_cubic_sign_gauge_linear_system_is_consistent():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )
    cocycle = _load_module(
        repo_root / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle"
    )

    su3_alpha = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    su3_beta = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    def k2(r: np.ndarray) -> Tuple[int, ...]:
        return tuple(int(round(2 * float(x))) for x in r.tolist())

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    def su3_weight(r: np.ndarray) -> Tuple[int, int]:
        return (
            int(round(float(np.dot(r, su3_alpha)))),
            int(round(float(np.dot(r, su3_beta)))),
        )

    def proj_to_su3(r: np.ndarray) -> np.ndarray:
        A = np.stack([su3_alpha, su3_beta], axis=1)
        G = A.T @ A
        coeffs = np.linalg.solve(G, A.T @ r)
        return A @ coeffs

    def e6_key(r: np.ndarray) -> Tuple[int, ...]:
        re6 = r - proj_to_su3(r)
        return tuple(int(round(2 * float(x))) for x in re6.tolist())

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3
    oa, ob, oc = color_orbs

    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Collect ordered couplings with raw cocycle sign.
    couplings: List[Tuple[int, int, int, int]] = []
    for a_root in orbits[oa]:
        ka = k2(roots[a_root])
        i = root_to_e6id[a_root]
        for b_root in orbits[ob]:
            kb = k2(roots[b_root])
            j = root_to_e6id[b_root]
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c_root = root_index.get(need)
            if c_root is None or idx_orb[c_root] != oc:
                continue
            k = root_to_e6id[c_root]
            raw = cocycle.epsilon_e8(ka, kb)
            couplings.append((i, j, k, raw))

    assert len(couplings) == 270
    triples = sorted({tuple(sorted((i, j, k))) for (i, j, k, _) in couplings})
    assert len(triples) == 45
    triple_index = {t: idx for idx, t in enumerate(triples)}

    # Solve sigma/d system (126 vars, 270 eqs) via simple elimination.
    n_sigma = 81
    n_d = 45
    nvars = n_sigma + n_d

    def var_sigma(color: int, e6id: int) -> int:
        return color * 27 + e6id

    def var_d(t: Tuple[int, int, int]) -> int:
        return n_sigma + triple_index[t]

    rows: List[Tuple[int, int]] = []
    for i, j, k, raw_sign in couplings:
        t = tuple(sorted((i, j, k)))
        mask = 0
        mask ^= 1 << var_sigma(0, i)
        mask ^= 1 << var_sigma(1, j)
        mask ^= 1 << var_sigma(2, k)
        mask ^= 1 << var_d(t)
        rhs = cocycle.sign_to_bit(raw_sign)
        rows.append((mask, rhs))

    pivots: Dict[int, Tuple[int, int]] = {}
    for mask, rhs in rows:
        m = mask
        r = rhs
        while m:
            p = m.bit_length() - 1
            if p in pivots:
                pm, pr = pivots[p]
                m ^= pm
                r ^= pr
            else:
                pivots[p] = (m, r)
                break
        if m == 0:
            assert r == 0
