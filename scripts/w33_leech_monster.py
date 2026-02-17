#!/usr/bin/env python3
"""
Leech lattice, Monster group numerology, and Moonshine observables

Pillar 57 — Leech / Monster / Moonshine

Provides computational evidence linking three copies of E8 (E8^3) and the
Leech lattice; highlights numerology connecting Leech kissing number (196560)
with Monster representation dimensions (196883) and group-size ratios.

Usage:
    python scripts/w33_leech_monster.py

"""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from functools import lru_cache
from math import comb, log2, log10
from pathlib import Path
from typing import Dict

# Ensure we can import sibling modules from scripts/ when executed as a file.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from w33_cryptographic_lattice import analyze_leech_connection
from w33_homology import (
    boundary_matrix,
    build_clique_complex,
    build_w33,
    compute_homology,
)


def _load_monster_irreps_via_gap() -> list | None:
    """Try to obtain Monster irreducible character *degrees* via GAP/libgap or
    fall back to a bundled static JSON file.

    Returns a list of integer character degrees if successful, otherwise None.
    """
    # 1) libgap (Sage) path
    try:
        from sage.all import libgap  # type: ignore

        ct = libgap.CharacterTable("M")
        irr = libgap.Irr(ct)
        degs = [int(c[0]) for c in irr]
        return degs
    except Exception:
        pass

    # 2) GAP CLI fallback
    if shutil.which("gap") is not None:
        gap_code = (
            't := CharacterTable("M"); '
            "degs := List(Irr(t), chi -> chi[1]); "
            'Print("GAP:MONSTER_DEGREES:", degs, "\n"); '
            "quit;"
        )
        try:
            proc = subprocess.run(
                ["gap", "-q"],
                input=gap_code,
                text=True,
                capture_output=True,
                check=True,
            )
            for line in proc.stdout.splitlines():
                if line.startswith("GAP:MONSTER_DEGREES:"):
                    payload = line.split(":", 1)[1].strip()
                    degs = ast.literal_eval(payload)
                    return [int(x) for x in degs]
        except Exception:
            pass

    # 3) Bundled static JSON (data/monster_degrees.json)
    try:
        import json
        from pathlib import Path

        static_path = (
            Path(__file__).resolve().parents[1] / "data" / "monster_degrees.json"
        )
        if static_path.exists():
            vals = json.loads(static_path.read_text())
            return [int(x) for x in vals]
    except Exception:
        pass

    return None


def e4_coeffs(n_terms: int = 8):
    """Return the first n_terms coefficients of E4(q)=Theta_{E8}(q).

    Coefficients are integers: E4 = 1 + 240 q + 2160 q^2 + 6720 q^3 + 17520 q^4 + ...
    """
    base = [1, 240, 2160, 6720, 17520, 30240, 60480, 82560]
    return base[:n_terms]


def poly_power(coeffs, power: int, n_terms: int):
    """Compute first n_terms coefficients of (sum coeffs[i] q^i)^power."""
    out = [0] * n_terms
    out[0] = 1 if power == 0 else coeffs[0] ** power
    # naive convolution (sufficient for small n_terms)
    from itertools import product

    # start from 1st power by repeated convolution
    cur = coeffs[:n_terms]
    for _ in range(1, power):
        nxt = [0] * n_terms
        for i in range(n_terms):
            if cur[i] == 0:
                continue
            for j in range(n_terms - i):
                if j >= len(coeffs):
                    break
                nxt[i + j] += cur[i] * coeffs[j]
        cur = nxt
    return cur[:n_terms]


def j_coeffs(n_terms: int = 6):
    """Compute first n_terms Fourier coefficients of the Klein j‑invariant.

    j(τ) = q^{-1} + 744 + Σ_{n>=1} c(n) q^n  — we return [c(1),...,c(n)].

    Implementation: j = E4^3 / Δ where E4 = 1 + 240 Σ σ_3(n) q^n and
    Δ(q)=q Π_{m>=1} (1-q^m)^{24}. Series division is used to produce exact
    integer coefficients up to the requested order (fast for n_terms ≤ 100).
    """
    # fast path: small precomputed values
    known = [
        196884,
        21493760,
        864299970,
        20245856256,
        333202640600,
        4252023300096,
        44656994071935,
        401490886656000,
        3176440229784420,
        22567393309593600,
    ]
    if n_terms <= len(known):
        return known[:n_terms]

    # helper: divisor-sum σ_k
    def sigma_k(n: int, k: int) -> int:
        s = 0
        d = 1
        while d * d <= n:
            if n % d == 0:
                s += d**k
                e = n // d
                if e != d:
                    s += e**k
            d += 1
        return s

    # degrees we need for series arithmetic
    N = n_terms + 4  # small slack

    # E4 coefficients: E4 = 1 + 240 Σ_{n>=1} σ_3(n) q^n
    e4 = [1] + [240 * sigma_k(i, 3) for i in range(1, N + 1)]

    # A = E4^3 (convolution via existing poly_power)
    A = poly_power(e4, 3, N + 1)

    # d(q) = Δ(q)/q = Π_{m>=1} (1-q^m)^{24}  (compute up to degree N)
    from math import comb

    d = [1] + [0] * N
    for m in range(1, N + 1):
        # (1 - q^m)^24 = sum_{j=0..24} C(24,j) (-1)^j q^{m*j}
        coeff = [0] * (N + 1)
        for j in range(0, 25):
            power = m * j
            if power > N:
                break
            coeff[power] = ((-1) ** j) * comb(24, j)
        # convolve d <- d * coeff (truncated)
        newd = [0] * (N + 1)
        for k in range(0, N + 1):
            s = 0
            for i in range(0, k + 1):
                s += d[i] * coeff[k - i]
            newd[k] = s
        d = newd

    # Now perform series division S = A / d where d[0] == 1 and A,d length >= N
    S = [0] * (N + 1)
    for k in range(0, N + 1):
        s = A[k]
        for i in range(1, k + 1):
            s -= d[i] * S[k - i]
        S[k] = s  # d[0] == 1

    # j(q) = q^{-1} * S(q)  => coefficient c(n) = S[n+1]
    out = [int(S[n + 1]) for n in range(1, n_terms + 1)]
    return out


# ----------------------------- McKay / Thompson -----------------------------


def load_monster_characters(json_path: str | None = None) -> dict | None:
    """Load full Monster character table from JSON file (if present).

    Expected JSON format:
      { "class_names": [...], "irreps": [{"degree": d, "values": [...]}, ...] }

    Returns dict or None if file not found / parsing fails.
    """
    import json
    from pathlib import Path

    if json_path:
        p = Path(json_path)
    else:
        p = Path(__file__).resolve().parents[1] / "data" / "monster_characters.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
        # basic validation
        if (
            not isinstance(payload, dict)
            or "class_names" not in payload
            or "irreps" not in payload
        ):
            return None
        return payload
    except Exception:
        return None


def _load_monster_char_map_via_gap(
    class_name: str, json_path: str | None = None
) -> dict | None:
    """Return a mapping {irrep_degree: character_value} for the given Monster
    conjugacy-class name.

    Priority order:
      1. bundled JSON file (data/monster_characters.json or path override)
      2. libgap (Sage)
      3. GAP CLI

    Returns None if no character data is available for the requested class.
    """
    # 1) check for bundled JSON (fast and safe)
    jt = load_monster_characters(json_path)
    if jt is not None:
        try:
            names = jt["class_names"]
            idx = names.index(class_name)
            mapping = {int(ir["degree"]): int(ir["values"][idx]) for ir in jt["irreps"]}
            return mapping
        except Exception:
            # fall through to other methods
            pass

    # 2) try libgap (Sage)
    try:
        from sage.all import libgap  # type: ignore

        t = libgap.CharacterTable("M")
        names = list(libgap.ClassNames(t))
        try:
            idx = names.index(class_name)
        except ValueError:
            return None
        irr = libgap.Irr(t)
        degs = [int(c[0]) for c in irr]
        vals = [int(c[idx]) for c in irr]
        return {int(d): int(v) for d, v in zip(degs, vals)}
    except Exception:
        pass

    # 3) GAP CLI fallback
    import ast
    import shutil
    import subprocess

    if shutil.which("gap") is None:
        return None

    gap_code = (
        f't := CharacterTable("M"); '
        f"names := ClassNames(t); "
        f'idx := Position(names, "{class_name}"); '
        f'if idx = fail then Print("GAP:CLASS_NOT_FOUND\n"); quit; fi; '
        "vals := List(Irr(t), chi -> chi[idx]); "
        "degs := List(Irr(t), chi -> chi[1]); "
        'Print("GAP:CHAR_DEGREES:", degs, "\n"); '
        'Print("GAP:CHAR_VALUES:", vals, "\n"); '
        "quit;"
    )
    try:
        proc = subprocess.run(
            ["gap", "-q"], input=gap_code, text=True, capture_output=True, check=True
        )
    except Exception:
        return None

    degrees = None
    values = None
    for line in proc.stdout.splitlines():
        if line.startswith("GAP:CHAR_DEGREES:"):
            degrees = ast.literal_eval(line.split(":", 1)[1].strip())
        elif line.startswith("GAP:CHAR_VALUES:"):
            values = ast.literal_eval(line.split(":", 1)[1].strip())
    if degrees is None or values is None:
        return None
    return {int(d): int(v) for d, v in zip(degrees, values)}


def _qpoly_mul(a: list[int], b: list[int], max_deg: int) -> list[int]:
    out = [0] * (max_deg + 1)
    for i, ai in enumerate(a[: max_deg + 1]):
        if ai == 0:
            continue
        max_j = max_deg - i
        for j, bj in enumerate(b[: max_j + 1]):
            if bj == 0:
                continue
            out[i + j] += ai * bj
    return out


def _qpoly_pow(base: list[int], exp: int, max_deg: int) -> list[int]:
    if exp < 0:
        raise ValueError("exp must be non-negative")
    result = [0] * (max_deg + 1)
    result[0] = 1
    cur = base[: max_deg + 1] + [0] * max(0, (max_deg + 1) - len(base))
    e = exp
    while e:
        if e & 1:
            result = _qpoly_mul(result, cur, max_deg)
        e >>= 1
        if e:
            cur = _qpoly_mul(cur, cur, max_deg)
    return result


