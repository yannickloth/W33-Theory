from __future__ import annotations

from collections import defaultdict

from scripts.ce2_global_cocycle import _heisenberg_vec_maps, _simple_family_sign_map


def _u(e6id: int, e6id_to_vec: dict[int, tuple[int, int, int]]) -> tuple[int, int]:
    v = e6id_to_vec[int(e6id)]
    return (int(v[0]) % 3, int(v[1]) % 3)


def _z(e6id: int, e6id_to_vec: dict[int, tuple[int, int, int]]) -> int:
    return int(e6id_to_vec[int(e6id)][2]) % 3


def _u2_sub(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return ((a[0] - b[0]) % 3, (a[1] - b[1]) % 3)


def omega(u: tuple[int, int], v: tuple[int, int]) -> int:
    """Alternating form ω((x,y),(a,b)) = y·a - x·b (mod 3)."""
    x, y = int(u[0]) % 3, int(u[1]) % 3
    a, b = int(v[0]) % 3, int(v[1]) % 3
    return (y * a - x * b) % 3


def k_of_direction(d: tuple[int, int]) -> int | None:
    d1, d2 = int(d[0]) % 3, int(d[1]) % 3
    if d1 == 0:
        return None
    if d2 == 0:
        return (-d1) % 3
    return d1


def test_ce2_sign_symplectic_delta_and_constant_line_rule():
    sign_map = _simple_family_sign_map()
    e6id_to_vec, _vec_to_e6id = _heisenberg_vec_maps()

    # Balanced u-regimes.
    t1 = 0
    t2 = 0
    for c_i, m_i, o_i in sign_map.keys():
        um = _u(m_i, e6id_to_vec)
        uo = _u(o_i, e6id_to_vec)
        if um == uo:
            t1 += 1
        else:
            t2 += 1
    assert len(sign_map) == 864
    assert (t1, t2) == (432, 432)

    # Symplectic delta law on the t=2 regime.
    for (c_i, m_i, o_i), _sgn in sign_map.items():
        uc = _u(c_i, e6id_to_vec)
        um = _u(m_i, e6id_to_vec)
        uo = _u(o_i, e6id_to_vec)
        if um == uo:
            continue
        d = _u2_sub(um, uc)
        assert uo == ((uc[0] - d[0]) % 3, (uc[1] - d[1]) % 3)
        dz = (_z(o_i, e6id_to_vec) - _z(m_i, e6id_to_vec)) % 3
        assert dz == omega(uc, d)

    # Extract constant (uc,d) pairs from the data in each regime.
    t1_signs: dict[tuple[tuple[int, int], tuple[int, int]], set[int]] = defaultdict(set)
    t2_signs: dict[tuple[tuple[int, int], tuple[int, int]], set[int]] = defaultdict(set)
    for (c_i, m_i, o_i), sgn in sign_map.items():
        uc = _u(c_i, e6id_to_vec)
        um = _u(m_i, e6id_to_vec)
        uo = _u(o_i, e6id_to_vec)
        d = _u2_sub(um, uc)
        if um == uo:
            t1_signs[(uc, d)].add(int(sgn))
        else:
            t2_signs[(uc, d)].add(int(sgn))

    const_t1 = {k for k, v in t1_signs.items() if len(v) == 1}
    const_t2 = {k for k, v in t2_signs.items() if len(v) == 1}
    assert const_t1 == const_t2
    assert len(const_t1) == 18

    # Closed-form constant-line prediction.
    pred: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for uc in [(i, j) for i in range(3) for j in range(3)]:
        for d in [
            (a, b) for a in range(3) for b in range(3) if not (a == 0 and b == 0)
        ]:
            kd = k_of_direction(d)
            if kd is None:
                continue
            if omega(uc, d) == kd:
                pred.add((uc, d))
    assert pred == const_t1
