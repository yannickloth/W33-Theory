#!/usr/bin/env python3
"""
Jacobi-or-die: build the Z3-graded E8 bracket from (E6 ⊕ sl3) ⊕ (27⊗3) ⊕ (27*⊗3*)
and stress-test Jacobi numerically.

We use repo-native, *certified* ingredients:
  - E6 action in the 27 (basis matrices): artifacts/e6_27rep_basis_export/E6_basis_78.npy
  - The canonical 45-term E6 cubic invariant (signed triads):
      artifacts/canonical_su3_gauge_and_cubic.json

This script does NOT assume a priori E8 structure constants; it constructs a candidate
Lie bracket in the standard Z3-graded form and checks Jacobi across the hard cases:
  (g1,g1,g1), (g2,g2,g2), (g1,g1,g2), (g1,g2,g2), plus mixed (generic) triples.

Outputs:
  - artifacts/toe_e8_z3graded_jacobi.json
  - artifacts/toe_e8_z3graded_jacobi.md
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np

# optional numba support (safe, optional acceleration for cubic_sym)
try:
    import numba as _numba  # type: ignore

    _NUMBA_AVAILABLE = True
except Exception:
    _NUMBA_AVAILABLE = False

ROOT = Path(__file__).resolve().parents[1]


def _load_signed_cubic_triads() -> List[Tuple[int, int, int, int]]:
    """
    Return 45 signed triads (i,j,k,s) defining the E6 cubic invariant in the canonical 27 basis.
    """
    path = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    triads = data["triads"]
    d_triples = data["solution"]["d_triples"]
    out: List[Tuple[int, int, int, int]] = []
    for t, obj in zip(triads, d_triples, strict=True):
        i, j, k = (int(t[0]), int(t[1]), int(t[2]))
        s = int(obj["sign"])
        out.append((i, j, k, s))
    if len(out) != 45:
        raise RuntimeError("Expected 45 cubic triads")
    return out


def _sl3_project(M: np.ndarray) -> np.ndarray:
    tr = np.trace(M)
    return M - (tr / 3.0) * np.eye(3, dtype=np.complex128)


def _comm(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B - B @ A


def _max_abs(x: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.max(np.abs(x)))


def _elt_norm(e: "E8Z3") -> float:
    return max(
        _max_abs(e.e6),
        _max_abs(e.sl3),
        _max_abs(e.g1),
        _max_abs(e.g2),
    )


@dataclass(frozen=True)
class E8Z3:
    """
    An element of the Z3-graded vector space:
      g0 = e6 ⊕ sl3,  g1 = 27⊗3,  g2 = 27*⊗3*.

    Storage:
      - e6:  (27,27) matrix in the 27 representation
      - sl3: (3,3) matrix in the 3 representation
      - g1:  (27,3) tensor (columns are 27-vectors)
      - g2:  (27,3) tensor interpreted as dual coordinates
    """

    e6: np.ndarray
    sl3: np.ndarray
    g1: np.ndarray
    g2: np.ndarray

    @staticmethod
    def zero() -> "E8Z3":
        return E8Z3(
            e6=np.zeros((27, 27), dtype=np.complex128),
            sl3=np.zeros((3, 3), dtype=np.complex128),
            g1=np.zeros((27, 3), dtype=np.complex128),
            g2=np.zeros((27, 3), dtype=np.complex128),
        )

    def __add__(self, other: "E8Z3") -> "E8Z3":
        return E8Z3(
            e6=self.e6 + other.e6,
            sl3=self.sl3 + other.sl3,
            g1=self.g1 + other.g1,
            g2=self.g2 + other.g2,
        )

    def __sub__(self, other: "E8Z3") -> "E8Z3":
        return E8Z3(
            e6=self.e6 - other.e6,
            sl3=self.sl3 - other.sl3,
            g1=self.g1 - other.g1,
            g2=self.g2 - other.g2,
        )

    def scale(self, c: complex) -> "E8Z3":
        return E8Z3(e6=c * self.e6, sl3=c * self.sl3, g1=c * self.g1, g2=c * self.g2)


class E6Projector:
    """
    Project End(27) -> e6 using the invariant trace form:
      <A,B> = Tr(A B).
    """

    def __init__(self, basis78: np.ndarray):
        if basis78.shape != (78, 27, 27):
            raise ValueError(f"Expected (78,27,27); got {basis78.shape}")
        self.basis = basis78.astype(np.complex128)
        # flattened view for faster projections (78 x 729)
        self._basis_flat = self.basis.reshape(78, -1)

        # Gram_{ab} = Tr(B_a B_b) = sum_{i,j} B_a[i,j] * B_b[j,i]
        gram = np.einsum("aij,bji->ab", self.basis, self.basis)
        rank = int(np.linalg.matrix_rank(gram))
        if rank != 78:
            raise RuntimeError(
                f"E6 Gram matrix rank {rank} != 78 (basis not independent?)"
            )
        self.gram = gram
        self.gram_inv = np.linalg.inv(gram)

    def project(self, M: np.ndarray) -> np.ndarray:
        if M.shape != (27, 27):
            raise ValueError(f"Expected (27,27); got {M.shape}")
        # Use flattened basis + BLAS-backed dot products for speed:
        # b_a = Σ_{i,j} basis[a,i,j] * M[j,i]  == basis_flat @ M.T.ravel()
        M_flat = M.T.ravel()
        b = self._basis_flat @ M_flat
        c = self.gram_inv @ b
        out_flat = c @ self._basis_flat
        return out_flat.reshape(27, 27)


class E8Z3Bracket:
    def __init__(
        self,
        *,
        e6_projector: E6Projector,
        cubic_triads: Sequence[Tuple[int, int, int, int]],
        scale_g1g1: float = 1.0,
        scale_g2g2: float = 1.0,
        scale_e6: float = 1.0,
        scale_sl3: float = 1.0,
        use_numba: bool = False,
    ):
        self._proj_e6 = e6_projector
        self._triads = list(cubic_triads)
        # precompute triad index arrays and complex signs for vectorized cubic_sym
        triads_arr = np.array(self._triads, dtype=int)
        self._triad_a = triads_arr[:, 0]
        self._triad_b = triads_arr[:, 1]
        self._triad_c = triads_arr[:, 2]
        # keep signs as complex128 (allows non-integer scaling if needed)
        self._triad_sign = triads_arr[:, 3].astype(np.complex128)
        self.scale_g1g1 = float(scale_g1g1)
        self.scale_g2g2 = float(scale_g2g2)
        self.scale_e6 = float(scale_e6)
        self.scale_sl3 = float(scale_sl3)

        # Decide whether to enable the optional numba path. Environment variable
        # TOE_USE_NUMBA=1/true/yes will enable numba globally even if not passed.
        self._use_numba = bool(use_numba) or (
            os.environ.get("TOE_USE_NUMBA", "").lower() in ("1", "true", "yes")
        )

        # optional fast-NumPy scatter path (uses np.bincount on real/imag parts)
        self._use_fast_numpy = (
            bool(use_numba) and False
        )  # kept False unless explicitly enabled
        self._use_fast_numpy = self._use_fast_numpy or (
            os.environ.get("TOE_USE_FAST_CUBIC_SYM", "").lower() in ("1", "true", "yes")
        )

        # Precompile a numba-accelerated cubic_sym implementation if available and requested.
        if self._use_numba and _NUMBA_AVAILABLE:
            a_cl = self._triad_a.copy().astype(np.int64)
            b_cl = self._triad_b.copy().astype(np.int64)
            c_cl = self._triad_c.copy().astype(np.int64)
            s_cl = self._triad_sign.copy().astype(np.complex128)

            @_numba.njit
            def _cubic_sym_numba(u, v, scale):
                out = np.zeros(27, dtype=np.complex128)
                for t in range(a_cl.shape[0]):
                    ai = a_cl[t]
                    bi = b_cl[t]
                    ci = c_cl[t]
                    ss = s_cl[t] * scale
                    out[ai] += ss * (u[bi] * v[ci] + u[ci] * v[bi])
                    out[bi] += ss * (u[ai] * v[ci] + u[ci] * v[ai])
                    out[ci] += ss * (u[ai] * v[bi] + u[bi] * v[ai])
                return out

            # store the compiled function for cubic_sym to call when enabled
            self._cubic_sym_numba = _cubic_sym_numba
        else:
            self._cubic_sym_numba = None

        # prepare small cached arrays for fast-numpy path
        self._triad_a_arr = self._triad_a
        self._triad_b_arr = self._triad_b
        self._triad_c_arr = self._triad_c
        self._triad_sign_arr = self._triad_sign

    def cubic_sym(self, u: np.ndarray, v: np.ndarray, *, scale: float) -> np.ndarray:
        """
        Vectorized symmetric bilinear map S^2(27) -> 27* induced by the cubic triads.
        Replaces the Python triad loop with NumPy indexing and accumulation for speed.

        When `use_numba` was enabled at construction and `numba` is available, this will
        dispatch to a precompiled Numba implementation (optional acceleration).
        """
        if u.shape != (27,) or v.shape != (27,):
            raise ValueError("Expected u,v shape (27,)")

        # Fast path: call the numba-compiled kernel when available and requested.
        if getattr(self, "_cubic_sym_numba", None) is not None and self._use_numba:
            return self._cubic_sym_numba(u, v, float(scale))
        a = self._triad_a
        b = self._triad_b
        c = self._triad_c
        s = self._triad_sign * float(scale)

        # vectorized contributions for each triad
        contrib_a = s * (u[b] * v[c] + u[c] * v[b])
        contrib_b = s * (u[a] * v[c] + u[c] * v[a])
        contrib_c = s * (u[a] * v[b] + u[b] * v[a])

        # Fast path: call the numba-compiled kernel when available and requested.
        if getattr(self, "_cubic_sym_numba", None) is not None and self._use_numba:
            return self._cubic_sym_numba(u, v, float(scale))

        # Fast NumPy scatter path (optional): use np.bincount on real/imag parts
        if self._use_fast_numpy:
            # split real/imag and accumulate using bincount (minlength=27)
            out_real = (
                np.bincount(a, weights=contrib_a.real, minlength=27)
                + np.bincount(b, weights=contrib_b.real, minlength=27)
                + np.bincount(c, weights=contrib_c.real, minlength=27)
            )
            out_imag = (
                np.bincount(a, weights=contrib_a.imag, minlength=27)
                + np.bincount(b, weights=contrib_b.imag, minlength=27)
                + np.bincount(c, weights=contrib_c.imag, minlength=27)
            )
            return (out_real + 1j * out_imag).astype(np.complex128)

        # Default (safe) accumulation using np.add.at
        out = np.zeros(27, dtype=np.complex128)
        np.add.at(out, a, contrib_a)
        np.add.at(out, b, contrib_b)
        np.add.at(out, c, contrib_c)
        return out

    def bracket_g1_g1(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """
        [27⊗3, 27⊗3] -> 27*⊗3* using (cubic_sym on 27) ⊗ (epsilon on 3).
        """
        if X.shape != (27, 3) or Y.shape != (27, 3):
            raise ValueError("Expected X,Y shape (27,3)")
        out = np.zeros((27, 3), dtype=np.complex128)
        # epsilon_{ab0}: (1,2)=+1, (2,1)=-1
        out[:, 0] = self.cubic_sym(
            X[:, 1], Y[:, 2], scale=self.scale_g1g1
        ) - self.cubic_sym(X[:, 2], Y[:, 1], scale=self.scale_g1g1)
        # epsilon_{ab1}: (2,0)=+1, (0,2)=-1
        out[:, 1] = self.cubic_sym(
            X[:, 2], Y[:, 0], scale=self.scale_g1g1
        ) - self.cubic_sym(X[:, 0], Y[:, 2], scale=self.scale_g1g1)
        # epsilon_{ab2}: (0,1)=+1, (1,0)=-1
        out[:, 2] = self.cubic_sym(
            X[:, 0], Y[:, 1], scale=self.scale_g1g1
        ) - self.cubic_sym(X[:, 1], Y[:, 0], scale=self.scale_g1g1)
        return out

    def bracket_g2_g2(self, U: np.ndarray, V: np.ndarray) -> np.ndarray:
        """
        [27*⊗3*, 27*⊗3*] -> 27⊗3 using an independent scaling for the dual intertwiner.

        Note: by representation theory the *shape* (support on the 45 triads) is fixed; however the
        relative normalization between [g1,g1] and [g2,g2] is a genuine degree of freedom until we
        enforce the mixed Jacobi constraints (g1,g1,g2) / (g2,g2,g1). We therefore keep this
        scale separate from `scale_g1g1`.
        """
        if U.shape != (27, 3) or V.shape != (27, 3):
            raise ValueError("Expected U,V shape (27,3)")
        out = np.zeros((27, 3), dtype=np.complex128)
        out[:, 0] = self.cubic_sym(
            U[:, 1], V[:, 2], scale=self.scale_g2g2
        ) - self.cubic_sym(U[:, 2], V[:, 1], scale=self.scale_g2g2)
        out[:, 1] = self.cubic_sym(
            U[:, 2], V[:, 0], scale=self.scale_g2g2
        ) - self.cubic_sym(U[:, 0], V[:, 2], scale=self.scale_g2g2)
        out[:, 2] = self.cubic_sym(
            U[:, 0], V[:, 1], scale=self.scale_g2g2
        ) - self.cubic_sym(U[:, 1], V[:, 0], scale=self.scale_g2g2)
        return out

    def bracket(self, a: E8Z3, b: E8Z3) -> E8Z3:
        """
        Full Z3-graded bracket with tunable scalings:
          - scale_g1g1:  multiplies [g1,g1] -> g2
          - scale_g2g2:  multiplies [g2,g2] -> g1
          - scale_e6:    multiplies the e6-component of [g1,g2]
          - scale_sl3:   multiplies the sl3-component of [g1,g2]
        """
        # g0-g0
        e6 = _comm(a.e6, b.e6)
        sl3 = _comm(a.sl3, b.sl3)

        # g0 action on g1 (and antisym for [g1,g0] via the mixed terms)
        g1 = a.e6 @ b.g1 - b.e6 @ a.g1 + b.g1 @ a.sl3.T - a.g1 @ b.sl3.T

        # g0 action on g2
        g2 = -a.e6.T @ b.g2 + b.e6.T @ a.g2 - b.g2 @ a.sl3 + a.g2 @ b.sl3

        # g1-g1 -> g2
        g2 = g2 + self.bracket_g1_g1(a.g1, b.g1)

        # g2-g2 -> g1
        g1 = g1 + self.bracket_g2_g2(a.g2, b.g2)

        # g1-g2 -> g0 (antisymmetrized)
        if np.any(a.g1) or np.any(b.g2):
            A0 = a.g1 @ b.g2.T
            B0 = a.g1.T @ b.g2
            e6 = e6 + self.scale_e6 * self._proj_e6.project(A0)
            sl3 = sl3 + self.scale_sl3 * _sl3_project(B0)
        if np.any(b.g1) or np.any(a.g2):
            A0 = b.g1 @ a.g2.T
            B0 = b.g1.T @ a.g2
            e6 = e6 - self.scale_e6 * self._proj_e6.project(A0)
            sl3 = sl3 - self.scale_sl3 * _sl3_project(B0)

        return E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)


def _random_int_matrix(
    rng: np.random.Generator, shape: Tuple[int, ...], *, scale: int
) -> np.ndarray:
    return rng.integers(low=-scale, high=scale + 1, size=shape).astype(np.complex128)


def _random_element(
    rng: np.random.Generator,
    e6_basis: np.ndarray,
    *,
    scale0: int,
    scale1: int,
    scale2: int,
    include_g0: bool = True,
    include_g1: bool = True,
    include_g2: bool = True,
) -> E8Z3:
    e6 = np.zeros((27, 27), dtype=np.complex128)
    sl3 = np.zeros((3, 3), dtype=np.complex128)
    g1 = np.zeros((27, 3), dtype=np.complex128)
    g2 = np.zeros((27, 3), dtype=np.complex128)

    if include_g0 and scale0 > 0:
        coeff = rng.integers(-scale0, scale0 + 1, size=(78,), dtype=np.int64)
        e6 = np.tensordot(coeff.astype(np.complex128), e6_basis, axes=(0, 0))
        sl3 = _random_int_matrix(rng, (3, 3), scale=scale0)
        sl3 = _sl3_project(sl3)

    if include_g1 and scale1 > 0:
        g1 = _random_int_matrix(rng, (27, 3), scale=scale1)

    if include_g2 and scale2 > 0:
        g2 = _random_int_matrix(rng, (27, 3), scale=scale2)

    return E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)


def _jacobi(br: E8Z3Bracket, x: E8Z3, y: E8Z3, z: E8Z3) -> E8Z3:
    return (
        br.bracket(x, br.bracket(y, z))
        + br.bracket(y, br.bracket(z, x))
        + br.bracket(z, br.bracket(x, y))
    )


def _tune_sl3_scale(
    br0: E8Z3Bracket,
    rng: np.random.Generator,
    e6_basis: np.ndarray,
    *,
    samples: int,
    scale1: int,
) -> float:
    """
    Use Jacobi on (g1,g1,g1) to fit the relative scaling between the e6 and sl3
    contributions in [g1,g2] by least squares.

    We hold scale_e6=1 and solve for r=scale_sl3 minimizing ||J_e6 + r J_sl3||.
    """
    # Build two brackets: one with only e6 contribution, one with only sl3 contribution.
    br_e6 = E8Z3Bracket(
        e6_projector=br0._proj_e6,
        cubic_triads=br0._triads,
        scale_g1g1=br0.scale_g1g1,
        scale_g2g2=br0.scale_g2g2,
        scale_e6=1.0,
        scale_sl3=0.0,
    )
    br_sl3 = E8Z3Bracket(
        e6_projector=br0._proj_e6,
        cubic_triads=br0._triads,
        scale_g1g1=br0.scale_g1g1,
        scale_g2g2=br0.scale_g2g2,
        scale_e6=0.0,
        scale_sl3=1.0,
    )

    num = 0.0
    den = 0.0
    for _ in range(samples):
        x = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=scale1,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        y = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=scale1,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        z = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=scale1,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        j_e6 = _jacobi(br_e6, x, y, z).g1
        j_sl3 = _jacobi(br_sl3, x, y, z).g1
        ve6 = j_e6.reshape(-1)
        vsl3 = j_sl3.reshape(-1)
        num += float(np.vdot(vsl3, ve6).real)
        den += float(np.vdot(vsl3, vsl3).real)
    if den == 0.0:
        return 0.0
    return float(-num / den)


def _tune_g2g2_scale(
    br0: E8Z3Bracket,
    rng: np.random.Generator,
    e6_basis: np.ndarray,
    *,
    samples: int,
    scale1: int,
    scale2: int,
) -> float:
    """
    Fit the dual scaling `scale_g2g2` by least squares on Jacobi(g1,g1,g2).

    Rationale:
      For x,y in g1 and u in g2, Jacobi(x,y,u) lives in g1 and depends affinely on
      `scale_g2g2` (holding other scales fixed), so we can solve a 1D least squares problem.
    """
    br_b0 = E8Z3Bracket(
        e6_projector=br0._proj_e6,
        cubic_triads=br0._triads,
        scale_g1g1=br0.scale_g1g1,
        scale_g2g2=0.0,
        scale_e6=br0.scale_e6,
        scale_sl3=br0.scale_sl3,
    )
    br_b1 = E8Z3Bracket(
        e6_projector=br0._proj_e6,
        cubic_triads=br0._triads,
        scale_g1g1=br0.scale_g1g1,
        scale_g2g2=1.0,
        scale_e6=br0.scale_e6,
        scale_sl3=br0.scale_sl3,
    )

    num = 0.0
    den = 0.0
    for _ in range(samples):
        x = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=scale1,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        y = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=scale1,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        u = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=0,
            scale2=scale2,
            include_g0=False,
            include_g1=False,
        )
        j0 = _jacobi(br_b0, x, y, u).g1
        j1 = _jacobi(br_b1, x, y, u).g1
        dj = (j1 - j0).reshape(-1)
        v0 = j0.reshape(-1)
        num += float(np.vdot(dj, v0).real)
        den += float(np.vdot(dj, dj).real)
    if den == 0.0:
        return 0.0
    return float(-num / den)


def _tune_sl3_and_g2g2_scales(
    *,
    proj: E6Projector,
    triads: Sequence[Tuple[int, int, int, int]],
    rng: np.random.Generator,
    e6_basis: np.ndarray,
    scale_g1g1: float,
    scale_e6: float,
    samples: int,
    scale1: int,
    scale2: int,
) -> Tuple[float, float]:
    """
    Jointly fit (scale_sl3, scale_g2g2) from Jacobi(g1,g1,g2), holding scale_e6 fixed.

    We solve the 2D least squares problem:
      minimize || J0 + r J_sl3 + s J_g2 || over r,s,
    where:
      - J0   := Jacobi with (scale_e6=scale_e6, scale_sl3=0, scale_g2g2=0)
      - J_sl3:= Jacobi with (scale_e6=0,        scale_sl3=1, scale_g2g2=0)
      - J_g2 := Jacobi with (scale_e6=0,        scale_sl3=0, scale_g2g2=1)
    """
    br0 = E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads,
        scale_g1g1=scale_g1g1,
        scale_g2g2=0.0,
        scale_e6=scale_e6,
        scale_sl3=0.0,
    )
    br_sl3 = E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads,
        scale_g1g1=scale_g1g1,
        scale_g2g2=0.0,
        scale_e6=0.0,
        scale_sl3=1.0,
    )
    br_g2 = E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads,
        scale_g1g1=scale_g1g1,
        scale_g2g2=1.0,
        scale_e6=0.0,
        scale_sl3=0.0,
    )

    a11 = 0.0
    a12 = 0.0
    a22 = 0.0
    b1 = 0.0
    b2 = 0.0

    for _ in range(samples):
        x = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=scale1,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        y = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=scale1,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        u = _random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=0,
            scale2=scale2,
            include_g0=False,
            include_g1=False,
        )

        c = _jacobi(br0, x, y, u).g1.reshape(-1)
        a = _jacobi(br_sl3, x, y, u).g1.reshape(-1)
        d = _jacobi(br_g2, x, y, u).g1.reshape(-1)

        a11 += float(np.vdot(a, a).real)
        a12 += float(np.vdot(a, d).real)
        a22 += float(np.vdot(d, d).real)
        b1 += float(np.vdot(a, c).real)
        b2 += float(np.vdot(d, c).real)

    det = a11 * a22 - a12 * a12
    if det == 0.0:
        return 0.0, 0.0

    r = (-b1 * a22 + b2 * a12) / det
    s = (-b2 * a11 + b1 * a12) / det
    return float(r), float(s)


def _write_md(path: Path, report: dict) -> None:
    lines: List[str] = []
    lines.append("# Z3-graded E8 Jacobi check (constructed)\n")
    lines.append(f"- status: `{report.get('status')}`")
    lines.append(f"- scale_g1g1: `{report['scales']['scale_g1g1']}`")
    lines.append(f"- scale_g2g2: `{report['scales']['scale_g2g2']}`")
    lines.append(f"- scale_e6: `{report['scales']['scale_e6']}`")
    lines.append(f"- scale_sl3: `{report['scales']['scale_sl3']}`")
    lines.append("")
    lines.append("## Jacobi residuals (max entrywise abs)\n")
    for k, v in report["jacobi"].items():
        lines.append(f"- {k}: `{v['max_residual']}` over `{v['trials']}` trials")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--trials", type=int, default=500)
    parser.add_argument("--tune-samples", type=int, default=200)
    parser.add_argument(
        "--scale0", type=int, default=2, help="rand scale for g0 coeffs"
    )
    parser.add_argument(
        "--scale1", type=int, default=2, help="rand scale for g1 entries"
    )
    parser.add_argument(
        "--scale2", type=int, default=2, help="rand scale for g2 entries"
    )
    parser.add_argument("--scale-g1g1", type=float, default=1.0)
    parser.add_argument(
        "--scale-g2g2",
        type=float,
        default=float("nan"),
        help="If NaN (default), fit from Jacobi(g1,g1,g2). Otherwise use the provided value.",
    )
    parser.add_argument(
        "--scale-cubic",
        type=float,
        default=float("nan"),
        help="Deprecated alias for --scale-g1g1 (kept for older notes).",
    )
    parser.add_argument("--scale-e6", type=float, default=1.0)
    parser.add_argument(
        "--scale-sl3",
        type=float,
        default=float("nan"),
        help="If set to NaN (default), fit from (g1,g1,g1) Jacobi. Otherwise use the provided value.",
    )
    parser.add_argument("--tol", type=float, default=1e-7)
    args = parser.parse_args(list(argv) if argv is not None else None)

    basis_path = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    if not basis_path.exists():
        raise RuntimeError(
            "Missing artifacts/e6_27rep_basis_export/E6_basis_78.npy. "
            "Run: python3 tools/build_e6_27rep_minuscule.py --export-basis78"
        )

    e6_basis = np.load(basis_path).astype(np.complex128)
    triads = _load_signed_cubic_triads()
    proj = E6Projector(e6_basis)

    rng = np.random.default_rng(int(args.seed))

    if not np.isnan(float(args.scale_cubic)):
        scale_g1g1 = float(args.scale_cubic)
    else:
        scale_g1g1 = float(args.scale_g1g1)

    if np.isnan(float(args.scale_sl3)) and np.isnan(float(args.scale_g2g2)):
        # Joint fit from the mixed Jacobi constraints (most informative).
        scale_sl3, scale_g2g2 = _tune_sl3_and_g2g2_scales(
            proj=proj,
            triads=triads,
            rng=rng,
            e6_basis=e6_basis,
            scale_g1g1=scale_g1g1,
            scale_e6=float(args.scale_e6),
            samples=int(args.tune_samples),
            scale1=int(args.scale1),
            scale2=int(args.scale2),
        )
    else:
        # Fall back to the older 1D fits / explicit values.
        if np.isnan(float(args.scale_sl3)):
            br0 = E8Z3Bracket(
                e6_projector=proj,
                cubic_triads=triads,
                scale_g1g1=scale_g1g1,
                scale_g2g2=0.0,
                scale_e6=float(args.scale_e6),
                scale_sl3=0.0,
            )
            scale_sl3 = _tune_sl3_scale(
                br0,
                rng,
                e6_basis,
                samples=int(args.tune_samples),
                scale1=int(args.scale1),
            )
        else:
            scale_sl3 = float(args.scale_sl3)

        if np.isnan(float(args.scale_g2g2)):
            scale_g2g2 = _tune_g2g2_scale(
                E8Z3Bracket(
                    e6_projector=proj,
                    cubic_triads=triads,
                    scale_g1g1=scale_g1g1,
                    scale_g2g2=0.0,
                    scale_e6=float(args.scale_e6),
                    scale_sl3=scale_sl3,
                ),
                rng,
                e6_basis,
                samples=int(args.tune_samples),
                scale1=int(args.scale1),
                scale2=int(args.scale2),
            )
        else:
            scale_g2g2 = float(args.scale_g2g2)

    br = E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads,
        scale_g1g1=scale_g1g1,
        scale_g2g2=scale_g2g2,
        scale_e6=float(args.scale_e6),
        scale_sl3=scale_sl3,
    )

    def run_case(
        name: str,
        include_g0: bool,
        include_g1: bool,
        include_g2: bool,
        trials: int,
    ) -> dict:
        max_res = 0.0
        for _ in range(trials):
            x = _random_element(
                rng,
                e6_basis,
                scale0=int(args.scale0),
                scale1=int(args.scale1),
                scale2=int(args.scale2),
                include_g0=include_g0,
                include_g1=include_g1,
                include_g2=include_g2,
            )
            y = _random_element(
                rng,
                e6_basis,
                scale0=int(args.scale0),
                scale1=int(args.scale1),
                scale2=int(args.scale2),
                include_g0=include_g0,
                include_g1=include_g1,
                include_g2=include_g2,
            )
            z = _random_element(
                rng,
                e6_basis,
                scale0=int(args.scale0),
                scale1=int(args.scale1),
                scale2=int(args.scale2),
                include_g0=include_g0,
                include_g1=include_g1,
                include_g2=include_g2,
            )
            j = _jacobi(br, x, y, z)
            max_res = max(max_res, _elt_norm(j))
        return {"trials": int(trials), "max_residual": float(max_res)}

    cases = {
        "g1_g1_g1": run_case(
            "g1_g1_g1",
            include_g0=False,
            include_g1=True,
            include_g2=False,
            trials=args.trials,
        ),
        "g2_g2_g2": run_case(
            "g2_g2_g2",
            include_g0=False,
            include_g1=False,
            include_g2=True,
            trials=args.trials,
        ),
        "g1_g1_g2": run_case(
            "g1_g1_g2",
            include_g0=False,
            include_g1=True,
            include_g2=True,
            trials=args.trials,
        ),
        "mixed_all": run_case(
            "mixed_all",
            include_g0=True,
            include_g1=True,
            include_g2=True,
            trials=args.trials,
        ),
    }

    max_overall = max(v["max_residual"] for v in cases.values())
    status = "ok" if max_overall <= float(args.tol) else "fail"

    report = {
        "status": status,
        "tol": float(args.tol),
        "scales": {
            "scale_g1g1": float(scale_g1g1),
            "scale_g2g2": float(scale_g2g2),
            "scale_e6": float(args.scale_e6),
            "scale_sl3": float(scale_sl3),
        },
        "paths": {
            "e6_basis": str(basis_path),
            "cubic_triads": "artifacts/canonical_su3_gauge_and_cubic.json",
        },
        "jacobi": cases,
    }

    out_json = ROOT / "artifacts" / "toe_e8_z3graded_jacobi.json"
    out_md = ROOT / "artifacts" / "toe_e8_z3graded_jacobi.md"
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    _write_md(out_md, report)
    print(f"status={status} max_residual={max_overall} tol={args.tol}")
    print(f"scale_sl3={scale_sl3}")
    print(f"scale_g2g2={scale_g2g2}")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")

    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
