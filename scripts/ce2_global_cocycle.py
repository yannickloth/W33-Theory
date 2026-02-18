#!/usr/bin/env python3
"""Global (non per-triple) CE2 cocycle rules inferred from sparse local repairs.

This module turns the *structured* CE2 local solutions into a reusable law.

Current status:
  - Implements the dominant "simple family" (5184 / 5832 sparse entries):
      * exactly one e6 matrix unit in U or V
      * coefficient magnitude = 1/54
  - Support location is fully global/Heisenberg:
      row = match + other - c   in F3^3 Heisenberg coordinates (u1,u2,z)
      col = other
  - Side (U vs V) depends only on which g1 element matches the sl3 index.
  - Sign is given by a committed explicit GF(2) polynomial (deg ≤ 4),
    falling back to the compact 864-entry map if needed.

  - Implements the remaining "fiber family" (648 / 5832 sparse entries):
      * exactly one e6 + one sl3 matrix unit
      * coefficient magnitude = 1/108
      * supported exactly on the 9 Heisenberg fibers (bad9) in the E6 27-set
      * sign is fully explicit from indices (no lookup)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


@dataclass(frozen=True)
class CE2SparseUV:
    U: list[tuple[int, Fraction]]
    V: list[tuple[int, Fraction]]


SimpleFamilyUV = CE2SparseUV  # compatibility alias


def _flat_e6(row: int, col: int) -> int:
    return int(row) * 27 + int(col)


def _flat_sl3(i: int, j: int) -> int:
    return 27 * 27 + int(i) * 3 + int(j)


def _decode_key_triplet(
    k: str,
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """Parse key like '0,0:17,1:3,0' -> ((0,0),(17,1),(3,0))."""
    parts = str(k).split(":")
    if len(parts) != 3:
        raise ValueError(f"unexpected key format: {k!r}")

    def parse_pair(s: str) -> tuple[int, int]:
        a, b = s.split(",")
        return (int(a), int(b))

    return (parse_pair(parts[0]), parse_pair(parts[1]), parse_pair(parts[2]))


@lru_cache(maxsize=1)
def _heisenberg_vec_maps() -> (
    tuple[dict[int, tuple[int, int, int]], dict[tuple[int, int, int], int]]
):
    """Return e6id -> (u1,u2,z) and inverse map, all mod 3."""
    model_path = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    e6id_to_h = model.get("e6id_to_heisenberg", {})
    if not isinstance(e6id_to_h, dict) or len(e6id_to_h) != 27:
        raise ValueError("unexpected/missing e6id_to_heisenberg mapping")

    e6id_to_vec: dict[int, tuple[int, int, int]] = {}
    vec_to_e6id: dict[tuple[int, int, int], int] = {}
    for k, payload in e6id_to_h.items():
        if not isinstance(payload, dict):
            raise ValueError("unexpected heisenberg payload")
        u = payload.get("u")
        z = payload.get("z")
        if not (isinstance(u, list) and len(u) == 2):
            raise ValueError("unexpected heisenberg u")
        vec = (int(u[0]) % 3, int(u[1]) % 3, int(z) % 3)
        e6id = int(k)
        e6id_to_vec[e6id] = vec
        vec_to_e6id[vec] = e6id

    if len(e6id_to_vec) != 27 or len(vec_to_e6id) != 27:
        raise ValueError("expected full 27-point inverse mapping")
    return e6id_to_vec, vec_to_e6id


def _vec_add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return ((a[0] + b[0]) % 3, (a[1] + b[1]) % 3, (a[2] + b[2]) % 3)


def _vec_sub(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return ((a[0] - b[0]) % 3, (a[1] - b[1]) % 3, (a[2] - b[2]) % 3)


@lru_cache(maxsize=1)
def _simple_family_sign_map() -> dict[tuple[int, int, int], int]:
    """Load sign(c, match, other) ∈ {+1,-1} from sparse CE2 data for the simple family."""
    compact_path = ROOT / "committed_artifacts" / "ce2_simple_family_sign_map.json"
    if compact_path.exists():
        data = json.loads(compact_path.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
        if not isinstance(entries, list):
            raise ValueError("unexpected compact CE2 sign JSON format")

        sign_map: dict[tuple[int, int, int], int] = {}
        for rec in entries:
            if not isinstance(rec, dict):
                continue
            try:
                c_i = int(rec["c"])
                match_i = int(rec["match"])
                other_i = int(rec["other"])
                s = int(rec["sign"])
            except Exception:
                continue
            if s not in (-1, 1):
                raise ValueError(f"unexpected sign value in compact map: {s}")
            sign_map[(c_i, match_i, other_i)] = s

        if len(sign_map) != 864:
            raise ValueError(
                f"unexpected compact sign-map size: {len(sign_map)} (expected 864)"
            )
        return sign_map

    sparse_path = ROOT / "committed_artifacts" / "ce2_sparse_local_solutions.json"
    data = json.loads(sparse_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("unexpected sparse CE2 JSON format")

    sign_map: dict[tuple[int, int, int], int] = {}
    for rec in entries:
        if not isinstance(rec, dict):
            continue
        k = rec.get("k")
        if not isinstance(k, str):
            continue
        a, b, c = _decode_key_triplet(k)
        U_raw = rec.get("U", [])
        V_raw = rec.get("V", [])
        if not isinstance(U_raw, list) or not isinstance(V_raw, list):
            continue
        nz = list(U_raw) + list(V_raw)
        if len(nz) != 1:
            continue
        idx, val_raw = nz[0]
        idx = int(idx)
        val = Fraction(str(val_raw))
        if val == 0 or abs(val.denominator) != 54:
            continue
        if not (0 <= idx < 27 * 27):
            continue

        # Determine (c,match,other) using the sl3-index equality rule.
        a_i, a_j = a
        b_i, b_j = b
        c_i, c_j = c
        if a_j == c_j and b_j != c_j:
            match_i, other_i = a_i, b_i
        elif b_j == c_j and a_j != c_j:
            match_i, other_i = b_i, a_i
        else:
            continue

        s = 1 if val > 0 else -1
        key = (int(c_i), int(match_i), int(other_i))
        if key in sign_map and int(sign_map[key]) != int(s):
            raise ValueError(
                f"non-deterministic sign for key={key}: {sign_map[key]} vs {s}"
            )
        sign_map[key] = int(s)

    if len(sign_map) != 864:
        raise ValueError(
            f"unexpected simple-family sign-map size: {len(sign_map)} (expected 864)"
        )
    return sign_map


def _encode_trit_pair_bits(trit: int) -> tuple[int, int]:
    """Encode a trit in {0,1,2} into two GF(2) bits (is1,is2)."""
    t = int(trit) % 3
    if t == 0:
        return (0, 0)
    if t == 1:
        return (1, 0)
    return (0, 1)


def _encode_simple_family_sign_input_bits(c_i: int, match_i: int, other_i: int) -> int:
    """Encode (c,match,other) into an 18-bit mask for the GF(2) sign polynomial."""
    e6id_to_vec, _vec_to_e6id = _heisenberg_vec_maps()
    vc = e6id_to_vec[int(c_i)]
    vm = e6id_to_vec[int(match_i)]
    vo = e6id_to_vec[int(other_i)]
    trits = (
        vc[0],
        vc[1],
        vc[2],
        vm[0],
        vm[1],
        vm[2],
        vo[0],
        vo[1],
        vo[2],
    )
    bits_mask = 0
    for i, t in enumerate(trits):
        b0, b1 = _encode_trit_pair_bits(t)
        if b0:
            bits_mask |= 1 << (2 * i + 0)
        if b1:
            bits_mask |= 1 << (2 * i + 1)
    return bits_mask


@lru_cache(maxsize=1)
def _gf2_deg4_monomial_mask_to_feature_idx() -> dict[int, int]:
    """deg-lex monomials on 18 bits up to degree 4 (4048 terms)."""
    n_bits = 18
    masks: list[int] = [0]  # constant
    for d in range(1, 5):
        for combo in combinations(range(n_bits), d):
            m = 0
            for b in combo:
                m |= 1 << b
            masks.append(m)
    if len(masks) != 4048:
        raise ValueError(f"unexpected monomial count: {len(masks)} (expected 4048)")
    out = {m: i for i, m in enumerate(masks)}
    if len(out) != 4048:
        raise ValueError("duplicate monomial mask detected")
    return out


@lru_cache(maxsize=1)
def _simple_family_sign_poly_coeff_mask() -> int | None:
    """Load a degree-4 GF(2) polynomial for the simple-family sign, if present."""
    poly_path = (
        ROOT / "committed_artifacts" / "ce2_simple_family_sign_poly_gf2_deg4.json"
    )
    if not poly_path.exists():
        return None
    data = json.loads(poly_path.read_text(encoding="utf-8"))
    idxs = data.get("coeff_feature_indices", [])
    if not isinstance(idxs, list):
        raise ValueError("unexpected CE2 sign polynomial JSON format")
    coeff_mask = 0
    for idx in idxs:
        i = int(idx)
        if not (0 <= i < 4048):
            raise ValueError(f"unexpected coefficient index: {i}")
        coeff_mask |= 1 << i
    return coeff_mask


@lru_cache(maxsize=20000)
def _eval_simple_family_sign_poly_bit(input_bits_mask: int) -> int:
    """Evaluate the fitted sign polynomial on the 18-bit encoding. Returns bit in {0,1}."""
    coeff_mask = _simple_family_sign_poly_coeff_mask()
    if coeff_mask is None:
        raise RuntimeError("simple-family sign polynomial not available")
    mask_to_idx = _gf2_deg4_monomial_mask_to_feature_idx()
    ones = [i for i in range(18) if ((int(input_bits_mask) >> i) & 1)]
    # constant monomial always evaluates to 1
    bit = (coeff_mask >> mask_to_idx[0]) & 1
    for d in range(1, min(4, len(ones)) + 1):
        for combo in combinations(ones, d):
            m = 0
            for b in combo:
                m |= 1 << b
            bit ^= (coeff_mask >> mask_to_idx[m]) & 1
    return int(bit) & 1


def _f3_chi(v: int) -> int:
    """Quadratic character chi on F3: chi(0)=chi(1)=+1, chi(2)=-1."""
    return 1 if (int(v) % 3) in (0, 1) else -1


def _f3_omega(u: tuple[int, int], v: tuple[int, int]) -> int:
    """Standard symplectic form ω((x,y),(a,b)) = y·a - x·b (mod 3)."""
    x, y = int(u[0]) % 3, int(u[1]) % 3
    a, b = int(v[0]) % 3, int(v[1]) % 3
    return (y * a - x * b) % 3


def _f3_k_of_direction(d: tuple[int, int]) -> int:
    """Constant-line selector k(d) used in the CE2 simple-family sign laws."""
    d1, d2 = int(d[0]) % 3, int(d[1]) % 3
    return ((-d1) if d2 == 0 else d1) % 3


F3SparsePolyTerm = tuple[int, tuple[int, int, int, int]]


def _eval_f3_sparse_poly(
    uc1: int,
    uc2: int,
    d1: int,
    d2: int,
    terms: tuple[F3SparsePolyTerm, ...],
) -> int:
    """Evaluate a sparse polynomial over F3 in variables (uc1,uc2,d1,d2), exponents in {0,1,2}."""
    xs = (int(uc1) % 3, int(uc2) % 3, int(d1) % 3, int(d2) % 3)
    acc = 0
    for coeff, exps in terms:
        c = int(coeff) % 3
        mon = 1
        for base, exp in zip(xs, exps):
            e = int(exp)
            if e == 0:
                continue
            if e == 1:
                mon = (mon * base) % 3
            elif e == 2:
                mon = (mon * base * base) % 3
            else:
                raise ValueError(f"unexpected exponent for F3 sparse poly: {e}")
        acc = (acc + c * mon) % 3
    return int(acc) % 3


# Closed-form sign laws in Heisenberg/symplectic variables (uc1,uc2,d1,d2).
#
# These sparse term lists were fitted exactly (degree <= 5) against the committed
# 864-entry CE2 simple-family sign map and then validated by:
#   - symplectic delta law for t=2 (u_m != u_o)
#   - constant-line selection rule (same set for t=1 and t=2)
# See: scripts/w33_ce2_sign_symplectic_closed_form.py
_SIMPLE_FAMILY_SIGN_C0_TERMS: dict[int, tuple[F3SparsePolyTerm, ...]] = {
    # t=1 (u_m == u_o), variable-case c0 (deg <= 4, weight 16)
    1: (
        (1, (0, 0, 0, 2)),
        (1, (0, 0, 2, 0)),
        (2, (0, 1, 0, 0)),
        (1, (0, 1, 0, 2)),
        (1, (0, 1, 1, 0)),
        (2, (0, 1, 1, 1)),
        (1, (0, 1, 2, 0)),
        (1, (0, 2, 1, 1)),
        (2, (0, 2, 2, 0)),
        (2, (1, 0, 0, 1)),
        (1, (1, 0, 0, 2)),
        (2, (1, 0, 1, 1)),
        (1, (1, 1, 0, 0)),
        (1, (1, 1, 0, 2)),
        (2, (1, 1, 1, 1)),
        (2, (2, 0, 0, 2)),
    ),
    # t=2 (u_m != u_o), variable-case c0 (deg <= 4, weight 14)
    2: (
        (1, (0, 0, 0, 2)),
        (1, (0, 0, 2, 0)),
        (2, (0, 1, 0, 0)),
        (1, (0, 1, 0, 2)),
        (2, (0, 1, 1, 1)),
        (1, (0, 1, 2, 0)),
        (1, (0, 2, 1, 1)),
        (2, (0, 2, 2, 0)),
        (1, (1, 0, 0, 2)),
        (2, (1, 0, 1, 1)),
        (1, (1, 1, 0, 0)),
        (1, (1, 1, 0, 2)),
        (2, (1, 1, 1, 1)),
        (2, (2, 0, 0, 2)),
    ),
}

_SIMPLE_FAMILY_SIGN_EPS_TERMS: dict[int, tuple[F3SparsePolyTerm, ...]] = {
    # eps is encoded by e in F3, with eps=+1 if e in {0,1}, else -1.
    # t=1 variable-case eps encoding polynomial e (deg <= 5, weight 36)
    1: (
        (2, (0, 0, 0, 2)),
        (2, (0, 0, 1, 0)),
        (2, (0, 0, 1, 1)),
        (2, (0, 0, 1, 2)),
        (1, (0, 0, 2, 0)),
        (2, (0, 0, 2, 1)),
        (1, (0, 1, 0, 0)),
        (2, (0, 1, 0, 2)),
        (1, (0, 1, 1, 0)),
        (2, (0, 1, 1, 1)),
        (2, (0, 1, 2, 0)),
        (2, (0, 2, 1, 0)),
        (1, (0, 2, 2, 1)),
        (1, (1, 0, 0, 0)),
        (2, (1, 0, 0, 1)),
        (1, (1, 0, 0, 2)),
        (2, (1, 0, 1, 0)),
        (1, (1, 0, 1, 1)),
        (1, (1, 0, 2, 0)),
        (2, (1, 0, 2, 1)),
        (2, (1, 1, 0, 0)),
        (2, (1, 1, 0, 1)),
        (2, (1, 1, 1, 0)),
        (2, (1, 1, 1, 1)),
        (2, (1, 1, 1, 2)),
        (2, (1, 1, 2, 0)),
        (2, (1, 1, 2, 1)),
        (1, (1, 2, 0, 0)),
        (1, (1, 2, 1, 0)),
        (1, (1, 2, 1, 1)),
        (1, (1, 2, 2, 0)),
        (1, (2, 0, 0, 0)),
        (1, (2, 0, 0, 1)),
        (1, (2, 1, 0, 0)),
        (1, (2, 1, 0, 1)),
        (2, (2, 2, 0, 0)),
    ),
    # t=2 variable-case eps encoding polynomial e (deg <= 5, weight 19)
    2: (
        (1, (0, 0, 0, 0)),
        (2, (0, 0, 0, 2)),
        (2, (0, 0, 1, 1)),
        (1, (0, 0, 2, 0)),
        (2, (0, 1, 1, 1)),
        (1, (0, 1, 2, 0)),
        (2, (0, 2, 2, 0)),
        (1, (1, 0, 0, 0)),
        (1, (1, 0, 0, 2)),
        (2, (1, 0, 1, 1)),
        (1, (1, 1, 0, 0)),
        (1, (1, 1, 2, 0)),
        (2, (1, 2, 0, 0)),
        (2, (1, 2, 1, 1)),
        (2, (1, 2, 2, 0)),
        (2, (2, 0, 0, 0)),
        (2, (2, 0, 0, 2)),
        (2, (2, 1, 0, 0)),
        (1, (2, 2, 0, 0)),
    ),
}

_SIMPLE_FAMILY_SIGN_CONST_P_TERMS: dict[int, tuple[F3SparsePolyTerm, ...]] = {
    # Constant-line cases: sign = chi(P) where P is a small F3 polynomial.
    # t=1 constant-case sign polynomial P (deg <= 2, weight 10)
    1: (
        (2, (0, 0, 0, 0)),
        (2, (0, 0, 0, 2)),
        (1, (0, 0, 1, 0)),
        (2, (0, 0, 1, 1)),
        (2, (0, 1, 0, 1)),
        (1, (0, 1, 1, 0)),
        (1, (0, 2, 0, 0)),
        (1, (1, 0, 0, 0)),
        (1, (1, 0, 0, 1)),
        (1, (1, 1, 0, 0)),
    ),
    # t=2 constant-case sign polynomial P (deg <= 2, weight 5)
    2: (
        (2, (0, 0, 0, 2)),
        (2, (0, 0, 1, 1)),
        (2, (0, 2, 0, 0)),
        (2, (1, 0, 0, 0)),
        (2, (1, 1, 0, 0)),
    ),
}


def predict_simple_family_sign_closed_form(c_i: int, match_i: int, other_i: int) -> int:
    """Closed-form sign(c,match,other) ∈ {+1,-1} for the CE2 simple family."""
    e6id_to_vec, _ = _heisenberg_vec_maps()
    uc1, uc2, _zc = e6id_to_vec[int(c_i)]
    um1, um2, zm = e6id_to_vec[int(match_i)]
    uo1, uo2, zo = e6id_to_vec[int(other_i)]

    t = 1 if (int(um1), int(um2)) == (int(uo1), int(uo2)) else 2
    d1 = (int(um1) - int(uc1)) % 3
    d2 = (int(um2) - int(uc2)) % 3
    d = (int(d1), int(d2))

    constant_line = False
    if d1 != 0:
        constant_line = _f3_omega((uc1, uc2), d) == _f3_k_of_direction(d)

    if constant_line:
        poly = _SIMPLE_FAMILY_SIGN_CONST_P_TERMS[int(t)]
        p = _eval_f3_sparse_poly(uc1, uc2, d1, d2, poly)
        return _f3_chi(p)

    c0 = _eval_f3_sparse_poly(uc1, uc2, d1, d2, _SIMPLE_FAMILY_SIGN_C0_TERMS[int(t)])
    e = _eval_f3_sparse_poly(uc1, uc2, d1, d2, _SIMPLE_FAMILY_SIGN_EPS_TERMS[int(t)])
    eps = _f3_chi(e)
    zsum = (int(zm) + int(zo)) % 3
    return int(eps) * _f3_chi((int(zsum) + int(c0)) % 3)


def predict_simple_family_sign(c_i: int, match_i: int, other_i: int) -> int:
    """Return sign(c,match,other) ∈ {+1,-1} for the CE2 simple family.

    Preference order:
      1) Closed-form symplectic/Heisenberg law (degree ≤ 5, sparse)
      2) Explicit GF(2) polynomial (degree ≤ 4) if the artifact is present
      3) Compact committed sign map (864-entry table)
      4) Fallback extraction from sparse CE2 local solutions
    """
    return predict_simple_family_sign_closed_form(int(c_i), int(match_i), int(other_i))

    coeff_mask = _simple_family_sign_poly_coeff_mask()
    if coeff_mask is not None:
        bits = _encode_simple_family_sign_input_bits(
            int(c_i), int(match_i), int(other_i)
        )
        parity = _eval_simple_family_sign_poly_bit(bits)
        return 1 if parity == 0 else -1
    return _simple_family_sign_map()[(int(c_i), int(match_i), int(other_i))]


def predict_simple_family_uv(
    a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]
) -> CE2SparseUV | None:
    """Predict the dominant CE2 simple-family U/V sparse correction for (a,b,c).

    The input is three (e6id, sl3_index) pairs.

    Returns:
      - SimpleFamilyUV(U=[...], V=[...]) if the triple matches the simple family
      - None otherwise
    """
    a_i, a_j = int(a[0]), int(a[1])
    b_i, b_j = int(b[0]), int(b[1])
    c_i, c_j = int(c[0]), int(c[1])

    # Exactly one g1 must match the sl3 index of c.
    if a_j == c_j and b_j != c_j:
        match_i, other_i = a_i, b_i
        side = "V"
    elif b_j == c_j and a_j != c_j:
        match_i, other_i = b_i, a_i
        side = "U"
    else:
        return None

    e6id_to_vec, vec_to_e6id = _heisenberg_vec_maps()
    v_row = _vec_sub(
        _vec_add(e6id_to_vec[match_i], e6id_to_vec[other_i]), e6id_to_vec[c_i]
    )
    row = int(vec_to_e6id[v_row])
    col = int(other_i)
    flat = int(row) * 27 + int(col)

    s = predict_simple_family_sign(int(c_i), int(match_i), int(other_i))
    coeff = Fraction(int(s), 54)

    if side == "U":
        return CE2SparseUV(U=[(flat, coeff)], V=[])
    return CE2SparseUV(U=[], V=[(flat, coeff)])


def predict_fiber_family_uv(
    a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]
) -> CE2SparseUV | None:
    """Predict the 1/108 fiber-family CE2 correction (supported on bad9 fibers).

    This family occurs exactly when:
      - exactly one of a_j,b_j matches c_j  (same as the simple family), AND
      - the three involved E6 ids lie in the same Heisenberg fiber u ∈ F3^2, AND
      - exactly one of the g1 E6 ids equals c_i (so {a_i,b_i,c_i} has 2 distinct points
        inside that fiber triad).

    Output:
      - one e6 matrix unit with +1/108 (in the same side as the matching g1)
      - one sl3 matrix unit with ±1/108, whose placement across U/V depends on whether
        match_i==c_i or other_i==c_i.
    """
    a_i, a_j = int(a[0]), int(a[1])
    b_i, b_j = int(b[0]), int(b[1])
    c_i, c_j = int(c[0]), int(c[1])

    # Exactly one g1 must match the sl3 index of c.
    if a_j == c_j and b_j != c_j:
        match_i, match_j = a_i, a_j
        other_i, other_j = b_i, b_j
        e6_side = "V"
    elif b_j == c_j and a_j != c_j:
        match_i, match_j = b_i, b_j
        other_i, other_j = a_i, a_j
        e6_side = "U"
    else:
        return None

    e6id_to_vec, _vec_to_e6id = _heisenberg_vec_maps()
    u_match = e6id_to_vec[match_i][:2]
    u_other = e6id_to_vec[other_i][:2]
    u_c = e6id_to_vec[c_i][:2]
    if not (u_match == u_other == u_c):
        return None

    match_eq = match_i == c_i
    other_eq = other_i == c_i
    if match_eq == other_eq:
        return None

    e6_idx: int
    sl3_idx: int
    sl3_coeff: Fraction
    sl3_side: str

    # e6 is always +1/108.
    e6_coeff = Fraction(1, 108)

    if match_eq:
        # match_i == c_i: diagonal e6[other,other] and positive sl3[other_j,other_j]
        e6_idx = _flat_e6(other_i, other_i)
        sl3_idx = _flat_sl3(other_j, other_j)
        sl3_coeff = Fraction(1, 108)
        sl3_side = e6_side
    else:
        # other_i == c_i: off-diagonal e6[match,other] and negative sl3[other_j,c_j]
        e6_idx = _flat_e6(match_i, other_i)
        sl3_idx = _flat_sl3(other_j, c_j)
        sl3_coeff = Fraction(-1, 108)
        sl3_side = "U" if e6_side == "V" else "V"

    if e6_side == "U":
        U = [(e6_idx, e6_coeff)]
        V = []
    else:
        U = []
        V = [(e6_idx, e6_coeff)]

    if sl3_side == "U":
        U.append((sl3_idx, sl3_coeff))
    else:
        V.append((sl3_idx, sl3_coeff))

    # stable ordering for deterministic output
    U.sort(key=lambda kv: kv[0])
    V.sort(key=lambda kv: kv[0])
    return CE2SparseUV(U=U, V=V)


def predict_ce2_uv(
    a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]
) -> CE2SparseUV | None:
    """Predict CE2 sparse (U,V) from global laws.

    Precedence matters: the fiber-family overrides the simple-family when both
    sl3-index conditions hold.
    """
    uv = predict_fiber_family_uv(a, b, c)
    if uv is not None:
        return uv
    return predict_simple_family_uv(a, b, c)
