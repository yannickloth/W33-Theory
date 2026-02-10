from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class HeisenbergLabel:
    u: tuple[int, int]
    z: int


def triad_key(values: Iterable[int]) -> tuple[int, int, int]:
    a, b, c = sorted(int(x) for x in values)
    if len({a, b, c}) != 3:
        raise ValueError("Triad must contain three distinct ids")
    return (a, b, c)


def sign_to_f3_coeff(sign: int) -> int:
    if sign not in (-1, 1):
        raise ValueError("sign must be +/-1")
    return 1 if sign == 1 else 2


def det2(a: tuple[int, int], b: tuple[int, int]) -> int:
    return (a[0] * b[1] - a[1] * b[0]) % 3


def is_collinear_f3_2(
    u: tuple[int, int], v: tuple[int, int], w: tuple[int, int]
) -> bool:
    vu = ((v[0] - u[0]) % 3, (v[1] - u[1]) % 3)
    wu = ((w[0] - u[0]) % 3, (w[1] - u[1]) % 3)
    return det2(vu, wu) == 0


def classify_triad_geometry(
    triad: tuple[int, int, int],
    labels: dict[int, HeisenbergLabel],
) -> str:
    p0, p1, p2 = labels[triad[0]], labels[triad[1]], labels[triad[2]]
    if p0.u == p1.u == p2.u:
        return "fiber"
    if is_collinear_f3_2(p0.u, p1.u, p2.u):
        return "affine_line"
    return "other"


def sorted_u_line_for_triad(
    triad: tuple[int, int, int],
    labels: dict[int, HeisenbergLabel],
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    us = sorted({labels[triad[0]].u, labels[triad[1]].u, labels[triad[2]].u})
    if len(us) != 3:
        raise ValueError("Triad does not span three distinct u points")
    return (us[0], us[1], us[2])


def z_profile_over_u_line(
    triad: tuple[int, int, int],
    labels: dict[int, HeisenbergLabel],
    u_line: tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
) -> tuple[int, int, int]:
    u_to_z = {
        labels[triad[0]].u: labels[triad[0]].z,
        labels[triad[1]].u: labels[triad[1]].z,
        labels[triad[2]].u: labels[triad[2]].z,
    }
    return (u_to_z[u_line[0]], u_to_z[u_line[1]], u_to_z[u_line[2]])


def ordered_nonzero_entries_count(unordered_nonzero: int) -> int:
    # Symmetric cubic tensor: each unordered distinct triad contributes 3! ordered entries.
    return int(unordered_nonzero) * 6
