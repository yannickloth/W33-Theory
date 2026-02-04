#!/usr/bin/env python3
"""
Verify W(E6) invariance of the 45-term E6 cubic sign tensor in the **canonical mixed-orbit gauge**,
including the correct Weyl action signs μ on root vectors.

We work with a fixed E6 simple reflection generator w = s_α realized by the Chevalley element n_α(1),
which acts on root vectors by:
  w(e_β) = μ_w(β) * e_{wβ},   μ_w(β) ∈ {±1}.

The cubic on the 27 is unique up to scale. In GF(2) bits, invariance for a generator w takes the form:
  d(p(t)) = d(t) ⊕ δ(i) ⊕ δ(j) ⊕ δ(k) ⊕ g_w
for every triad t = {i,j,k}, where:
  - p is the induced permutation of the 27 E6-ids under w (using one fixed 27-orbit in the SU(3)=3 triangle),
  - δ(i) are the induced sign bits on the chosen 27-basis after applying the canonical phase gauge,
  - g_w is a single global bit (overall scaling ambiguity of the invariant cubic).

This tool computes p, δ, and solves g_w per generator, reporting any failures.

Writes:
  artifacts/e6_cubic_invariance_canonical_gauge.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

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


solver = _load_module(
    ROOT / "tools" / "solve_canonical_su3_gauge_and_cubic.py",
    "solve_canonical_su3_gauge_and_cubic",
)
cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")
we6 = _load_module(ROOT / "tools" / "weyl_e6_action.py", "weyl_e6_action")


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def bit(sgn: int) -> int:
    if sgn not in (-1, 1):
        raise ValueError("Expected ±1")
    return 1 if sgn == -1 else 0


def bit_to_sign(b: int) -> int:
    if b not in (0, 1):
        raise ValueError("Expected bit 0/1")
    return -1 if b else 1


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


def lie_bracket_coeff(
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


def root_string_pq(
    beta_k2: Tuple[int, ...],
    alpha_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> Tuple[int, int]:
    p = 0
    while True:
        cand = tuple(beta_k2[i] - (p + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            p += 1
            continue
        break
    q = 0
    while True:
        cand = tuple(beta_k2[i] + (q + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            q += 1
            continue
        break
    return p, q


def mat_eye(n: int) -> List[List[Fraction]]:
    return [
        [Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)
    ]


def mat_mul(A: List[List[Fraction]], B: List[List[Fraction]]) -> List[List[Fraction]]:
    n = len(A)
    m = len(B[0])
    k = len(B)
    out = [[Fraction(0) for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = Fraction(0)
            for t in range(k):
                s += A[i][t] * B[t][j]
            out[i][j] = s
    return out


def mat_pow(A: List[List[Fraction]], e: int) -> List[List[Fraction]]:
    if e == 0:
        return mat_eye(len(A))
    out = mat_eye(len(A))
    cur = A
    ee = e
    while ee:
        if ee & 1:
            out = mat_mul(cur, out)
        ee >>= 1
        if ee:
            cur = mat_mul(cur, cur)
    return out


def exp_nilpotent(M: List[List[Fraction]]) -> List[List[Fraction]]:
    n = len(M)
    out = mat_eye(n)
    fact = 1
    for k in range(1, n + 1):
        fact *= k
        P = mat_pow(M, k)
        for i in range(n):
            for j in range(n):
                out[i][j] += P[i][j] / fact
    return out


def apply_mat(M: List[List[Fraction]], v: List[Fraction]) -> List[Fraction]:
    n = len(M)
    out = [Fraction(0) for _ in range(n)]
    for i in range(n):
        s = Fraction(0)
        for j in range(n):
            s += M[i][j] * v[j]
        out[i] = s
    return out


def weyl_mu_on_root(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> Tuple[Tuple[int, ...], int]:
    """
    For w = s_α realized by n_α(1), compute:
      n_α(1) e_β n_α(1)^{-1} = μ * e_{wβ}
    returning (wβ, μ).
    """
    p, q = root_string_pq(beta_k2, alpha_k2, root_index)
    string = [
        tuple(beta_k2[i] + s * alpha_k2[i] for i in range(8)) for s in range(-p, q + 1)
    ]
    pos = {r: idx for idx, r in enumerate(string)}
    n = len(string)

    minus_alpha_k2 = tuple(-x for x in alpha_k2)

    E = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    F = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for r, gamma in enumerate(string):
        gp = tuple(gamma[i] + alpha_k2[i] for i in range(8))
        if gp in pos:
            c = lie_bracket_coeff(alpha_k2, gamma, root_index)
            E[pos[gp]][r] = Fraction(c)
        gm = tuple(gamma[i] - alpha_k2[i] for i in range(8))
        if gm in pos:
            c = lie_bracket_coeff(minus_alpha_k2, gamma, root_index)
            F[pos[gm]][r] = Fraction(c)

    expE = exp_nilpotent(E)
    expFneg = exp_nilpotent([[-x for x in row] for row in F])
    w = mat_mul(expE, mat_mul(expFneg, expE))

    v0 = [Fraction(0) for _ in range(n)]
    v0[p] = Fraction(1)
    v1 = apply_mat(w, v0)

    nz = [(i, v) for i, v in enumerate(v1) if v != 0]
    if len(nz) != 1:
        raise RuntimeError(f"Unexpected Weyl action support size: {nz}")
    idx, coeff = nz[0]
    wbeta = string[idx]
    if coeff not in (Fraction(1), Fraction(-1)):
        raise RuntimeError(f"Unexpected Weyl coefficient: {coeff}")
    mu = 1 if coeff == 1 else -1
    return wbeta, mu


@dataclass(frozen=True)
class CheckResult:
    gen_name: str
    failures: int
    inferred_global_bit: int | None


def main() -> None:
    # Refresh canonical solution.
    solver.main()
    sol_path = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    sol = json.loads(sol_path.read_text(encoding="utf-8"))
    if not sol.get("counts", {}).get("solvable", False):
        raise RuntimeError("canonical_su3_gauge_and_cubic.json is not solvable")

    solution = sol["solution"]
    phase_bits: Dict[str, List[int]] = solution["phase_bits"]
    d_bits = {
        tuple(int(x) for x in t["triple"]): (1 if int(t["sign"]) == -1 else 0)
        for t in solution["d_triples"]
    }

    # Build E8 roots and indices.
    roots = cds.construct_e8_roots()
    root_index = {k2(roots[i]): i for i in range(len(roots))}

    # Mixed orbit representative: use the first orbit listed in orbits_3 from the solver artifact.
    oi_ref = int(sol["orbits_3"][0]["orbit"])
    e6_keys_27 = [tuple(int(x) for x in k) for k in sol["e6_keys_27_k2"]]
    if len(e6_keys_27) != 27:
        raise RuntimeError("Missing e6_keys_27_k2")

    # Map (orbit,e6id)->root index (on the fly, stable inside this process).
    orbits = cds.compute_we6_orbits(roots)
    if oi_ref >= len(orbits) or len(orbits[oi_ref]) != 27:
        raise RuntimeError("Reference mixed orbit not found or not size 27")

    # Root->e6id mapping for the reference orbit (uses solver's key ordering).
    key_to_id = {k: i for i, k in enumerate(e6_keys_27)}
    orb_root_by_id = [-1] * 27
    for ridx in orbits[oi_ref]:
        kk = solver.e6_key(roots[ridx])
        if kk not in key_to_id:
            raise RuntimeError("Reference orbit root has E6 key not in solver list")
        orb_root_by_id[key_to_id[kk]] = ridx
    if any(v == -1 for v in orb_root_by_id):
        raise RuntimeError("Failed to build (orbit,e6id)->root table")

    # E6 simple roots in the repo's embedding.
    e6_simple = we6.get_e6_simple_roots()
    e6_simple_k2 = [k2(np.array(v, dtype=float)) for v in e6_simple]
    gen_names = [f"s{i+1}" for i in range(len(e6_simple_k2))]

    results: List[CheckResult] = []
    failures_by_gen: Dict[str, List[Dict[str, object]]] = {}

    for gen_name, alpha_k2 in zip(gen_names, e6_simple_k2):
        # Compute induced permutation p and sign bits δ on the 27 basis in canonical gauge.
        p = [-1] * 27
        delta = [0] * 27
        for i in range(27):
            ridx = orb_root_by_id[i]
            beta = k2(roots[ridx])
            wbeta, mu = weyl_mu_on_root(alpha_k2, beta, root_index)
            tidx = root_index.get(wbeta)
            if tidx is None:
                raise RuntimeError("weyl_mu_on_root produced a non-root")
            kk = solver.e6_key(roots[tidx])
            j = key_to_id.get(kk)
            if j is None:
                raise RuntimeError("Image root not in 27 key set")
            p[i] = j
            delta[i] = (
                phase_bits[str(oi_ref)][i] ^ phase_bits[str(oi_ref)][j] ^ bit(mu)
            ) & 1

        if any(x < 0 for x in p):
            raise RuntimeError("Bad induced permutation")
        if len(set(p)) != 27:
            raise RuntimeError("Induced map is not a permutation")

        # Check invariance on all 45 triads, solving for g_w.
        g_bit: int | None = None
        failures = 0
        for triad, d_t in d_bits.items():
            i, j, k = triad
            tp = tuple(sorted((p[i], p[j], p[k])))
            d_tp = d_bits.get(tp)
            if d_tp is None:
                raise RuntimeError("Triad image not in triad set")
            val = (d_tp ^ d_t ^ delta[i] ^ delta[j] ^ delta[k]) & 1
            if g_bit is None:
                g_bit = val
            elif g_bit != val:
                failures += 1
                if failures <= 25:
                    failures_by_gen.setdefault(gen_name, []).append(
                        {
                            "triad": list(triad),
                            "image": list(tp),
                            "lhs_bit": int(val),
                            "expected_g": int(g_bit),
                        }
                    )

        results.append(
            CheckResult(gen_name=gen_name, failures=failures, inferred_global_bit=g_bit)
        )

    out = {
        "status": "ok",
        "counts": {
            "generators": len(results),
            "failures_total": int(sum(r.failures for r in results)),
        },
        "results": [
            {
                "gen": r.gen_name,
                "failures": int(r.failures),
                "global_bit": (
                    None
                    if r.inferred_global_bit is None
                    else int(r.inferred_global_bit)
                ),
            }
            for r in results
        ],
        "failures_by_generator": failures_by_gen,
    }
    out_path = ROOT / "artifacts" / "e6_cubic_invariance_canonical_gauge.json"
    out_path.write_text(json.dumps(out, indent=2, default=int), encoding="utf-8")
    print(
        "PASS" if out["counts"]["failures_total"] == 0 else "FAIL",
        "E6 cubic invariance in canonical gauge",
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
