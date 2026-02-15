"""Derive CP phase(s) δ from a Jarlskog invariant J and mixing angles.

Functions provided:
- jarlskog_from_angles(theta12, theta13, theta23, delta)
- delta_from_jarlskog(J, theta12, theta13, theta23, *, tol=1e-12)

The inversion solves:
  J = s12 c12 s23 c23 s13 c13^2 sin(δ)
for δ (returns principal solution and the complementary π-δ solution).

This module is small, pure-numeric and intended for unit tests and notebooks.
"""

from __future__ import annotations

import math
from typing import Tuple

import numpy as np


def jarlskog_from_angles(
    theta12: float, theta13: float, theta23: float, delta: float
) -> float:
    """Compute the Jarlskog invariant J from standard mixing angles.

    All angles are in radians.
    Formula (PDG convention):
      J = s12 c12 s23 c23 s13 c13^2 sin(delta)
    """
    s12, c12 = math.sin(theta12), math.cos(theta12)
    s13, c13 = math.sin(theta13), math.cos(theta13)
    s23, c23 = math.sin(theta23), math.cos(theta23)
    return float(s12 * c12 * s23 * c23 * s13 * (c13**2) * math.sin(delta))


def _normalize_angle_positive(rad: float) -> float:
    """Normalize angle to [0, 2π)."""
    twopi = 2 * math.pi
    return float(rad % twopi)


def delta_from_jarlskog(
    J: float, theta12: float, theta13: float, theta23: float, *, tol: float = 1e-12
) -> Tuple[float, float]:
    """Invert the Jarlskog relation to recover two possible CP phases.

    Returns a tuple (δ_primary, δ_complement) in radians, both normalized to [0, 2π).
    - δ_primary is arcsin(x) (principal value in [-π/2, π/2]) mapped to [0,2π).
    - δ_complement = π - δ_primary (the complementary solution with same sine).

    Raises ValueError if the denominator is (near) zero or if |J| > denom (outside
    physical range) beyond `tol`.
    """
    s12, c12 = math.sin(theta12), math.cos(theta12)
    s13, c13 = math.sin(theta13), math.cos(theta13)
    s23, c23 = math.sin(theta23), math.cos(theta23)

    denom = s12 * c12 * s23 * c23 * s13 * (c13**2)
    if abs(denom) < 1e-16:
        raise ValueError("mixing angles give zero denominator; δ not determined")

    x = J / denom
    if abs(x) > 1.0 + tol:
        raise ValueError(
            f"J out of physical range for given angles (|J/denom|={abs(x):.3e} > 1)"
        )

    # clamp due to tiny numerical noise
    x = max(-1.0, min(1.0, float(x)))

    delta_p = math.asin(x)  # principal solution in [-π/2, π/2]
    delta_alt = math.pi - delta_p

    return _normalize_angle_positive(delta_p), _normalize_angle_positive(delta_alt)


if __name__ == "__main__":
    # tiny demo using W33-relevant angles (degrees → radians)
    theta12_deg = 12.15
    theta13_deg = 0.119
    theta23_deg = 2.38
    delta_deg = 68.0

    t12 = math.radians(theta12_deg)
    t13 = math.radians(theta13_deg)
    t23 = math.radians(theta23_deg)
    d = math.radians(delta_deg)

    J = jarlskog_from_angles(t12, t13, t23, d)
    print(f"示例: J = {J:.3e} for δ = {delta_deg}°")

    dp, da = delta_from_jarlskog(J, t12, t13, t23)
    print(
        f"Recovered δ (deg): {math.degrees(dp):.6f}, complementary: {math.degrees(da):.6f}"
    )