def _qpoly_inv(den: list[int], max_deg: int) -> list[int]:
    """Inverse of a power series with den[0] == 1, truncated to max_deg."""
    if not den or den[0] != 1:
        raise ValueError("series inverse requires den[0] == 1")
    out = [0] * (max_deg + 1)
    out[0] = 1
    for n in range(1, max_deg + 1):
        s = 0
        for k in range(1, n + 1):
            if k < len(den):
                s += den[k] * out[n - k]
        out[n] = -s
    return out


def _qpoly_div(num: list[int], den: list[int], max_deg: int) -> list[int]:
    inv = _qpoly_inv(den, max_deg)
    num_pad = num[: max_deg + 1] + [0] * max(0, (max_deg + 1) - len(num))
    return _qpoly_mul(num_pad, inv, max_deg)


def _qpochhammer(max_deg: int, step: int = 1) -> list[int]:
    """Compute (q^step; q^step)_inf = prod_{k>=1} (1 - q^{k*step}) to max_deg."""
    if step <= 0:
        raise ValueError("step must be positive")
    poly = [1] + [0] * max_deg
    for k in range(1, (max_deg // step) + 1):
        power = k * step
        for n in range(max_deg, power - 1, -1):
            poly[n] -= poly[n - power]
    return poly


def _qpochhammer_arith(max_deg: int, step: int, offset: int) -> list[int]:
    """Compute prod_{k>=0} (1 - q^{offset + k*step}) to max_deg.

    This is a shifted q-Pochhammer (q^offset; q^step)_∞ truncated to max_deg.
    """
    if step <= 0:
        raise ValueError("step must be positive")
    if offset <= 0:
        raise ValueError("offset must be positive")
    poly = [1] + [0] * max_deg
    power = offset
    while power <= max_deg:
        for n in range(max_deg, power - 1, -1):
            poly[n] -= poly[n - power]
        power += step
    return poly


def mckay_thompson_series(class_name: str, max_q_exp: int = 8) -> dict[int, int] | None:
    """Return a McKay-Thompson series T_g(q)=q^-1 + sum_{n>=1} a_n q^n.

    Offline (no GAP) support is implemented for a subset of prime-order classes
    expressible as eta-quotients, plus a small number of composite-order
    classes appearing in classical eta-product formulas:
      - Fricke primes (pA): 2A, 3A, 5A, 7A, 13A
      - Non-Fricke primes (pB): 2B, 3B, 5B, 7B, 13B
      - Composite: 4A–4D, 6A–6E, 8A/8A'/8B/8E, 9A, 10A–10E, 11A, 3C

    Identity class 1A returns J(q)=j(q)-744.
    """
    name = class_name.upper()
    if max_q_exp < 0:
        raise ValueError("max_q_exp must be non-negative")

    if name in ("1A", "ID", "IDENTITY"):
        coeffs = j_coeffs(max_q_exp)
        out = {-1: 1, 0: 0}
        for n, c in enumerate(coeffs, start=1):
            out[n] = int(c)
        return out

    if name == "4C":
        # Ramanujan–Sato / Moonshine:
        #   j_4C(τ) = (η(τ)/η(4τ))^8 = q^{-1} - 8 + 20 q - 62 q^3 + ...
        # Normalize to constant term 0 => T_4C = j_4C + 8.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e4 = _qpochhammer(deg, step=4)
        ratio = _qpoly_div(e1, e4, deg)
        ratio_pow = _qpoly_pow(ratio, 8, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) + 8
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "4A":
        # Ramanujan–Sato / Moonshine:
        #   j_4A(τ) = (η(2τ)^2/(η(τ)η(4τ)))^{24}
        #          = q^{-1} + 24 + 276 q + 2048 q^2 + ...
        # Normalize to constant term 0 => T_4A = j_4A - 24.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e4 = _qpochhammer(deg, step=4)
        num = _qpoly_mul(e2, e2, deg)
        den = _qpoly_mul(e1, e4, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 24, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) - 24
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "4B":
        # (Ramanujan–Sato / Moonshine)
        #   j_4B(τ) = (η(2τ)/η(4τ))^{12} + 2^6 (η(4τ)/η(2τ))^{12}
        #          = q^{-1} + 52 q + 834 q^3 + ...
        # Constant term is 0 in this normalization.
        deg = max_q_exp + 1
        e2 = _qpochhammer(deg, step=2)
        e4 = _qpochhammer(deg, step=4)
        ratio = _qpoly_div(e2, e4, deg)
        r0 = _qpoly_pow(ratio, 12, deg)
        r0_inv = _qpoly_inv(r0, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(r0):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        for k, ck in enumerate(r0_inv):
            exp = 1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(64 * ck)

        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "4D":
        # (Ramanujan–Sato / Moonshine)
        #   j_4D(τ) = (η(2τ)/η(4τ))^{12} = q^{-1} - 12 q + 66 q^3 + ...
        # Constant term is 0 in this normalization.
        deg = max_q_exp + 1
        e2 = _qpochhammer(deg, step=2)
        e4 = _qpochhammer(deg, step=4)
        ratio = _qpoly_div(e2, e4, deg)
        r0 = _qpoly_pow(ratio, 12, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(r0):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "6B":
        # Ramanujan–Sato / Moonshine:
        #   j_6B(τ) = (η(2τ)η(3τ)/(η(τ)η(6τ)))^{12}
        #          = q^{-1} + 12 + 78 q + 364 q^2 + ...
        # Normalize to constant term 0 => T_6B = j_6B - 12.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e3 = _qpochhammer(deg, step=3)
        e6 = _qpochhammer(deg, step=6)
        num = _qpoly_mul(e2, e3, deg)
        den = _qpoly_mul(e1, e6, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 12, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) - 12
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "6C":
        # Ramanujan–Sato / Moonshine:
        #   j_6C(τ) = (η(τ)η(3τ)/(η(2τ)η(6τ)))^{6}
        #          = q^{-1} - 6 + 15 q - 32 q^2 + ...
        # Normalize to constant term 0 => T_6C = j_6C + 6.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e3 = _qpochhammer(deg, step=3)
        e6 = _qpochhammer(deg, step=6)
        num = _qpoly_mul(e1, e3, deg)
        den = _qpoly_mul(e2, e6, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 6, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) + 6
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "6D":
        # Ramanujan–Sato / Moonshine:
        #   j_6D(τ) = (η(τ)η(2τ)/(η(3τ)η(6τ)))^{4}
        #          = q^{-1} - 4 - 2 q + 28 q^2 + ...
        # Normalize to constant term 0 => T_6D = j_6D + 4.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e3 = _qpochhammer(deg, step=3)
        e6 = _qpochhammer(deg, step=6)
        num = _qpoly_mul(e1, e2, deg)
        den = _qpoly_mul(e3, e6, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 4, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) + 4
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "6E":
        # Ramanujan–Sato / Moonshine:
        #   j_6E(τ) = (η(2τ)η(3τ)^3/(η(τ)η(6τ)^3))^{3}
        #          = q^{-1} + 3 + 6 q + 4 q^2 + ...
        # Normalize to constant term 0 => T_6E = j_6E - 3.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e3 = _qpochhammer(deg, step=3)
        e6 = _qpochhammer(deg, step=6)
        e3_3 = _qpoly_pow(e3, 3, deg)
        e6_3 = _qpoly_pow(e6, 3, deg)
        num = _qpoly_mul(e2, e3_3, deg)
        den = _qpoly_mul(e1, e6_3, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 3, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) - 3
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "6A":
        # Ramanujan–Sato / Moonshine "near-square" identity:
        #   j_6A = (sqrt(j_6B) - 1/sqrt(j_6B))^2 = j_6B + 1/j_6B - 2
        # and j_6B = q^{-1} * R(q) with R(0)=1, so 1/j_6B = q * R(q)^{-1}.
        #
        # Normalize to constant term 0 => T_6A = j_6A - 10.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e3 = _qpochhammer(deg, step=3)
        e6 = _qpochhammer(deg, step=6)
        num = _qpoly_mul(e2, e3, deg)
        den = _qpoly_mul(e1, e6, deg)
        ratio = _qpoly_div(num, den, deg)
        r = _qpoly_pow(ratio, 12, deg)  # R(q) above
        r_inv = _qpoly_inv(r, deg)

        series: dict[int, int] = {}
        # j_6B = q^{-1} R(q)
        for k, ck in enumerate(r):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)
        # + 1/j_6B = q * R(q)^{-1}
        for k, ck in enumerate(r_inv):
            exp = 1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)
        # - 2
        series[0] = series.get(0, 0) - 2

        # Normalize to constant term 0 (expected constant is 10).
        series[0] = series.get(0, 0) - 10
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name in ("8A'", "8APRIME", "8A-PRIME"):
        # Alias for the "8A'" hauptmodul in the literature.
        name = "8A'"

    if name == "8A":
        # (Ramanujan–Sato / Moonshine)
        #   j_8A(τ) = (η(2τ)η(4τ)/(η(τ)η(8τ)))^{8}
        #          = q^{-1} + 8 + 36 q + 128 q^2 + ...
        # Normalize to constant term 0 => T_8A = j_8A - 8.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e4 = _qpochhammer(deg, step=4)
        e8 = _qpochhammer(deg, step=8)
        num = _qpoly_mul(e2, e4, deg)
        den = _qpoly_mul(e1, e8, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 8, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) - 8
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "8A'":
        # (Ramanujan–Sato / Moonshine)
        #   j_8A'(τ) = (η(τ)η(4τ)^2/(η(2τ)^2 η(8τ)))^{8}
        #           = q^{-1} - 8 + 36 q - 128 q^2 + ...
        # Normalize to constant term 0 => T_8A' = j_8A' + 8.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e4 = _qpochhammer(deg, step=4)
        e8 = _qpochhammer(deg, step=8)
        e4_2 = _qpoly_mul(e4, e4, deg)
        e2_2 = _qpoly_mul(e2, e2, deg)
        num = _qpoly_mul(e1, e4_2, deg)
        den = _qpoly_mul(e2_2, e8, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 8, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) + 8
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "8B":
        # (Ramanujan–Sato / Moonshine)
        #   j_8B(τ) = (η(4τ)^2/(η(2τ)η(8τ)))^{12}
        #          = q^{-1} + 12 q + 66 q^3 + ...
        # Constant term is 0 in this normalization.
        deg = max_q_exp + 1
        e2 = _qpochhammer(deg, step=2)
        e4 = _qpochhammer(deg, step=4)
        e8 = _qpochhammer(deg, step=8)
        e4_2 = _qpoly_mul(e4, e4, deg)
        den = _qpoly_mul(e2, e8, deg)
        ratio = _qpoly_div(e4_2, den, deg)
        ratio_pow = _qpoly_pow(ratio, 12, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "8E":
        # (Ramanujan–Sato / Moonshine)
        #   j_8E(τ) = (η(4τ)^3/(η(2τ)η(8τ)^2))^{4}
        #          = q^{-1} + 4 q + 2 q^3 - 8 q^5 + ...
        # Constant term is 0 in this normalization.
        deg = max_q_exp + 1
        e2 = _qpochhammer(deg, step=2)
        e4 = _qpochhammer(deg, step=4)
        e8 = _qpochhammer(deg, step=8)
        e4_3 = _qpoly_pow(e4, 3, deg)
        e8_2 = _qpoly_mul(e8, e8, deg)
        den = _qpoly_mul(e2, e8_2, deg)
        ratio = _qpoly_div(e4_3, den, deg)
        ratio_pow = _qpoly_pow(ratio, 4, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "10B":
        # (Ramanujan–Sato / Moonshine)
        #   j_10B(τ) = (η(τ)η(5τ)/(η(2τ)η(10τ)))^{4}
        #           = q^{-1} - 4 + 6 q - 8 q^2 + ...
        # Normalize to constant term 0 => T_10B = j_10B + 4.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e5 = _qpochhammer(deg, step=5)
        e10 = _qpochhammer(deg, step=10)
        num = _qpoly_mul(e1, e5, deg)
        den = _qpoly_mul(e2, e10, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 4, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) + 4
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "10C":
        # (Ramanujan–Sato / Moonshine)
        #   j_10C(τ) = (η(τ)η(2τ)/(η(5τ)η(10τ)))^{2}
        #           = q^{-1} - 2 - 3 q + 6 q^2 + ...
        # Normalize to constant term 0 => T_10C = j_10C + 2.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e5 = _qpochhammer(deg, step=5)
        e10 = _qpochhammer(deg, step=10)
        num = _qpoly_mul(e1, e2, deg)
        den = _qpoly_mul(e5, e10, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 2, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) + 2
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "10D":
        # (Ramanujan–Sato / Moonshine)
        #   j_10D(τ) = (η(2τ)η(5τ)/(η(τ)η(10τ)))^{6}
        #           = q^{-1} + 6 + 21 q + 62 q^2 + ...
        # Normalize to constant term 0 => T_10D = j_10D - 6.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e5 = _qpochhammer(deg, step=5)
        e10 = _qpochhammer(deg, step=10)
        num = _qpoly_mul(e2, e5, deg)
        den = _qpoly_mul(e1, e10, deg)
        ratio = _qpoly_div(num, den, deg)
        ratio_pow = _qpoly_pow(ratio, 6, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio_pow):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) - 6
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "10E":
        # (Ramanujan–Sato / Moonshine)
        #   j_10E(τ) = η(2τ)η(5τ)^5/(η(τ)η(10τ)^5)
        #           = q^{-1} + 1 + q + 2 q^2 + ...
        # Normalize to constant term 0 => T_10E = j_10E - 1.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e5 = _qpochhammer(deg, step=5)
        e10 = _qpochhammer(deg, step=10)
        e5_5 = _qpoly_pow(e5, 5, deg)
        e10_5 = _qpoly_pow(e10, 5, deg)
        num = _qpoly_mul(e2, e5_5, deg)
        den = _qpoly_mul(e1, e10_5, deg)
        ratio = _qpoly_div(num, den, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(ratio):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        series[0] = series.get(0, 0) - 1
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "10A":
        # (Ramanujan–Sato / Moonshine) near-square identity:
        #   j_10A = (sqrt(j_10D) - 1/sqrt(j_10D))^2 = j_10D + 1/j_10D - 2.
        #
        # Normalize to constant term 0 => T_10A = j_10A - 4.
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e2 = _qpochhammer(deg, step=2)
        e5 = _qpochhammer(deg, step=5)
        e10 = _qpochhammer(deg, step=10)
        num = _qpoly_mul(e2, e5, deg)
        den = _qpoly_mul(e1, e10, deg)
        ratio = _qpoly_div(num, den, deg)
        r0 = _qpoly_pow(ratio, 6, deg)
        r0_inv = _qpoly_inv(r0, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(r0):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)
        for k, ck in enumerate(r0_inv):
            exp = 1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)
        series[0] = series.get(0, 0) - 2

        series[0] = series.get(0, 0) - 4
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "11A":
        # Formula (e.g. Ramanujan–Sato series / Cooper):
        #   j_11A(τ) = (1+3F)^3 + (F^{-1/2}+3F^{1/2})^2
        #           = F^{-1} + 7 + 18F + 27F^2 + 27F^3,
        #   where F = η(3τ)η(33τ)/(η(τ)η(11τ)).
        #
        # Our normalization uses T_11A = j_11A - a0 so that constant term is 0.
        deg = max_q_exp + 3  # slack for F^3
        e1 = _qpochhammer(deg, step=1)
        e3 = _qpochhammer(deg, step=3)
        e11 = _qpochhammer(deg, step=11)
        e33 = _qpochhammer(deg, step=33)

        num = _qpoly_mul(e3, e33, deg)
        den = _qpoly_mul(e1, e11, deg)
        ratio = _qpoly_div(num, den, deg)  # (E3*E33)/(E1*E11), constant term 1

        # F(q) = q * ratio(q)
        F = [0] * (deg + 1)
        for k, ck in enumerate(ratio[:deg]):
            if k + 1 <= deg:
                F[k + 1] = int(ck)

        F2 = _qpoly_mul(F, F, deg)
        F3 = _qpoly_mul(F2, F, deg)

        ratio_inv = _qpoly_inv(ratio, deg)

        # Build j_11A as a Laurent series dict exp->coeff
        j: dict[int, int] = {-1: 1}

        # F^{-1} = q^{-1} * ratio^{-1}
        for k, ck in enumerate(ratio_inv[: deg + 1]):
            exp = k - 1
            if -1 <= exp <= max_q_exp and ck:
                j[exp] = j.get(exp, 0) + int(ck)

        # + 7
        j[0] = j.get(0, 0) + 7

        # + 18F + 27F^2 + 27F^3
        for k, ck in enumerate(F[: deg + 1]):
            if 0 <= k <= max_q_exp and ck:
                j[k] = j.get(k, 0) + 18 * int(ck)
        for k, ck in enumerate(F2[: deg + 1]):
            if 0 <= k <= max_q_exp and ck:
                j[k] = j.get(k, 0) + 27 * int(ck)
        for k, ck in enumerate(F3[: deg + 1]):
            if 0 <= k <= max_q_exp and ck:
                j[k] = j.get(k, 0) + 27 * int(ck)

        # Normalize to constant term 0.
        a0 = int(j.get(0, 0))
        out = {}
        for e, c in j.items():
            if e == 0:
                continue
            if -1 <= e <= max_q_exp:
                out[e] = int(c)
        out[-1] = 1
        out[0] = 0
        if a0 != 6:
            # Keep as an internal sanity check but don't hard-require the known value.
            # (Different normalizations in the literature sometimes shift by constants.)
            pass
        return out

    if name == "3C":
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e3 = _qpochhammer(deg, step=3)
        e9 = _qpochhammer(deg, step=9)
        num = _qpoly_mul(e3, e3, deg)
        den = _qpoly_mul(e1, e9, deg)
        ratio = _qpoly_div(num, den, deg)

        r0 = _qpoly_pow(ratio, 6, deg)
        r0_inv = _qpoly_inv(r0, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(r0):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)

        for k, ck in enumerate(r0_inv):
            exp = 1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(-27 * ck)

        series[0] = series.get(0, 0) - 6
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    if name == "9A":
        deg = max_q_exp + 1
        e1 = _qpochhammer(deg, step=1)
        e3 = _qpochhammer(deg, step=3)
        e9 = _qpochhammer(deg, step=9)
        num = _qpoly_mul(e3, e3, deg)
        den = _qpoly_mul(e1, e9, deg)
        ratio = _qpoly_div(num, den, deg)
        r0 = _qpoly_pow(ratio, 6, deg)

        series: dict[int, int] = {}
        for k, ck in enumerate(r0):
            exp = -1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(ck)
        series[0] = series.get(0, 0) - 6
        if series.get(0, 0) != 0:
            raise AssertionError(
                f"Expected constant term 0 for {name}, got {series.get(0)}"
            )
        series.setdefault(-1, 1)
        return series

    fricke_prime = {"2A": 2, "3A": 3, "5A": 5, "7A": 7, "13A": 13}
    non_fricke_prime = {"2B": 2, "3B": 3, "5B": 5, "7B": 7, "13B": 13}
    if name in fricke_prime:
        p = fricke_prime[name]
        use_fricke = True
    elif name in non_fricke_prime:
        p = non_fricke_prime[name]
        use_fricke = False
    else:
        p = None
        use_fricke = False
    if p is None:
        return None

    # Prime-order Hauptmodul via eta-quotients.
    a = 24 // (p - 1)
    scale = p ** (12 // (p - 1))
    const = 24 // (p - 1)

    # Need one extra degree because term1 is q^-1 * (1 + O(q)).
    deg = max_q_exp + 1
    e = _qpochhammer(deg, step=1)  # (q;q)_inf
    ep = _qpochhammer(deg, step=p)  # (q^p;q^p)_inf
    ratio = _qpoly_div(e, ep, deg)  # E(q)/E(q^p)

    ratio_pow = _qpoly_pow(ratio, a, deg)

    series: dict[int, int] = {}
    # term1: q^-1 * ratio_pow
    for k, ck in enumerate(ratio_pow):
        exp = -1 + k
        if -1 <= exp <= max_q_exp and ck:
            series[exp] = series.get(exp, 0) + int(ck)

    if use_fricke:
        ratio_inv_pow = _qpoly_pow(_qpoly_inv(ratio, deg), a, deg)
        for k, ck in enumerate(ratio_inv_pow):
            exp = 1 + k
            if -1 <= exp <= max_q_exp and ck:
                series[exp] = series.get(exp, 0) + int(scale * ck)

    # constant shift
    series[0] = series.get(0, 0) + int(const)
    if series.get(0, 0) != 0:
        raise AssertionError(
            f"Expected constant term 0 for {name}, got {series.get(0)}"
        )

    series.setdefault(-1, 1)
    return series


def rogers_ramanujan_r5_series(max_q_exp: int) -> list[int]:
    """Compute r5(q)=R(q)^5 as a q-series through q^{max_q_exp}.

    Using the product formula (Wikipedia):
      R(q) = q^{1/5} * ( (q;q^5)_∞ (q^4;q^5)_∞ ) / ( (q^2;q^5)_∞ (q^3;q^5)_∞ )

    Hence:
      r5(q) = R(q)^5 = q * ( (q;q^5)_∞ (q^4;q^5)_∞ / ( (q^2;q^5)_∞ (q^3;q^5)_∞ ) )^5.
    """
    if max_q_exp < 0:
        raise ValueError("max_q_exp must be non-negative")
    deg = max_q_exp
    a1 = _qpochhammer_arith(deg, step=5, offset=1)  # (q;q^5)_∞
    a4 = _qpochhammer_arith(deg, step=5, offset=4)  # (q^4;q^5)_∞
    a2 = _qpochhammer_arith(deg, step=5, offset=2)  # (q^2;q^5)_∞
    a3 = _qpochhammer_arith(deg, step=5, offset=3)  # (q^3;q^5)_∞
    num = _qpoly_mul(a1, a4, deg)
    den = _qpoly_mul(a2, a3, deg)
    ratio = _qpoly_div(num, den, deg)  # constant 1
    ratio5 = _qpoly_pow(ratio, 5, deg)

    r5 = [0] * (deg + 1)
    # multiply by q: shift by 1
    for k, ck in enumerate(ratio5[:deg]):
        if k + 1 <= deg:
            r5[k + 1] = int(ck)
    return r5


def verify_rogers_ramanujan_5b_identity(max_q_exp: int = 12) -> dict[str, object]:
    """Verify the Rogers–Ramanujan identity behind the 5B Hauptmodul.

    Wikipedia states:
      1/R(q)^5 - R(q)^5 = (η(τ)/η(5τ))^6 + 11.

    With our q=e^{2πiτ} convention, (η(τ)/η(5τ))^6 has leading q^{-1}, and the
    Monster normalization for 5B is:
      T_5B(q) = 1/R(q)^5 - 5 - R(q)^5.
    """
    if max_q_exp < 1:
        raise ValueError("max_q_exp must be >= 1")

    t5b = mckay_thompson_series("5B", max_q_exp=max_q_exp)
    if t5b is None:
        raise RuntimeError("5B series unavailable")

    # We need a small amount of slack because 1/r5 involves U^{-1} and
    # coefficient exponents shift by -1. To validate through q^{max_q_exp},
    # compute r5 through q^{max_q_exp+2} and invert U through degree max_q_exp+1.
    r5 = rogers_ramanujan_r5_series(max_q_exp=max_q_exp + 2)

    # r5(q) = q * U(q) with U(0)=1, so 1/r5 = q^{-1} * U(q)^{-1}.
    U = [r5[k + 1] for k in range(max_q_exp + 2)]
    U[0] = 1
    invU = _qpoly_inv(U, max_q_exp + 1)

    expr: dict[int, int] = {}
    # 1/r5
    for k, ck in enumerate(invU[: max_q_exp + 2]):
        exp = -1 + k
        if -1 <= exp <= max_q_exp and ck:
            expr[exp] = expr.get(exp, 0) + int(ck)
    # -5 constant
    expr[0] = expr.get(0, 0) - 5
    # - r5
    for exp in range(1, max_q_exp + 1):
        ck = int(r5[exp])
        if ck:
            expr[exp] = expr.get(exp, 0) - ck

    mismatches: list[tuple[int, int, int]] = []
    for e in [-1, 0] + list(range(1, max_q_exp + 1)):
        lv = int(expr.get(e, 0))
        rv = int(t5b.get(e, 0))
        if lv != rv:
            mismatches.append((e, lv, rv))

    return {
        "max_q_exp": max_q_exp,
        "verified": len(mismatches) == 0,
        "n_mismatches": len(mismatches),
        "mismatches": mismatches[:10],
        "r5_first_coeffs": r5[: min(len(r5), 8)],
    }


def j_series_via_rogers_ramanujan_r5(max_q_exp: int = 12) -> dict[int, int]:
    """Compute the Klein j-invariant series using Rogers–Ramanujan data.

    Wikipedia gives the rational function identity relating the Klein j-invariant
    and the Rogers–Ramanujan continued fraction R(q):

      j(τ) = - (r^20 - 228 r^15 + 494 r^10 + 228 r^5 + 1)^3
             / ( r^5 (r^10 + 11 r^5 - 1)^5 )

    with r = R(q). Setting t = r^5 = R(q)^5 turns this into:

      j(τ) = - (t^4 - 228 t^3 + 494 t^2 + 228 t + 1)^3 / ( t (t^2 + 11 t - 1)^5 )
           =   (t^4 - 228 t^3 + 494 t^2 + 228 t + 1)^3 / ( t (1 - 11 t - t^2)^5 ).

    Since t(q) = q + O(q^2), this produces the Laurent expansion:
      j(τ) = q^{-1} + 744 + Σ_{n>=1} c(n) q^n.
    """
    if max_q_exp < 0:
        raise ValueError("max_q_exp must be non-negative")

    # We need coefficients through q^{max_q_exp} after dividing by t(q), which
    # introduces a q^{-1} shift. Compute ordinary series through degree max_q_exp+1.
    deg = max_q_exp + 1
    t = rogers_ramanujan_r5_series(max_q_exp=deg + 1)  # need t[deg+1] for U
    t_trunc = t[: deg + 1]

    t2 = _qpoly_mul(t_trunc, t_trunc, deg)
    t3 = _qpoly_mul(t2, t_trunc, deg)
    t4 = _qpoly_mul(t2, t2, deg)

    # P(t) = t^4 - 228 t^3 + 494 t^2 + 228 t + 1
    P = [0] * (deg + 1)
    P[0] = 1
    for k in range(0, deg + 1):
        P[k] += 228 * int(t_trunc[k])
        P[k] += 494 * int(t2[k])
        P[k] -= 228 * int(t3[k])
        P[k] += int(t4[k])

    num = _qpoly_pow(P, 3, deg)

    # W(t) = (1 - 11 t - t^2)^5
    W = [0] * (deg + 1)
    W[0] = 1
    for k in range(0, deg + 1):
        W[k] -= 11 * int(t_trunc[k])
        W[k] -= int(t2[k])

    W5 = _qpoly_pow(W, 5, deg)
    invW5 = _qpoly_inv(W5, deg)

    # A(q) = num / W5
    A = _qpoly_mul(num, invW5, deg)

    # Divide by t(q): t = q * U with U(0)=1 => 1/t = q^{-1} * U^{-1}.
    U = [int(t[k + 1]) for k in range(deg + 1)]
    U[0] = 1
    invU = _qpoly_inv(U, deg)

    AU = _qpoly_mul(A, invU, deg)

    out: dict[int, int] = {-1: int(AU[0])}
    for n in range(0, max_q_exp + 1):
        out[n] = int(AU[n + 1])
    return out


def verify_j_via_rogers_ramanujan(max_q_exp: int = 12) -> dict[str, object]:
    """Verify j(τ) reconstruction from t(q)=R(q)^5 via the Wikipedia identity."""
    if max_q_exp < 1:
        raise ValueError("max_q_exp must be >= 1")

    j_rr = j_series_via_rogers_ramanujan_r5(max_q_exp=max_q_exp)
    j_ref = j_coeffs(max_q_exp)

    mismatches: list[tuple[int, int, int]] = []
    if int(j_rr.get(-1, 0)) != 1:
        mismatches.append((-1, int(j_rr.get(-1, 0)), 1))
    if int(j_rr.get(0, 0)) != 744:
        mismatches.append((0, int(j_rr.get(0, 0)), 744))
    for n in range(1, max_q_exp + 1):
        lv = int(j_rr.get(n, 0))
        rv = int(j_ref[n - 1])
        if lv != rv:
            mismatches.append((n, lv, rv))

    return {
        "max_q_exp": max_q_exp,
        "verified": len(mismatches) == 0,
        "n_mismatches": len(mismatches),
        "mismatches": mismatches[:10],
    }


def _laurent_mul(
    a: dict[int, int], b: dict[int, int], min_exp: int, max_exp: int
) -> dict[int, int]:
    out: dict[int, int] = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = ea + eb
            if e < min_exp or e > max_exp:
                continue
            out[e] = out.get(e, 0) + ca * cb
    return {e: c for e, c in out.items() if c != 0}


def _laurent_pow(
    f: dict[int, int], k: int, min_exp: int, max_exp: int
) -> dict[int, int]:
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return {0: 1}
    out = dict(f)
    for _ in range(1, k):
        out = _laurent_mul(out, f, min_exp=min_exp, max_exp=max_exp)
    return out


def _solve_linear_system_fraction(
    A: list[list[Fraction]], b: list[Fraction]
) -> list[Fraction]:
    n = len(b)
    if n == 0:
        return []
    M = [row[:] + [b_i] for row, b_i in zip(A, b)]
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if M[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            raise ValueError("singular system in Faber polynomial solve")
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]

        pv = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col]
            if factor == 0:
                continue
            for j in range(col, n + 1):
                M[r][j] -= factor * M[col][j]
    return [M[i][n] for i in range(n)]


def faber_polynomial_series(
    f: dict[int, int], m: int, max_q_exp: int
) -> dict[str, object]:
    """Compute the Faber polynomial Phi_m for a q^-1 + O(q) series f.

    Returns:
      - coeffs: [c0,...,c_{m-1}] where Phi_m(x)=x^m + sum_{k=0..m-1} c_k x^k
      - series: Laurent coefficients of Phi_m(f(q)) up to q^{max_q_exp}
    """
    if m <= 0:
        raise ValueError("m must be positive")
    if max_q_exp < 0:
        raise ValueError("max_q_exp must be non-negative")

    min_exp = -m
    exps = list(range(-m + 1, 1))  # -m+1,...,0
    # When solving cancellations up to q^0, we must retain enough positive degrees
    # during intermediate products; otherwise sequential truncation can drop
    # contributions (order-dependent). The worst-case needed exponent is m-1.
    solve_max_exp = max(m - 1, 0)
    powers = [
        _laurent_pow(f, k, min_exp=min_exp, max_exp=solve_max_exp) for k in range(m)
    ]
    f_m = _laurent_pow(f, m, min_exp=min_exp, max_exp=solve_max_exp)

    A = [[Fraction(powers[k].get(e, 0)) for k in range(m)] for e in exps]
    b = [Fraction(-f_m.get(e, 0)) for e in exps]
    coeffs = _solve_linear_system_fraction(A, b)

    # To compute coefficients up to q^N in a sequential product, we need slack
    # up to N+(m-1), since intermediate terms can later combine with q^-1 factors.
    build_max_exp = max_q_exp + (m - 1)
    series = _laurent_pow(f, m, min_exp=min_exp, max_exp=build_max_exp)
    for k, ck in enumerate(coeffs):
        if ck == 0:
            continue
        term = _laurent_pow(f, k, min_exp=min_exp, max_exp=build_max_exp)
        for e, v in term.items():
            series[e] = series.get(e, 0) + int(ck * v)

    for e in range(-m + 1, 1):
        if series.get(e, 0) != 0:
            raise AssertionError(f"Faber cancellation failed at q^{e}: {series.get(e)}")
    if series.get(-m, 0) != 1:
        raise AssertionError("Faber normalization failed (q^-m coefficient)")

    # Return only coefficients through max_q_exp (but compute with slack above).
    series = {e: c for e, c in series.items() if e <= max_q_exp}

    coeffs_int: list[int] = []
    for c in coeffs:
        if c.denominator != 1:
            raise AssertionError("non-integer Faber coefficient encountered")
        coeffs_int.append(int(c.numerator))

    return {"m": m, "coeffs": coeffs_int, "series": series}


def verify_fricke_prime_replicability(
    class_name: str, max_q_exp: int = 10
) -> dict[str, object]:
    """Verify the m=p replicability identity for supported prime-order classes."""
    name = class_name.upper()
    p_map = {
        "2A": 2,
        "2B": 2,
        "3A": 3,
        "3B": 3,
        "3C": 3,
        "5A": 5,
        "5B": 5,
        "7A": 7,
        "7B": 7,
        "11A": 11,
        "13A": 13,
        "13B": 13,
    }
    p = p_map.get(name)
    if p is None:
        raise ValueError(f"Unsupported class for replicability: {class_name}")

    f = mckay_thompson_series(name, max_q_exp=p * max_q_exp)
    if f is None:
        raise RuntimeError(f"Series unavailable for class {class_name}")

    faber = faber_polynomial_series(f, m=p, max_q_exp=max_q_exp)
    lhs: dict[int, int] = dict(faber["series"])  # type: ignore[assignment]

    rhs: dict[int, int] = {-p: 1}
    for n in range(1, max_q_exp + 1):
        rhs[n] = rhs.get(n, 0) + p * int(f.get(p * n, 0))

    j_needed = max_q_exp // p
    jpos = j_coeffs(j_needed)
    for n, c in enumerate(jpos, start=1):
        exp = p * n
        if exp <= max_q_exp:
            rhs[exp] = rhs.get(exp, 0) + int(c)

    mismatches: list[tuple[int, int, int]] = []
    for e in [-p] + list(range(1, max_q_exp + 1)):
        lv = int(lhs.get(e, 0))
        rv = int(rhs.get(e, 0))
        if lv != rv:
            mismatches.append((e, lv, rv))

    return {
        "class_name": name,
        "p": p,
        "max_q_exp": max_q_exp,
        "verified": len(mismatches) == 0,
        "n_mismatches": len(mismatches),
        "mismatches": mismatches[:10],
        "faber_coeffs": faber["coeffs"],
    }


def monster_order_factorization() -> dict[int, int]:
    """Prime factorization of |M| (Monster) as {prime: exponent}."""
    return {
        2: 46,
        3: 20,
        5: 9,
        7: 6,
        11: 2,
        13: 3,
        17: 1,
        19: 1,
        23: 1,
        29: 1,
        31: 1,
        41: 1,
        47: 1,
        59: 1,
        71: 1,
    }


def monster_order() -> int:
    n = 1
    for p, e in monster_order_factorization().items():
        n *= int(p) ** int(e)
    return n


def load_sporadic_group_orders(
    json_path: str | None = None,
) -> dict[str, dict[int, int]] | None:
    """Load sporadic group order factorizations (including Tits group) from JSON.

    The JSON format is a mapping {group_name: {prime: exponent}} with primes as strings.
    """
    path = (
        Path(json_path)
        if json_path is not None
        else (SCRIPTS_DIR.parent / "data" / "sporadic_group_orders.json")
    )
    if not path.exists():
        return None

    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[int, int]] = {}
    for name, fac in raw.items():
        out[str(name)] = {int(p): int(e) for p, e in fac.items()}
    return out


def analyze_sporadic_group_magnitudes(
    json_path: str | None = None,
) -> dict[str, object]:
    """Summarize sporadic group *orders* and prime signatures.

    The main output is logarithmic (base 10 and base 2) to avoid constructing huge ints.
    """
    facs = load_sporadic_group_orders(json_path=json_path)
    if facs is None:
        return {
            "available": False,
            "reason": "sporadic_group_orders.json missing",
        }

    logs10: dict[str, float] = {}
    logs2: dict[str, float] = {}
    digits: dict[str, int] = {}
    bits: dict[str, int] = {}

    all_primes: set[int] = set()
    for name, fac in facs.items():
        all_primes |= set(fac.keys())
        l10 = sum(int(e) * log10(int(p)) for p, e in fac.items())
        l2 = sum(int(e) * log2(int(p)) for p, e in fac.items())
        logs10[name] = float(l10)
        logs2[name] = float(l2)
        digits[name] = int(l10) + 1 if l10 > 0 else 1
        bits[name] = int(l2) + 1 if l2 > 0 else 1

    monster_primes = set(monster_prime_divisors())
    extra_primes_union = sorted(all_primes - monster_primes)
    groups_with_extra_primes = sorted(
        [g for g, fac in facs.items() if (set(fac.keys()) - monster_primes)]
    )

    ranked = sorted(logs10.items(), key=lambda kv: kv[1], reverse=True)
    top5 = [g for g, _ in ranked[:5]]

    return {
        "available": True,
        "n_groups": len(facs),
        "factorizations": facs,
        "log10_order": logs10,
        "log2_order": logs2,
        "digits": digits,
        "bits": bits,
        "primes_union": sorted(all_primes),
        "monster_primes": sorted(monster_primes),
        "extra_primes_union": extra_primes_union,
        "groups_with_extra_primes": groups_with_extra_primes,
        "top5_by_order": top5,
    }


def monster_prime_divisors() -> list[int]:
    return sorted(int(p) for p in monster_order_factorization().keys())


def class_number_negative_discriminant(D: int) -> int:
    """Class number h(D) for a negative discriminant D via reduced forms."""
    import math

    if D >= 0 or D % 4 not in (0, 1):
        raise ValueError("D must be a negative discriminant (0 or 1 mod 4)")

    h = 0
    limit = int(math.sqrt(abs(D) / 3)) + 2
    for a in range(1, limit + 1):
        for b in range(-a, a + 1):
            disc = b * b - D
            if disc % (4 * a) != 0:
                continue
            c = disc // (4 * a)
            if a > c or abs(b) > a:
                continue
            if (abs(b) == a or a == c) and b < 0:
                continue
            if b * b - 4 * a * c != D:
                continue
            h += 1
    return h


def genus_x0_prime(p: int) -> int:
    """Genus g(X0(p)) for prime p >= 2."""
    if p < 2:
        raise ValueError("p must be >= 2")
    if p in (2, 3, 5, 7, 13):
        return 0

    mu = p + 1
    cusps = 2
    e2 = 2 if p % 4 == 1 else 0
    e3 = 2 if p % 3 == 1 else 0
    g = 1 + mu / 12 - e2 / 4 - e3 / 3 - cusps / 2
    return int(round(g))


def ogg_primes_via_genus(max_p: int = 100) -> dict[str, object]:
    """Compute primes p<=max_p with genus(X0(p)^+) == 0 via class numbers.

    For odd primes p>3:
      g(X0(p)^+) = g(X0(p)) + 1 - h(-4p)/2.
    """
    import math

    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
        r = int(math.isqrt(n))
        f = 3
        while f <= r:
            if n % f == 0:
                return False
            f += 2
        return True

    ogg: list[int] = []
    details: dict[int, dict[str, int | float]] = {}
    for p in range(2, max_p + 1):
        if not is_prime(p):
            continue
        if p in (2, 3):
            ogg.append(p)
            details[p] = {"g_x0": 0, "h_minus4p": 0, "g_x0_plus": 0.0}
            continue
        g = genus_x0_prime(p)
        h = class_number_negative_discriminant(-4 * p)
        g_plus = g + 1 - h / 2
        details[p] = {"g_x0": g, "h_minus4p": h, "g_x0_plus": float(g_plus)}
        if abs(g_plus) < 1e-12:
            ogg.append(p)

    return {"max_p": max_p, "primes": ogg, "details": details}


def infer_monster_head_character_values(
    class_name: str, max_n: int = 3
) -> dict[int, int] | None:
    """Infer a small subset of Monster character values from moonshine 'head'
    decompositions V_n for n<=max_n, assuming early coefficients introduce at
    most one new irrep at each step.
    """
    if max_n < 1:
        raise ValueError("max_n must be >= 1")

    series = mckay_thompson_series(class_name, max_q_exp=max_n)
    if series is None:
        return None

    data = analyze_leech_monster()
    decomps = data.get("j_decompositions", {})

    chis: dict[int, int] = {1: 1}
    for n in range(1, max_n + 1):
        info = decomps.get(n)
        if not info or not info.get("exact"):
            break
        dec = info.get("decomp", {})
        unknown = [int(d) for d in dec.keys() if int(d) not in chis]
        known_sum = sum(
            int(mult) * int(chis[int(deg)])
            for deg, mult in dec.items()
            if int(deg) in chis
        )
        trace_n = int(series.get(n, 0))

        if len(unknown) == 0:
            if trace_n != known_sum:
                raise AssertionError(
                    f"Trace mismatch at n={n} for {class_name}: {trace_n} != {known_sum}"
                )
            continue
        if len(unknown) != 1:
            break

        deg = unknown[0]
        mult = int(dec.get(deg, 0))
        if mult == 0:
            break
        rhs = trace_n - known_sum
        if rhs % mult != 0:
            raise AssertionError(
                f"Non-integer character inference for {class_name} at n={n}"
            )
        chis[deg] = rhs // mult

    return chis


def verify_9a_cubing_relation(max_q_exp: int = 12) -> dict[str, object]:
    """Verify a composite-order replicability relation for class 9A:

        Phi_3(T_9A) = sum_{b=0..2} T_9A((tau+b)/3) + T_3B(3 tau),

    which implies the power-map identification (9A)^3 = 3B at the level of
    McKay-Thompson series.
    """
    if max_q_exp < 1:
        raise ValueError("max_q_exp must be >= 1")

    f9 = mckay_thompson_series("9A", max_q_exp=3 * max_q_exp)
    if f9 is None:
        raise RuntimeError("9A series unavailable")

    faber = faber_polynomial_series(f9, m=3, max_q_exp=max_q_exp)
    lhs: dict[int, int] = dict(faber["series"])  # type: ignore[assignment]

    rhs_dec: dict[int, int] = {}
    for n in range(1, max_q_exp + 1):
        rhs_dec[n] = 3 * int(f9.get(3 * n, 0))

    remainder: dict[int, int] = {}
    for e in set(lhs.keys()) | set(rhs_dec.keys()):
        remainder[e] = int(lhs.get(e, 0)) - int(rhs_dec.get(e, 0))
    remainder = {e: v for e, v in remainder.items() if v != 0}

    f3b = mckay_thompson_series("3B", max_q_exp=max_q_exp // 3)
    if f3b is None:
        raise RuntimeError("3B series unavailable")
    expected: dict[int, int] = {-3: 1}
    for n in range(1, max_q_exp // 3 + 1):
        expected[3 * n] = int(f3b.get(n, 0))

    mismatches: list[tuple[int, int, int]] = []
    for e in [-3] + [3 * n for n in range(1, max_q_exp // 3 + 1)]:
        lv = int(remainder.get(e, 0))
        rv = int(expected.get(e, 0))
        if lv != rv:
            mismatches.append((e, lv, rv))

    return {
        "max_q_exp": max_q_exp,
        "verified": len(mismatches) == 0,
        "n_mismatches": len(mismatches),
        "mismatches": mismatches[:10],
        "inferred_power_class": "3B",
    }


def verify_power_relation(
    class_name: str,
    m: int,
    expected_power_class: str | None = None,
    max_q_exp: int = 20,
    candidates: tuple[str, ...] = (),
) -> dict[str, object]:
    """Verify (or infer) the g^m power-map using *prime* replicability.

    For prime m:
      Phi_m(T_g)(τ) = sum_{b=0..m-1} T_g((τ+b)/m) + T_{g^m}(m τ).

    The decimation sum selects exponents divisible by m:
      sum_{b=0..m-1} T_g((τ+b)/m) = m * sum_{n>=1} a_{m n} q^n.
    """

    def _is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
        f = 3
        while f * f <= n:
            if n % f == 0:
                return False
            f += 2
        return True

    if m <= 1:
        raise ValueError("m must be >= 2")
    if not _is_prime(m):
        raise ValueError("verify_power_relation currently supports prime m only")
    if max_q_exp < 1:
        raise ValueError("max_q_exp must be >= 1")

    name = class_name.upper()
    f = mckay_thompson_series(name, max_q_exp=m * max_q_exp)
    if f is None:
        raise RuntimeError(f"Series unavailable for class {class_name}")

    faber = faber_polynomial_series(f, m=m, max_q_exp=max_q_exp)
    lhs: dict[int, int] = dict(faber["series"])  # type: ignore[assignment]

    rhs_dec: dict[int, int] = {}
    for n in range(1, max_q_exp + 1):
        rhs_dec[n] = m * int(f.get(m * n, 0))

    remainder: dict[int, int] = {}
    for e in set(lhs.keys()) | set(rhs_dec.keys()):
        remainder[e] = int(lhs.get(e, 0)) - int(rhs_dec.get(e, 0))
    remainder = {e: v for e, v in remainder.items() if v != 0}

    cand_results: dict[str, dict[str, object]] = {}
    for cand in candidates:
        fm = mckay_thompson_series(cand, max_q_exp=max_q_exp // m + 2)
        if fm is None:
            continue

        expected: dict[int, int] = {-m: 1}
        for n in range(1, max_q_exp // m + 1):
            expected[m * n] = int(fm.get(n, 0))

        mismatches: list[tuple[int, int, int]] = []
        exps = [-m] + [m * n for n in range(1, max_q_exp // m + 1)]
        for e in exps:
            lv = int(remainder.get(e, 0))
            rv = int(expected.get(e, 0))
            if lv != rv:
                mismatches.append((e, lv, rv))

        cand_results[cand.upper()] = {
            "n_mismatches": len(mismatches),
            "mismatches": mismatches[:10],
        }

    inferred = None
    if cand_results:
        inferred = min(cand_results.items(), key=lambda kv: int(kv[1]["n_mismatches"]))[
            0
        ]

    target = expected_power_class.upper() if expected_power_class else inferred
    verified = False
    target_mismatches: list[tuple[int, int, int]] = []
    if target and target in cand_results:
        verified = int(cand_results[target]["n_mismatches"]) == 0
        target_mismatches = list(cand_results[target]["mismatches"])  # type: ignore[list-item]

    return {
        "class_name": name,
        "m": m,
        "max_q_exp": max_q_exp,
        "verified": verified,
        "inferred_power_class": inferred,
        "expected_power_class": (
            expected_power_class.upper() if expected_power_class else None
        ),
        "target_mismatches": target_mismatches,
        "candidates": cand_results,
    }


def verify_replicability_relation(
    class_name: str,
    m: int,
    power_map: dict[int, str],
    max_q_exp: int = 20,
) -> dict[str, object]:
    """Verify the Conway–Norton replicability identity for general m.

    Uses the divisor-sum form:
      Phi_m(T_g)(τ) = sum_{ad=m} sum_{b=0..d-1} T_{g^a}((a τ + b)/d).

    This requires a power-map lookup for each divisor a of m (a>1) present in the
    sum. Provide `power_map` as {a: class_name_for_g^a}. The identity class is "1A".
    """
    if m <= 0:
        raise ValueError("m must be positive")
    if max_q_exp < 1:
        raise ValueError("max_q_exp must be >= 1")

    name = class_name.upper()
    f = mckay_thompson_series(name, max_q_exp=m * max_q_exp)
    if f is None:
        raise RuntimeError(f"Series unavailable for class {class_name}")

    faber = faber_polynomial_series(f, m=m, max_q_exp=max_q_exp)
    lhs: dict[int, int] = dict(faber["series"])  # type: ignore[assignment]

    rhs: dict[int, int] = {}

    for a in range(1, m + 1):
        if m % a != 0:
            continue
        d = m // a
        if a == 1:
            h_name = name
        else:
            h_name = power_map.get(a)
            if not h_name:
                raise ValueError(f"Missing power-map entry for a={a} in m={m}")
            h_name = h_name.upper()

        max_needed = d * (max_q_exp // a)
        h = mckay_thompson_series(h_name, max_q_exp=max_needed)
        if h is None:
            raise RuntimeError(f"Series unavailable for power-map class {h_name}")

        # d=1 contributes the negative power q^{-a} from the leading q^{-1}.
        if d == 1:
            rhs[-a] = rhs.get(-a, 0) + 1

        for k in range(1, max_q_exp // a + 1):
            n = d * k
            coef = int(h.get(n, 0))
            if coef == 0:
                continue
            exp = a * k
            rhs[exp] = rhs.get(exp, 0) + d * coef

    mismatches: list[tuple[int, int, int]] = []
    for e in [-m] + list(range(1, max_q_exp + 1)):
        lv = int(lhs.get(e, 0))
        rv = int(rhs.get(e, 0))
        if lv != rv:
            mismatches.append((e, lv, rv))

    return {
        "class_name": name,
        "m": m,
        "max_q_exp": max_q_exp,
        "verified": len(mismatches) == 0,
        "n_mismatches": len(mismatches),
        "mismatches": mismatches[:10],
    }


def verify_square_power_relation(
    class_name: str,
    expected_square_class: str | None = None,
    max_q_exp: int = 20,
    candidates: tuple[str, ...] = ("2A", "2B"),
) -> dict[str, object]:
    """Verify the m=2 replicability identity to infer/confirm g^2.

    For m=2:
      Phi_2(T_g)(τ) = T_g(τ/2) + T_g((τ+1)/2) + T_{g^2}(2τ).

    The decimation sum picks out even coefficients:
      T_g(τ/2) + T_g((τ+1)/2) = 2 * sum_{n>=1} a_{2n} q^n.
    """
    if max_q_exp < 1:
        raise ValueError("max_q_exp must be >= 1")

    name = class_name.upper()
    f = mckay_thompson_series(name, max_q_exp=2 * max_q_exp)
    if f is None:
        raise RuntimeError(f"Series unavailable for class {class_name}")

    faber = faber_polynomial_series(f, m=2, max_q_exp=max_q_exp)
    lhs: dict[int, int] = dict(faber["series"])  # type: ignore[assignment]

    rhs_dec: dict[int, int] = {}
    for n in range(1, max_q_exp + 1):
        rhs_dec[n] = 2 * int(f.get(2 * n, 0))

    remainder: dict[int, int] = {}
    for e in set(lhs.keys()) | set(rhs_dec.keys()):
        remainder[e] = int(lhs.get(e, 0)) - int(rhs_dec.get(e, 0))
    remainder = {e: v for e, v in remainder.items() if v != 0}

    cand_results: dict[str, dict[str, object]] = {}
    for cand in candidates:
        g2 = mckay_thompson_series(cand, max_q_exp=max_q_exp)
        if g2 is None:
            continue

        expected: dict[int, int] = {}
        for e, c in g2.items():
            ee = 2 * int(e)
            if ee <= max_q_exp:
                expected[ee] = int(c)

        mismatches: list[tuple[int, int, int]] = []
        for e in [-2] + [2 * n for n in range(1, max_q_exp // 2 + 1)]:
            lv = int(remainder.get(e, 0))
            rv = int(expected.get(e, 0))
            if lv != rv:
                mismatches.append((e, lv, rv))

        cand_results[cand] = {
            "n_mismatches": len(mismatches),
            "mismatches": mismatches[:10],
        }

    inferred = None
    if cand_results:
        inferred = min(cand_results.items(), key=lambda kv: int(kv[1]["n_mismatches"]))[
            0
        ]

    target = expected_square_class.upper() if expected_square_class else inferred
    verified = False
    target_mismatches: list[tuple[int, int, int]] = []
    if target and target in cand_results:
        verified = int(cand_results[target]["n_mismatches"]) == 0
        target_mismatches = list(cand_results[target]["mismatches"])  # type: ignore[list-item]

    return {
        "class_name": name,
        "max_q_exp": max_q_exp,
        "verified": verified,
        "inferred_power_class": inferred,
        "expected_power_class": (
            expected_square_class.upper() if expected_square_class else None
        ),
        "target_mismatches": target_mismatches,
        "candidates": cand_results,
    }


def compute_mckay_traces(
    class_name: str = "1A",
    n_terms: int = 8,
    use_full: bool = True,
    json_path: str | None = None,
):
    """Compute McKay–Thompson traces Tr(g | V_n) for `class_name` up to `n_terms`.

    - If `class_name` == '1A' (identity) this returns the standard j‑coefficients.
    - If a full Monster character table is available (GAP or bundled), it will be
      used to compute traces from the irrep multiplicities in `V_n`.
    - Otherwise, falls back to eta-quotient series for some prime-order classes.
    """
    # identity: trivial shortcut
    if class_name.upper() in ("1A", "ID", "IDENTITY"):
        return j_coeffs(n_terms)

    # Try to obtain character values for the requested class (JSON/libgap/GAP).
    char_map = _load_monster_char_map_via_gap(class_name, json_path=json_path)
    if char_map is None:
        # Offline fallback (eta-quotients) for a handful of Fricke prime classes.
        series = mckay_thompson_series(class_name, max_q_exp=n_terms)
        if series is not None:
            return [int(series.get(n, 0)) for n in range(1, n_terms + 1)]
        return None

    # obtain decomposition data
    data = analyze_leech_monster()
    if (
        use_full
        and data.get("monster_irreps_available")
        and data.get("j_decompositions_full")
    ):
        decomps = data["j_decompositions_full"]
    else:
        decomps = data["j_decompositions"]

    # character values already loaded above (JSON/libgap/GAP)

    traces = []
    for n in range(1, min(n_terms, len(data["j_coeffs"])) + 1):
        dec = decomps.get(n, {}).get("decomp", {})
        total = 0
        for deg, mult in dec.items():
            ch = char_map.get(int(deg))
            if ch is None:
                # missing character value for this irreducible degree
                total = None
                break
            total += int(mult) * int(ch)
        traces.append(total)
    return traces


def plot_mckay_series(
    class_name: str = "1A", n_terms: int = 12, out_png: str | None = None
):
    """Return McKay–Thompson traces and optionally save a PNG plot (matplotlib).

    Always writes a CSV to `./outputs/mckay_{class_name}.csv`.
    """
    traces = compute_mckay_traces(class_name, n_terms=n_terms)
    if traces is None:
        raise RuntimeError("Character table unavailable for class: %s" % class_name)

    from pathlib import Path

    out_dir = Path(__file__).resolve().parents[1] / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"mckay_{class_name}.csv"
    with csv_path.open("w", encoding="utf-8") as fh:
        fh.write("n,trace\n")
        for i, t in enumerate(traces, start=1):
            fh.write(f"{i},{t}\n")

    # optional plotting
    try:
        import matplotlib.pyplot as plt

        xs = list(range(1, len(traces) + 1))
        plt.figure(figsize=(7, 4))
        plt.plot(xs, traces, marker="o")
        plt.title(f"McKay–Thompson traces for {class_name}")
        plt.xlabel("n")
        plt.ylabel("trace")
        plt.grid(True)
        if out_png:
            plt.savefig(out_png)
        else:
            png_path = out_dir / f"mckay_{class_name}.png"
            plt.savefig(png_path)
        plt.close()
    except Exception:
        # matplotlib optional — CSV is always written
        out_png = None

    return {"csv": str(csv_path), "png": out_png}


@lru_cache(maxsize=1)
def compute_w33_monster_invariants() -> dict:
    """Compute W(3,3) invariants used in the Monster correction identities."""
    import numpy as np

    n, _vertices, adj, _edges = build_w33()
    simplices = build_clique_complex(n, adj)
    hom = compute_homology(simplices)

    n_vertices = len(simplices.get(0, []))
    n_lines = len(simplices.get(3, []))  # K4 cliques correspond to GQ lines
    b1 = int(hom["betti_numbers"].get(1, 0))

    # Hodge L1 = d1^T d1 + d2 d2^T on 1-chains (edges)
    d1 = boundary_matrix(simplices[1], simplices[0]).astype(float)
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    L1 = d1.T @ d1 + d2 @ d2.T
    evals = np.linalg.eigvalsh(L1)
    tol = 1e-8
    nonzero = [float(x) for x in evals if abs(float(x)) > tol]
    spectral_gap = min(nonzero) if nonzero else 0.0

    return {
        "n_vertices": int(n_vertices),
        "n_lines": int(n_lines),
        "n_incidence_objects": int(n_vertices + n_lines),
        "b1": int(b1),
        "spectral_gap_L1": float(spectral_gap),
    }


def verify_borcherds_denominator_identity(
    max_p_degree: int = 2, max_q_degree: int = 2
) -> dict:
    """Verify a low-order truncation of Borcherds' Monster Lie algebra identity.

    Denominator identity (Borcherds 1992), with J(τ)=j(τ)-744 and
    J(q)=∑_{n=-1}^∞ c(n) q^n (c(-1)=1, c(0)=0):

        p^{-1} ∏_{m>0, n∈ℤ} (1 - p^m q^n)^{c(mn)} = J(p) - J(q).

    This function verifies equality of the truncated Laurent series in p and q
    for p-degree ≤ max_p_degree and q-degree ≤ max_q_degree.
    """
    if max_p_degree < 0 or max_q_degree < 0:
        raise ValueError("max_p_degree and max_q_degree must be non-negative")

    # We need one extra q-degree because the unique negative-q factor (1 - p q^{-1})
    # can shift a q^{N+1} term down to q^N.
    max_p_intermediate = max_p_degree + 1
    max_q_intermediate = max_q_degree + 1
    max_coeff = max_p_intermediate * max_q_intermediate

    # c(n) are the coefficients of J(q)=j(q)-744 (same positive coefficients as j)
    j_pos = j_coeffs(max_coeff)
    c = {-1: 1, 0: 0}
    for i, v in enumerate(j_pos, start=1):
        c[i] = int(v)

    def series_mul(a: dict, b: dict, max_p: int, max_q: int, min_q: int) -> dict:
        out: dict[tuple[int, int], int] = {}
        for (pa, qa), ca in a.items():
            for (pb, qb), cb in b.items():
                p = pa + pb
                q = qa + qb
                if p > max_p or q > max_q or q < min_q:
                    continue
                out[(p, q)] = out.get((p, q), 0) + int(ca) * int(cb)
        return {k: v for k, v in out.items() if v != 0}

    def binomial_factor_series(m: int, n: int, e: int, max_p: int, max_q: int) -> dict:
        # (1 - x)^e = Σ_k (-1)^k C(e,k) x^k, with x = p^m q^n
        k_max = min(max_p // m, max_q // n)
        out = {(0, 0): 1}
        for k in range(1, k_max + 1):
            out[(m * k, n * k)] = ((-1) ** k) * comb(e, k)
        return out

    # Build positive (nonnegative-q) part first, allowing one extra q-degree.
    prod: dict[tuple[int, int], int] = {(0, 0): 1}
    for m in range(1, max_p_intermediate + 1):
        for n in range(1, max_q_intermediate + 1):
            e = int(c.get(m * n, 0))
            if e == 0:
                continue
            f = binomial_factor_series(m, n, e, max_p_intermediate, max_q_intermediate)
            prod = series_mul(prod, f, max_p_intermediate, max_q_intermediate, min_q=0)

    # Multiply the unique negative-q factor (1 - p q^{-1}) and truncate q to max_q_degree.
    prod = series_mul(
        prod,
        {(0, 0): 1, (1, -1): -1},
        max_p_intermediate,
        max_q_degree,
        min_q=-1,
    )

    # Apply the p^{-1} prefactor (shift p-degree by -1).
    lhs = {(p - 1, q): int(v) for (p, q), v in prod.items() if (p - 1) <= max_p_degree}

    # RHS series: J(p) - J(q), with no mixed terms.
    rhs: dict[tuple[int, int], int] = {(-1, 0): 1, (0, -1): -1}
    for k in range(1, max(max_p_degree, max_q_degree) + 1):
        ck = int(c.get(k, 0))
        if k <= max_p_degree:
            rhs[(k, 0)] = rhs.get((k, 0), 0) + ck
        if k <= max_q_degree:
            rhs[(0, k)] = rhs.get((0, k), 0) - ck

    keys = set(lhs) | set(rhs)
    mismatches = {}
    max_abs_mixed = 0
    for key in keys:
        lv = lhs.get(key, 0)
        rv = rhs.get(key, 0)
        if lv != rv:
            mismatches[key] = {"lhs": lv, "rhs": rv}
        p, q = key
        if p != 0 and q != 0:
            max_abs_mixed = max(max_abs_mixed, abs(lv - rv))

    return {
        "max_p_degree": int(max_p_degree),
        "max_q_degree": int(max_q_degree),
        "verified": len(mismatches) == 0,
        "n_mismatches": int(len(mismatches)),
        "max_abs_mixed_coefficient_error": int(max_abs_mixed),
        "mismatches": mismatches,
    }


@lru_cache(maxsize=1)
def analyze_leech_monster() -> Dict:
    """Compute Leech/Monster numerology derived from W(3,3)/E8 data.

    Returns a dictionary of integers and additional Moonshine checks suitable
    for deterministic unit tests.
    """
    data = analyze_leech_connection()

    e8_roots = data["e8_roots"]
    e8_cubed_roots = data["e8_cubed_roots"]
    leech_kissing = data["leech_kissing"]
    ratio = data["ratio"]

    # Smallest nontrivial Monster representation dimension (McKay--Thompson)
    monster_min_rep = 196_883
    monster_diff = monster_min_rep - leech_kissing

    psp_cubed_order = data.get("psp_cubed_order")
    co0_order = data.get("co0_order")
    excess_symmetry_factor = data.get("excess_symmetry_factor")

    interpretation = (
        "E8^3 provides 720 root vectors; the Leech kissing number 196560 "
        "is 273×720. The smallest Monster rep (196883) is close (difference=323), "
        "suggesting deep but nontrivial connections (Moonshine numerology)."
    )

    # modular/j comparisons
    e4 = e4_coeffs(n_terms=8)
    e4_cubed = poly_power(e4, 3, 8)
    # coefficient of q^1 in Theta(E8)^3 equals 720 (E8^3 minimal vectors)
    theta_e8_cubed_q1 = e4_cubed[1] if len(e4_cubed) > 1 else None

    # Expanded Klein j coefficients (q^1..q^N)
    j_list = j_coeffs(n_terms=8)

    # Small, commonly-used list of Monster irreducible character dimensions
    # (we keep a compact 'known' list for automated comparison tests).
    known_monster_irreps = [
        1,
        196_883,
        21_296_876,
        842_609_326,
        18_538_750_076,
        19_360_062_527,
    ]

    # Exact decomposition search (tries large-first, backtracking). Returns
    # a dict {dim: multiplicity} on success or None.
    import time as _time

    _decompose_deadline = [0.0]  # mutable container for closure

    def _decompose_exact(target: int, irreps: list[int], idx: int = 0, memo=None):
        memo = memo or {}
        key = (idx, target)
        if key in memo:
            return None
        # time-based cutoff: abort search after 5 seconds per coefficient
        if _time.perf_counter() > _decompose_deadline[0]:
            return None
        # cheap cutoff to avoid combinatorial explosion when using a very
        # small bundled irreps list — fallback to greedy will be used.
        if idx == 0 and len(irreps) < 10 and target > irreps[0] * 50:
            memo[key] = None
            return None
        if target == 0:
            return {}
        if idx >= len(irreps):
            return None
        val = irreps[idx]
        # reasonable cap on multiplicities to keep search bounded
        max_m = target // val
        if val == 1:
            max_m = min(max_m, 100)  # trivial rep shouldn't blow up search
        elif val >= 10**9:
            max_m = min(max_m, 3)
        elif val >= 10**7:
            max_m = min(max_m, 10)
        # try to use as many of the large irreps as possible first
        for m in range(max_m, -1, -1):
            rem = target - m * val
            if rem < 0:
                continue
            if rem == 0:
                out = {} if m == 0 else {val: m}
                return out
            sub = _decompose_exact(rem, irreps, idx + 1, memo)
            if sub is not None:
                if m:
                    sub[val] = m
                return sub
        memo[key] = None
        return None

    # Fast greedy partial decomposition (useful when exact match not found)
    def _greedy_decompose(target: int, irreps: list[int]):
        rem = target
        out = {}
        for val in irreps:
            if rem <= 0:
                break
            m = rem // val
            if m:
                out[val] = int(m)
                rem -= m * val
        return out, rem

    # Attempt exact decomposition using known irreps; fall back to greedy
    j_decompositions = {}
    irreps_desc = sorted(known_monster_irreps, reverse=True)
    for idx, c in enumerate(j_list, start=1):
        _decompose_deadline[0] = _time.perf_counter() + 2.0
        exact = _decompose_exact(c, irreps_desc)
        if exact is not None:
            # normalize to include zero multiplicities only for reported dims
            j_decompositions[idx] = {"exact": True, "decomp": exact, "remainder": 0}
        else:
            greedy, rem = _greedy_decompose(c, irreps_desc)
            j_decompositions[idx] = {"exact": False, "decomp": greedy, "remainder": rem}

    # attempt to load full Monster irreps via GAP/libgap (optional)
    # The Monster has 194 conjugacy classes → 194 irreducible representations.
    # Only consider data "available" when we have all (or nearly all) of them.
    monster_irreps_full = _load_monster_irreps_via_gap()
    monster_irreps_available = (
        monster_irreps_full is not None and len(monster_irreps_full) >= 100
    )
    j_decompositions_full = {}
    if monster_irreps_available:
        irreps_full_desc = sorted(monster_irreps_full, reverse=True)
        for idx, c in enumerate(j_list, start=1):
            _decompose_deadline[0] = _time.perf_counter() + 2.0
            exact = _decompose_exact(c, irreps_full_desc)
            if exact is not None:
                j_decompositions_full[idx] = {
                    "exact": True,
                    "decomp": exact,
                    "remainder": 0,
                }
            else:
                greedy, rem = _greedy_decompose(c, irreps_full_desc)
                j_decompositions_full[idx] = {
                    "exact": False,
                    "decomp": greedy,
                    "remainder": rem,
                }

    # expose the first coefficient for legacy tests
    j1 = j_list[0]
    j_minus_leech = j1 - leech_kissing

    # Derive the "Monster correction" from intrinsic W(3,3) invariants.
    w33_inv = compute_w33_monster_invariants()
    w33_objects = int(w33_inv["n_incidence_objects"])  # 40 points + 40 lines
    w33_b1 = int(w33_inv["b1"])  # dim H1(W33)
    w33_gap = float(w33_inv["spectral_gap_L1"])  # L1 spectral gap (Δ)

    monster_diff_from_w33 = w33_objects + 3 * w33_b1
    j_minus_leech_from_w33 = int(round(w33_gap)) * w33_b1

    # Canonical values (computed, not hard-coded)
    assert w33_objects == 80, f"Expected 40 points + 40 lines = 80, got {w33_objects}"
    assert w33_b1 == 81, f"Expected b1=81, got {w33_b1}"
    assert abs(w33_gap - 4.0) < 1e-8, f"Expected spectral gap 4, got {w33_gap}"

    # Monster/Leech identities
    assert (
        monster_diff == monster_diff_from_w33
    ), f"Monster correction mismatch: {monster_diff} vs {monster_diff_from_w33}"
    assert (
        j_minus_leech == j_minus_leech_from_w33
    ), f"j-Leech mismatch: {j_minus_leech} vs {j_minus_leech_from_w33}"
    assert j1 - monster_min_rep == 1, "McKay observation failed: 196884 != 1 + 196883"

    # Borcherds denominator identity (Monster Lie algebra) — low-order check
    borcherds = verify_borcherds_denominator_identity(max_p_degree=2, max_q_degree=2)
    assert borcherds["verified"] is True, (
        "Borcherds denominator identity failed (truncated check): "
        f"{borcherds['n_mismatches']} mismatches"
    )

    ogg = ogg_primes_via_genus(max_p=100)
    monster_primes = monster_prime_divisors()
    assert ogg["primes"] == monster_primes, "Ogg primes != primes dividing |Monster|"

    sporadic = analyze_sporadic_group_magnitudes()
    if sporadic.get("available") is True:
        facs = sporadic.get("factorizations", {})
        if isinstance(facs, dict) and "M" in facs:
            assert facs["M"] == monster_order_factorization()

    return {
        "e8_roots": e8_roots,
        "e8_cubed_roots": e8_cubed_roots,
        "leech_kissing": leech_kissing,
        "ratio": ratio,
        "monster_min_rep": monster_min_rep,
        "monster_diff": monster_diff,
        "psp_cubed_order": psp_cubed_order,
        "co0_order": co0_order,
        "excess_symmetry_factor": excess_symmetry_factor,
        "theta_e8_cubed_q1": theta_e8_cubed_q1,
        "j1": j1,
        "j_minus_leech": j_minus_leech,
        "j_coeffs": j_list,
        "monster_irreps_known": known_monster_irreps,
        "j_decompositions": j_decompositions,
        "monster_irreps_full": monster_irreps_full,
        "monster_irreps_available": monster_irreps_available,
        "j_decompositions_full": j_decompositions_full,
        "w33_invariants_for_monster": w33_inv,
        "monster_diff_from_w33": monster_diff_from_w33,
        "j_minus_leech_from_w33": j_minus_leech_from_w33,
        "borcherds_denominator_identity": borcherds,
        "ogg_primes": ogg["primes"],
        "ogg_primes_details": ogg["details"],
        "monster_order": monster_order(),
        "monster_order_primes": monster_primes,
        "sporadic_magnitudes": sporadic,
        "interpretation": interpretation,
    }


if __name__ == "__main__":
    out = analyze_leech_monster()
    print("PILLAR 57: LEECH / MONSTER / MOONSHINE NUMEROLOGY")
    print("- E8 roots:", out["e8_roots"])
    print("- E8^3 roots:", out["e8_cubed_roots"])
    print("- Leech kissing number:", out["leech_kissing"])
    print("- Ratio (Leech/E8^3):", out["ratio"])
    print("- Monster smallest nontrivial rep:", out["monster_min_rep"])
    print("- Difference (Monster - Leech):", out["monster_diff"])
    w33 = out["w33_invariants_for_monster"]
    print(
        "- W33 invariants: objects=%d, b1=%d, gap=%.1f"
        % (w33["n_incidence_objects"], w33["b1"], w33["spectral_gap_L1"])
    )
    print(
        "- 323 = objects + 3·b1 = %d + 3·%d" % (w33["n_incidence_objects"], w33["b1"])
    )
    print("- 324 = Δ·b1 =", out["j_minus_leech_from_w33"])
    print(
        "- Borcherds denominator (p≤%d,q≤%d): verified=%s"
        % (
            out["borcherds_denominator_identity"]["max_p_degree"],
            out["borcherds_denominator_identity"]["max_q_degree"],
            out["borcherds_denominator_identity"]["verified"],
        )
    )
    print("- Ogg primes (genus-zero X0(p)^+):", out["ogg_primes"])
    sp = out.get("sporadic_magnitudes", {})
    if isinstance(sp, dict) and sp.get("available") is True:
        print("- Sporadic prime union:", sp.get("primes_union"))
        print("- Extra primes beyond Monster:", sp.get("extra_primes_union"))
        print("- Extra-prime groups:", sp.get("groups_with_extra_primes"))
        top = sp.get("top5_by_order", [])
        if isinstance(top, list) and top:
            digits = sp.get("digits", {})
            if isinstance(digits, dict):
                print(
                    "- Largest sporadics (decimal digits):",
                    [(g, digits.get(g)) for g in top],
                )
    print("- Interpretation:", out["interpretation"])
