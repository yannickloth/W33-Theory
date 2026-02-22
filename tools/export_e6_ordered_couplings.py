"""
Export ordered couplings (i,j,k, raw_sign) in heis labeling to artifacts/e6_ordered_couplings.json
This reuses the root/cocycle code from the repo (compute_double_sixes and e8_lattice_cocycle).
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Ensure the module is present in sys.modules during execution. This avoids
    # dataclass and relative-import issues when the module inspects its
    # __module__ during class creation.
    import sys as _sys

    _sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception:
        # Fallback: if dynamic load fails, try a regular import (requires the
        # repo root to be on sys.path). Remove the placeholder module first.
        try:
            if name in _sys.modules and _sys.modules[name] is module:
                del _sys.modules[name]
        except Exception:
            pass
        import importlib as _importlib

        return _importlib.import_module(name)


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")

import numpy as np

# SU(3) projection basis used for color decomposition (same choice as in the sign-gauge solver)
SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

# local helpers mirroring the solve_e6_cubic_sign_gauge logic


def k2(r: np.ndarray):
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def su3_weight(r: np.ndarray):
    return (
        int(round(float(np.dot(r, SU3_ALPHA)))),
        int(round(float(np.dot(r, SU3_BETA)))),
    )


def proj_to_su3(r: np.ndarray) -> np.ndarray:
    A = np.stack([SU3_ALPHA, SU3_BETA], axis=1)
    G = A.T @ A
    coeffs = np.linalg.solve(G, A.T @ r)
    return A @ coeffs


def e6_key(r: np.ndarray):
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


# reconstruct same orbit labeling used in solve_e6_cubic_sign_gauge.py
roots = cds.construct_e8_roots()
orbits = cds.compute_we6_orbits(roots)
# get color orbits (the three 27-orbits with su3 weights matching)
orbit_sizes = [len(o) for o in orbits]
idx_orb = {v: oi for oi, orb in enumerate(orbits) for v in orb}
mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
weights_3 = {(1, 0), (-1, 1), (0, -1)}
color_orbs = sorted(
    [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
)
oa, ob, oc = color_orbs

# build e6 groups mapping and root_to_e6id
root_to_e6id = {}
e6_groups = {}
for oi in color_orbs:
    for r_idx in orbits[oi]:
        k = e6_key(roots[r_idx])
        if k not in e6_groups:
            e6_groups[k] = len(e6_groups)
        root_to_e6id[r_idx] = e6_groups[k]

# Build color_root_by_e6id
e6id_to_roots = [[] for _ in range(3)]
for color, oi in enumerate(color_orbs):
    for r_idx in orbits[oi]:
        e6id = root_to_e6id[r_idx]
        e6id_to_roots[color].append((e6id, r_idx))
    # ensure full

# build a lookup from doubled-coordinate key to root index
root_index = {k2(roots[i]): i for i in range(len(roots))}

# Now enumerate ordered couplings as in solve script
couplings = []
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

# couplings should be 270
print("couplings count", len(couplings))
# write to artifact
(Path(ROOT) / "artifacts").mkdir(exist_ok=True)
with open(
    Path(ROOT) / "artifacts" / "e6_ordered_couplings.json", "w", encoding="utf-8"
) as f:
    json.dump(
        [{"i": i, "j": j, "k": k, "raw": int(raw)} for (i, j, k, raw) in couplings],
        f,
        indent=2,
    )
print("Wrote artifacts/e6_ordered_couplings.json")
