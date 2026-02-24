from __future__ import annotations

from scripts.monomial_utils import monomial_group_order, find_sign_lifts_for_group
from scripts.w33_monster_11a_m12_golay_bridge import analyze as analyze_11a


def test_generic_monomial_lift_reproduces_2m12():
    # reuse the 11A bridge to get perms and code rows
    rep = analyze_11a(compute_monomial_order=False)
    assert rep.get("available") is True
    golay = rep.get("golay", {})
    # pick perms in code coords from earlier bridge output
    perms = []
    if golay.get("m12_generators_in_code_coords"):
        perms.append(tuple(golay["m12_generators_in_code_coords"]["b11_code_perm"]))
        perms.append(tuple(golay["m12_generators_in_code_coords"]["b21_code_perm"]))
    # we need the generator rows and code set, reconstruct as in bridge
    from tools.s12_universal_algebra import (
        enumerate_linear_code_f3,
        ternary_golay_generator_matrix,
    )

    gen = ternary_golay_generator_matrix()
    generator_rows = [tuple(int(x) % 3 for x in row) for row in gen]
    code_set = set(enumerate_linear_code_f3(gen))

    lifts = find_sign_lifts_for_group(perms, generator_rows, code_set)
    assert lifts is not None
    # compute order using monomial_group_order; should equal 190080
    gens = list(zip(perms, lifts))
    order = monomial_group_order(gens)
    assert order == 190_080
