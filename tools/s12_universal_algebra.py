#!/usr/bin/env python3
"""Core utilities for the Golay s12 model and its universal grade laws.

This module makes the s12 algebra checks reusable and testable:
- construct linear F3 codes from generator matrices,
- build the grade-defined bracket model used in repo s12 scripts,
- verify universal (grade-only) Lie/Jordan identities,
- run finite exhaustive checks on the ternary Golay instance.
"""
from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Any


def ternary_golay_generator_matrix() -> list[list[int]]:
    """Systematic 6x12 generator matrix for the ternary Golay code G_12."""
    return [
        [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 1, 2, 1, 0, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 0, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 0],
    ]


def _validate_generator(generator: list[list[int]]) -> tuple[int, int]:
    if not generator:
        raise ValueError("Generator matrix must be non-empty.")
    row_len = len(generator[0])
    if row_len == 0:
        raise ValueError("Generator matrix rows must be non-empty.")
    for row in generator:
        if len(row) != row_len:
            raise ValueError("Generator matrix rows must have equal length.")
        for val in row:
            if int(val) not in (0, 1, 2):
                raise ValueError("Generator entries must be in F3={0,1,2}.")
    return len(generator), row_len


def enumerate_linear_code_f3(generator: list[list[int]]) -> list[tuple[int, ...]]:
    """Enumerate all linear combinations over F3 of generator rows."""
    k, n = _validate_generator(generator)
    codewords = set()
    for coeffs in product(range(3), repeat=k):
        word = [0] * n
        for row_idx, coeff in enumerate(coeffs):
            if coeff == 0:
                continue
            row = generator[row_idx]
            for col_idx, val in enumerate(row):
                word[col_idx] = (word[col_idx] + coeff * int(val)) % 3
        codewords.add(tuple(word))
    return sorted(codewords)


def grade_mod3(word: tuple[int, ...]) -> int:
    """Grade map used in existing s12 scripts: sum(word) mod 3."""
    return int(sum(int(x) for x in word) % 3)


def omega(grade_i: int, grade_j: int) -> int:
    """Grade-level bracket coefficient used in repo's s12 model."""
    i = int(grade_i) % 3
    j = int(grade_j) % 3
    if i == 0 or j == 0:
        return 0
    return 1 if i <= j else 2


