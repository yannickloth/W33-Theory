#!/usr/bin/env python3
"""
Solve a W(E6)-equivariant sign gauge for the E6 cubic tensor using *explicit* Weyl action signs.

Key point:
  In a concrete Chevalley/cocycle basis for E8 root vectors, a Weyl element does not act as a
  pure permutation on root vectors; it acts as
      w(e_β) = μ_w(β) * e_{wβ},   with μ_w(β) ∈ {±1}.

Earlier attempts that ignored μ_w (or tried to fit it implicitly) can make the cubic tensor
look non-invariant. Here we compute μ_w exactly *inside each α-string* using the cocycle-derived
structure constants and the Chevalley formula:
  n_α(1) = exp(ad e_α) exp(ad e_{-α} * (-1)) exp(ad e_α),
and then solve for a gauge where the extracted E6 cubic signs are W(E6)-equivariant.

Unknowns (GF(2) bits):
  - phase_c(i): 3*27 basis flips for the (27,3) sector (colors c=0,1,2)
  - d_t: 45 cubic tensor signs on unordered triads t
  - g_gen: 6 global bits (overall sign per generator; allowed since the invariant cubic is unique up to scale)

Constraints:
  (A) 270 coupling equations from E8 mixed triples (colors fixed by the 3 SU(3)=3 orbits):
        phase_0(i) + phase_1(j) + phase_2(k) + d_{ {i,j,k} } = raw_sign(i,j,k)
      where raw_sign is the cocycle ε(α,β) for the ordered triple.

  (B) Weyl equivariance for each E6 simple reflection generator gen with permutation p and μ-signs:
        d_{p(t)} = d_t
                  + [phase_0(i)+phase_0(p(i)) + μ_0(i)]
                  + [phase_1(j)+phase_1(p(j)) + μ_1(j)]
                  + [phase_2(k)+phase_2(p(k)) + μ_2(k)]
                  + g_gen
      for each triad t=(i,j,k). Here μ_c(i) is the bit of μ_gen(beta(c,i)).

Output:
  artifacts/e6_cubic_weyl_equivariant_signs_with_mu.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
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


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")

SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def sign_to_bit(s: int) -> int:
    if s not in (-1, 1):
        raise ValueError("Expected ±1 sign")
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    if b not in (0, 1):
        raise ValueError("Expected bit 0/1")
    return -1 if b else 1


def su3_weight(r: np.ndarray) -> Tuple[int, int]:
    return (
        int(round(float(np.dot(r, SU3_ALPHA)))),
        int(round(float(np.dot(r, SU3_BETA)))),
    )


def proj_to_su3(r: np.ndarray) -> np.ndarray:
    A = np.stack([SU3_ALPHA, SU3_BETA], axis=1)
    G = A.T @ A
    coeffs = np.linalg.solve(G, A.T @ r)
    return A @ coeffs


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


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
    absN = cheva_abs_N(alpha_k2, beta_k2, root_index)
    eps = cocycle.epsilon_e8(alpha_k2, beta_k2)
    return int(eps * absN)


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


def mat_eye(n: int) -> List[List[Fraction]]:
    return [
        [Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)
    ]


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
    For the simple reflection s_α (realized by n_α(1)), compute:
      n_α(1) e_β n_α(1)^{-1} = μ * e_{s_α β}
    returning (s_α β, μ).
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
    # middle factor uses parameter -1:
    Fneg = [[-x for x in row] for row in F]
    expFneg = exp_nilpotent(Fneg)
    w = mat_mul(expE, mat_mul(expFneg, expE))

    v0 = [Fraction(0) for _ in range(n)]
    v0[p] = Fraction(1)
    v1 = apply_mat(w, v0)

    nz = [(i, v) for i, v in enumerate(v1) if v != 0]
    if len(nz) != 1:
        raise RuntimeError(f"Unexpected Weyl action support size: {nz}")
    idx, coeff = nz[0]
    if coeff not in (Fraction(1), Fraction(-1)):
        raise RuntimeError(f"Unexpected Weyl action coefficient: {coeff}")
    beta_prime = string[idx]
    mu = 1 if coeff == Fraction(1) else -1
    return beta_prime, mu


@dataclass(frozen=True)
class LinearSystemGF2:
    nvars: int
    rows: List[Tuple[int, int]]

    def solve(self) -> Tuple[bool, List[int], int]:
        pivots: Dict[int, Tuple[int, int]] = {}
        for mask, rhs in self.rows:
            m = mask
            r = rhs & 1
            while m:
                p = m.bit_length() - 1
                if p in pivots:
                    pm, pr = pivots[p]
                    m ^= pm
                    r ^= pr
                else:
                    pivots[p] = (m, r)
                    break
            if m == 0 and r == 1:
                return False, [0] * self.nvars, len(pivots)

        sol = [0] * self.nvars
        for p in sorted(pivots.keys(), reverse=True):
            m, r = pivots[p]
            rest = m & ~(1 << p)
            val = r
            while rest:
                q = rest & -rest
                idx = q.bit_length() - 1
                val ^= sol[idx]
                rest ^= q
            sol[p] = val
        return True, sol, len(pivots)


def main() -> None:
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3
    oa, ob, oc = color_orbs

    # E6 id mapping
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = e6_key(roots[ridx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    assert len(e6_groups) == 27

    # (color, e6id) -> root index
    color_root_by_e6id: List[List[int]] = [[-1] * 27 for _ in range(3)]
    for c, oi in enumerate(color_orbs):
        for ridx in orbits[oi]:
            color_root_by_e6id[c][root_to_e6id[ridx]] = ridx
    if any(x == -1 for row in color_root_by_e6id for x in row):
        raise RuntimeError("Missing root for some (color,e6id)")

    # Couplings and triads
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
            couplings.append((i, j, k, sign_to_bit(int(raw))))
    assert len(couplings) == 270

    triads = sorted({tuple(sorted((i, j, k))) for (i, j, k, _) in couplings})
    assert len(triads) == 45
    triad_index = {t: idx for idx, t in enumerate(triads)}

    # Generator perms p on e6ids and μ bits per (gen,color,i)
    gen_perms: List[Tuple[int, ...]] = []
    mu_bits: List[List[List[int]]] = []  # gen -> color -> i -> bit

    for alpha in cds.E6_SIMPLE_ROOTS:
        alpha_k2 = k2(alpha)

        perms_by_color = []
        mu_by_color: List[List[int]] = []
        for c, oi in enumerate(color_orbs):
            perm = [-1] * 27
            mub = [0] * 27
            for i in range(27):
                ridx = color_root_by_e6id[c][i]
                beta_k2 = k2(roots[ridx])
                beta_prime_k2, mu = weyl_mu_on_root(alpha_k2, beta_k2, root_index)
                img_idx = root_index.get(beta_prime_k2)
                if img_idx is None or idx_orb[img_idx] != oi:
                    raise RuntimeError("Weyl element left the color orbit (unexpected)")
                j = root_to_e6id[img_idx]
                perm[i] = j
                mub[i] = sign_to_bit(int(mu))
            if sorted(perm) != list(range(27)):
                raise RuntimeError("Bad generator permutation on e6ids")
            perms_by_color.append(tuple(perm))
            mu_by_color.append(mub)
        if not (perms_by_color[0] == perms_by_color[1] == perms_by_color[2]):
            raise RuntimeError("Permutation differs by color (unexpected)")
        gen_perms.append(perms_by_color[0])
        mu_bits.append(mu_by_color)

    # GF(2) variable layout: phase(81) + d(45) + g(6) = 132
    def var_phase(c: int, i: int) -> int:
        return c * 27 + i

    def var_d(t: Tuple[int, int, int]) -> int:
        return 81 + triad_index[t]

    def var_g(gen: int) -> int:
        return 81 + 45 + gen

    nvars = 132
    rows: List[Tuple[int, int]] = []

    # (A) coupling equations
    for i, j, k, raw_bit in couplings:
        t = tuple(sorted((i, j, k)))
        mask = 0
        mask ^= 1 << var_phase(0, i)
        mask ^= 1 << var_phase(1, j)
        mask ^= 1 << var_phase(2, k)
        mask ^= 1 << var_d(t)
        rows.append((mask, raw_bit))

    # (B) equivariance equations with μ
    for gen, p in enumerate(gen_perms):
        for i, j, k in triads:
            tp = tuple(sorted((p[i], p[j], p[k])))
            mask = 0
            mask ^= 1 << var_d(tp)
            mask ^= 1 << var_d((i, j, k))
            # phase differences
            mask ^= 1 << var_phase(0, i)
            mask ^= 1 << var_phase(0, p[i])
            mask ^= 1 << var_phase(1, j)
            mask ^= 1 << var_phase(1, p[j])
            mask ^= 1 << var_phase(2, k)
            mask ^= 1 << var_phase(2, p[k])
            # generator global
            mask ^= 1 << var_g(gen)
            # move μ to RHS
            rhs = mu_bits[gen][0][i] ^ mu_bits[gen][1][j] ^ mu_bits[gen][2][k]
            rows.append((mask, rhs))

    ok, sol, rank = LinearSystemGF2(nvars=nvars, rows=rows).solve()

    out: Dict[str, object] = {
        "status": "ok",
        "counts": {
            "variables": nvars,
            "equations": len(rows),
            "rank": int(rank),
            "solvable": bool(ok),
        },
    }

    if ok:
        phases = [[sol[var_phase(c, i)] for i in range(27)] for c in range(3)]
        d_bits = [sol[81 + t] for t in range(45)]
        g_bits = [sol[var_g(gen)] for gen in range(6)]
        d_map = {triads[idx]: bit_to_sign(d_bits[idx]) for idx in range(45)}
        out["solution"] = {
            "phase_bits": phases,
            "g_bits": g_bits,
            "d_triples": [{"triple": list(t), "sign": int(d_map[t])} for t in triads],
            "d_sign_distribution": dict(Counter(d_map.values())),
        }

    out_path = ROOT / "artifacts" / "e6_cubic_weyl_equivariant_signs_with_mu.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("PASS" if ok else "FAIL", "Weyl-equivariant sign system (with explicit μ).")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
