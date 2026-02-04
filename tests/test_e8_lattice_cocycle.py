from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_cocycle_is_antisymmetric_when_sum_is_root():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )
    cocycle = _load_module(
        repo_root / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle"
    )

    roots = cds.construct_e8_roots()

    def k2(r: np.ndarray) -> Tuple[int, ...]:
        return tuple(int(round(2 * float(x))) for x in r.tolist())

    root_index: Dict[Tuple[int, ...], int] = {
        k2(roots[i]): i for i in range(len(roots))
    }

    # Gather some pairs (α,β) with α+β a root.
    pairs = []
    ks = [k2(r) for r in roots]
    for _ in range(2000):
        i = random.randrange(len(roots))
        j = random.randrange(len(roots))
        if i == j:
            continue
        s = tuple(ks[i][t] + ks[j][t] for t in range(8))
        if s in root_index:
            pairs.append((ks[i], ks[j]))
        if len(pairs) >= 200:
            break

    assert len(pairs) >= 50
    for a, b in pairs:
        eps_ab = cocycle.epsilon_e8(a, b)
        eps_ba = cocycle.epsilon_e8(b, a)
        assert eps_ba == -eps_ab