def add_words_mod3(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((int(a[idx]) + int(b[idx])) % 3 for idx in range(len(a)))


def bracket(x: tuple[int, ...], y: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    """Return [x,y] = coeff * (x+y) in basis form."""
    coeff = omega(grade_mod3(x), grade_mod3(y))
    return add_words_mod3(x, y), int(coeff)


def _nested_bracket(
    x: tuple[int, ...], y: tuple[int, ...], z: tuple[int, ...]
) -> dict[tuple[int, ...], int]:
    """Compute [[x,y],z] as a sparse linear combination over F3."""
    xy_word, c_xy = bracket(x, y)
    if c_xy == 0:
        return {}
    xyz_word, c_xyz = bracket(xy_word, z)
    coeff = (c_xy * c_xyz) % 3
    if coeff == 0:
        return {}
    return {xyz_word: coeff}


def _add_linear_terms(
    lhs: dict[tuple[int, ...], int], rhs: dict[tuple[int, ...], int]
) -> dict[tuple[int, ...], int]:
    out = dict(lhs)
    for key, coeff in rhs.items():
        out[key] = (out.get(key, 0) + int(coeff)) % 3
        if out[key] == 0:
            del out[key]
    return out


def jordan_triple(
    x: tuple[int, ...], y: tuple[int, ...], z: tuple[int, ...]
) -> dict[tuple[int, ...], int]:
    """Jordan triple {x,y,z} = [[x,y],z] + [[z,y],x] as sparse linear combo."""
    term1 = _nested_bracket(x, y, z)
    term2 = _nested_bracket(z, y, x)
    return _add_linear_terms(term1, term2)


def ad_power(
    x: tuple[int, ...], y: tuple[int, ...], power: int
) -> tuple[tuple[int, ...], int]:
    """Compute ad_x^power(y) as one basis word with a coefficient."""
    cur_word = y
    cur_coeff = 1
    for _ in range(int(power)):
        next_word, next_coeff = bracket(x, cur_word)
        cur_word = next_word
        cur_coeff = (cur_coeff * next_coeff) % 3
        if cur_coeff == 0:
            return cur_word, 0
    return cur_word, int(cur_coeff)


def verify_universal_grade_laws() -> dict[str, Any]:
    """Verify identities that depend only on grades and omega."""
    jacobi_failures: list[dict[str, Any]] = []
    ad3_failures = []
    jordan_symmetry_failures = []

    for i, j, k in product(range(3), repeat=3):
        lhs = (
            omega(j, k) * omega(i, (j + k) % 3)
            + omega(k, i) * omega(j, (k + i) % 3)
            + omega(i, j) * omega(k, (i + j) % 3)
        ) % 3
        if lhs != 0:
            jacobi_failures.append(
                {"grades": [int(i), int(j), int(k)], "jacobi_coeff_mod3": int(lhs)}
            )

        lhs_j = (
            omega(i, j) * omega((i + j) % 3, k) + omega(k, j) * omega((k + j) % 3, i)
        ) % 3
        rhs_j = (
            omega(k, j) * omega((k + j) % 3, i) + omega(i, j) * omega((i + j) % 3, k)
        ) % 3
        if lhs_j != rhs_j:
            jordan_symmetry_failures.append((i, j, k, int(lhs_j), int(rhs_j)))

    for i, j in product(range(3), repeat=2):
        coeff = (omega(i, j) * omega(i, (i + j) % 3) * omega(i, (2 * i + j) % 3)) % 3
        if coeff != 0:
            ad3_failures.append((i, j, int(coeff)))

    return {
        "jacobi_coefficient_identity_holds": len(jacobi_failures) == 0,
        "jacobi_failure_count": len(jacobi_failures),
        "jacobi_failures": jacobi_failures,
        "ad3_coefficient_identity_holds": len(ad3_failures) == 0,
        "ad3_failure_count": len(ad3_failures),
        "jordan_triple_xz_symmetry_holds": len(jordan_symmetry_failures) == 0,
        "jordan_symmetry_failure_count": len(jordan_symmetry_failures),
        "checked_grade_triples": 27,
        "checked_grade_pairs": 9,
    }


def _deterministic_triples(
    elems: list[tuple[int, ...]], limit: int
) -> list[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    n = len(elems)
    out = []
    for t in range(max(0, int(limit))):
        x = elems[(17 * t + 3) % n]
        y = elems[(29 * t + 5) % n]
        z = elems[(43 * t + 7) % n]
        out.append((x, y, z))
    return out


def build_s12_universal_report(jordan_sample_limit: int = 4000) -> dict[str, Any]:
    """Build a full report for the ternary Golay s12 model."""
    generator = ternary_golay_generator_matrix()
    codewords = enumerate_linear_code_f3(generator)
    zero = tuple([0] * len(generator[0]))
    nonzero = [cw for cw in codewords if cw != zero]

    by_grade = {grade: [] for grade in (0, 1, 2)}
    for cw in nonzero:
        by_grade[grade_mod3(cw)].append(cw)

    g0 = by_grade[0]
    g1 = by_grade[1]
    g2 = by_grade[2]
    g12 = g1 + g2

    # Bracket symmetry checks
    sym_11_pass = 0
    sym_11_total = 0
    for x in g1:
        for y in g1:
            r_xy, c_xy = bracket(x, y)
            r_yx, c_yx = bracket(y, x)
            sym_11_total += 1
            if r_xy == r_yx and c_xy == c_yx:
                sym_11_pass += 1

    sym_22_pass = 0
    sym_22_total = 0
    for x in g2:
        for y in g2:
            r_xy, c_xy = bracket(x, y)
            r_yx, c_yx = bracket(y, x)
            sym_22_total += 1
            if r_xy == r_yx and c_xy == c_yx:
                sym_22_pass += 1

    anti_12_pass = 0
    anti_12_total = 0
    for x in g1:
        for y in g2:
            r_xy, c_xy = bracket(x, y)
            r_yx, c_yx = bracket(y, x)
            anti_12_total += 1
            if r_xy == r_yx and ((c_xy + c_yx) % 3 == 0):
                anti_12_pass += 1

    # Centrality of g0
    g0_central_pass = 0
    g0_central_total = 0
    for x in g0:
        for y in g12:
            _, coeff = bracket(x, y)
            g0_central_total += 1
            if coeff == 0:
                g0_central_pass += 1

    # ad^3 = 0 on g1
    ad3_zero_pass = 0
    ad3_zero_total = 0
    ad2_nonzero_count = 0
    ad2_grade_hist = Counter()
    for x in g1:
        for y in g1:
            w3, c3 = ad_power(x, y, 3)
            ad3_zero_total += 1
            if c3 == 0 or w3 == zero:
                ad3_zero_pass += 1

            w2, c2 = ad_power(x, y, 2)
            if c2 != 0 and w2 != zero:
                ad2_nonzero_count += 1
                ad2_grade_hist[str(grade_mod3(w2))] += 1

    # Jordan symmetry sampling
    jordan_pass = 0
    jordan_total = 0
    jordan_triples = _deterministic_triples(g1, jordan_sample_limit)
    for x, y, z in jordan_triples:
        lhs = jordan_triple(x, y, z)
        rhs = jordan_triple(z, y, x)
        jordan_total += 1
        if lhs == rhs:
            jordan_pass += 1

    report = {
        "status": "ok",
        "model": "Golay grade-defined Jordan-Lie s12",
        "generator_shape": [len(generator), len(generator[0])],
        "code_size": len(codewords),
        "algebra_dimensions": {
            "total_nonzero": len(nonzero),
            "grade0": len(g0),
            "grade1": len(g1),
            "grade2": len(g2),
            "quotient_by_grade0": len(g1) + len(g2),
        },
        "universal_grade_laws": verify_universal_grade_laws(),
        "exhaustive_checks": {
            "g1_g1_symmetric": {
                "holds": sym_11_pass == sym_11_total,
                "pass": sym_11_pass,
                "total": sym_11_total,
            },
            "g2_g2_symmetric": {
                "holds": sym_22_pass == sym_22_total,
                "pass": sym_22_pass,
                "total": sym_22_total,
            },
            "g1_g2_antisymmetric": {
                "holds": anti_12_pass == anti_12_total,
                "pass": anti_12_pass,
                "total": anti_12_total,
            },
            "g0_central": {
                "holds": g0_central_pass == g0_central_total,
                "pass": g0_central_pass,
                "total": g0_central_total,
            },
            "ad3_zero_on_g1": {
                "holds": ad3_zero_pass == ad3_zero_total,
                "pass": ad3_zero_pass,
                "total": ad3_zero_total,
            },
            "ad2_nontrivial_on_g1": {
                "nonzero_count": ad2_nonzero_count,
                "total": len(g1) * len(g1),
                "nonzero_rate": (
                    ad2_nonzero_count / float(len(g1) * len(g1)) if len(g1) > 0 else 0.0
                ),
                "target_grade_histogram": dict(ad2_grade_hist),
            },
            "jordan_triple_xz_symmetry_sample": {
                "holds": jordan_pass == jordan_total,
                "pass": jordan_pass,
                "total": jordan_total,
            },
        },
    }
    return report
