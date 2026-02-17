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
import shutil
import subprocess
import sys
from fractions import Fraction
from functools import lru_cache
from math import comb
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


def mckay_thompson_series(class_name: str, max_q_exp: int = 8) -> dict[int, int] | None:
    """Return a McKay-Thompson series T_g(q)=q^-1 + sum_{n>=1} a_n q^n.

    Offline (no GAP) support is implemented for Fricke prime classes:
      2A, 3A, 5A, 7A, 13A.

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

    fricke_prime = {"2A": 2, "3A": 3, "5A": 5, "7A": 7, "13A": 13}
    p = fricke_prime.get(name)
    if p is None:
        return None

    # Fricke prime Hauptmodul:
    #   T_pA(tau) = (eta/eta(p))^{24/(p-1)}
    #            + p^{12/(p-1)} (eta(p)/eta)^{24/(p-1)}
    #            + 24/(p-1)
    a = 24 // (p - 1)
    scale = p ** (12 // (p - 1))
    const = 24 // (p - 1)

    # Need one extra degree because term1 is q^-1 * (1 + O(q)).
    deg = max_q_exp + 1
    e = _qpochhammer(deg, step=1)  # (q;q)_inf
    ep = _qpochhammer(deg, step=p)  # (q^p;q^p)_inf
    ratio = _qpoly_div(e, ep, deg)  # E(q)/E(q^p)

    ratio_pow = _qpoly_pow(ratio, a, deg)
    ratio_inv_pow = _qpoly_pow(_qpoly_inv(ratio, deg), a, deg)

    series: dict[int, int] = {}
    # term1: q^-1 * ratio_pow
    for k, ck in enumerate(ratio_pow):
        exp = -1 + k
        if -1 <= exp <= max_q_exp and ck:
            series[exp] = series.get(exp, 0) + int(ck)

    # term2: scale * q^+1 * ratio_inv_pow
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
    """Verify the m=p replicability identity for Fricke prime classes pA."""
    name = class_name.upper()
    p_map = {"2A": 2, "3A": 3, "5A": 5, "7A": 7, "13A": 13}
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
    - Otherwise, falls back to eta-quotient series for a few Fricke prime classes.
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
    print("- Interpretation:", out["interpretation"])
