from __future__ import annotations

import numpy as np

from scripts.monomial_utils import (
    perm_inverse,
    monomial_mul,
    monomial_inv,
    monomial_group_order,
    apply_monomial,
    find_sign_lift_for_perm,
    find_sign_lifts_for_group,
)


def test_permutation_inverse_and_mul():
    perm = (2, 0, 1)
    inv = perm_inverse(perm)
    assert inv == (1, 2, 0)
    # multiply by inverse gives identity
    assert monomial_mul((perm, (1, 1, 1)), (inv, (1, 1, 1))) == (
        (0, 1, 2), (1, 1, 1)
    )


def test_monomial_inverse():
    elem = ((1, 0), (2, 1))
    inv = monomial_inv(elem)
    # test that mul gives identity
    assert monomial_mul(elem, inv) == ((0, 1), (1, 1))


def test_group_order_small():
    # trivial group
    assert monomial_group_order([]) == 1
    # single order-2 element (swap)
    g = ((1, 0), (1, 1))
    assert monomial_group_order([g]) == 2


def test_apply_and_find_sign():
    # simple code: words of length 3 over F3 where sum=0
    code = {(0, 0, 0), (1, 1, 1), (2, 2, 2)}
    gen_rows = list(code)
    perm = (1, 2, 0)
    signs = find_sign_lift_for_perm(perm=perm, generator_rows=gen_rows, code_set=code)
    # in this trivial case, permutation alone works (signs all 1)
    assert signs == (1, 1, 1)
    # test apply_monomial
    w = (1, 1, 1)
    assert apply_monomial(w, perm, signs) == (1, 1, 1)


def test_find_signs_group():
    # two perms wrt same simple code above
    perms = [(1, 2, 0), (2, 0, 1)]
    code = {(0, 0, 0), (1, 1, 1), (2, 2, 2)}
    gens = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    lifts = find_sign_lifts_for_group(perms, gens, code)
    assert lifts == [(1, 1, 1), (1, 1, 1)]


def test_bridge_report_factories():
    from scripts.w33_monster_structure_bridge_report import _MONOMIAL_FACTORIES
    assert "11A" in _MONOMIAL_FACTORIES
    assert "identity" in _MONOMIAL_FACTORIES
    perms = _MONOMIAL_FACTORIES["11A"]()
    assert isinstance(perms, list) and len(perms) == 2
    for perm in perms:
        assert len(perm) == 12
