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
  - Sign is currently loaded from the committed sparse CE2 data and is
    deterministic on the ordered triple (c, match, other).

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

    s = _simple_family_sign_map()[(int(c_i), int(match_i), int(other_i))]
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
