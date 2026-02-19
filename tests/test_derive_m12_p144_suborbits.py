from scripts.derive_m12_p144_suborbits import (
    cosets_right,
    find_psl2_11_subgroup,
    generate_group,
    inv,
    orbit_sizes_on_cosets,
    perm_from_cycles,
)


def test_m12_p144_suborbits_match_expected():
    b11 = perm_from_cycles(12, [[1, 4], [3, 10], [5, 11], [6, 12]])
    b21 = perm_from_cycles(12, [[1, 8, 9], [2, 3, 4], [5, 12, 11], [6, 10, 7]])
    gens = [b11, b21, inv(b11), inv(b21)]

    g_elems = generate_group(gens)
    assert len(g_elems) == 95040

    found = find_psl2_11_subgroup(g_elems)
    h = found.subgroup
    assert len(h) == 660

    coset_reps, coset_of = cosets_right(g_elems, h)
    suborbits = sorted(
        orbit_sizes_on_cosets(
            coset_reps, coset_of, [found.a2, found.b3, inv(found.a2), inv(found.b3)]
        )
    )

    assert suborbits == [1, 11, 11, 55, 66]
