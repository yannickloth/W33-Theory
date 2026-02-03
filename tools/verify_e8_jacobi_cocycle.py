#!/usr/bin/env python3
"""
Stress-test Jacobi identity for the cocycle-derived E8 Chevalley bracket.

We define root-space brackets by:
  if α+β is a root, [e_α, e_β] = N_{α,β} e_{α+β}, else 0,
with N_{α,β} = ε(α,β) * |N_{α,β}|,
and |N_{α,β}| = p+1 from the root-string length on the negative side.

This is a necessary sanity check before trusting derived Weyl-action signs μ.

Output:
  artifacts/e8_jacobi_cocycle_check.json
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def cheva_abs_N(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    p = 0
    while True:
        cand = tuple(beta_k2[i] - (p + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            p += 1
            continue
        break
    return p + 1


def N(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    s = tuple(alpha_k2[i] + beta_k2[i] for i in range(8))
    if s not in root_index:
        return 0
    return int(
        cocycle.epsilon_e8(alpha_k2, beta_k2)
        * cheva_abs_N(alpha_k2, beta_k2, root_index)
    )


def main() -> None:
    rng = random.Random(0)
    roots = cds.construct_e8_roots()
    keys = [k2(r) for r in roots]
    root_index = {keys[i]: i for i in range(len(keys))}

    # Sample triples with some chance of nonzero Jacobi.
    trials = 20000
    checked = 0
    failures = 0
    failure_examples = []
    nz_hist = Counter()

    for _ in range(trials):
        a = rng.randrange(len(keys))
        b = rng.randrange(len(keys))
        c = rng.randrange(len(keys))
        if a == b or b == c or a == c:
            continue
        alpha = keys[a]
        beta = keys[b]
        gamma = keys[c]

        # Only bother if at least two inner brackets can be nonzero.
        ab = tuple(alpha[i] + beta[i] for i in range(8))
        bg = tuple(beta[i] + gamma[i] for i in range(8))
        ga = tuple(gamma[i] + alpha[i] for i in range(8))
        inner = int(ab in root_index) + int(bg in root_index) + int(ga in root_index)
        if inner < 2:
            continue

        def bracket(x, y):
            s = tuple(x[i] + y[i] for i in range(8))
            nxy = N(x, y, root_index)
            if nxy == 0:
                return None
            return s, nxy

        # Compute J = [a,[b,c]] + [b,[c,a]] + [c,[a,b]]
        J: Dict[Tuple[int, ...], int] = {}

        bc = bracket(beta, gamma)
        if bc is not None:
            s, nbc = bc
            a_s = bracket(alpha, s)
            if a_s is not None:
                t, nat = a_s
                J[t] = J.get(t, 0) + nbc * nat

        ca = bracket(gamma, alpha)
        if ca is not None:
            s, nca = ca
            b_s = bracket(beta, s)
            if b_s is not None:
                t, nbt = b_s
                J[t] = J.get(t, 0) + nca * nbt

        abp = bracket(alpha, beta)
        if abp is not None:
            s, nab = abp
            c_s = bracket(gamma, s)
            if c_s is not None:
                t, nct = c_s
                J[t] = J.get(t, 0) + nab * nct

        if not J:
            continue
        checked += 1
        nz = sum(1 for v in J.values() if v != 0)
        nz_hist[nz] += 1
        if nz != 0:
            failures += 1
            if len(failure_examples) < 5:
                failure_examples.append(
                    {
                        "alpha": list(alpha),
                        "beta": list(beta),
                        "gamma": list(gamma),
                        "J_terms": [
                            {"root": list(k), "coeff": int(v)}
                            for k, v in J.items()
                            if v != 0
                        ],
                    }
                )

    out = {
        "status": "ok",
        "trials": trials,
        "checked": checked,
        "failures": failures,
        "nz_hist": {str(k): int(v) for k, v in nz_hist.items()},
        "failure_examples": failure_examples,
    }
    out_path = ROOT / "artifacts" / "e8_jacobi_cocycle_check.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Checked", checked, "triples; failures", failures)
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
