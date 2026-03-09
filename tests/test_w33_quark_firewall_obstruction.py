from collections import Counter

from w33_quark_firewall_obstruction import build_quark_firewall_obstruction


def test_firewall_triads_split_into_expected_sector_families_and_heisenberg_points():
    obstruction = build_quark_firewall_obstruction()

    families = Counter(record.family for record in obstruction.firewall_triads)
    assert families == Counter(
        {
            "singlet_higgs": 1,
            "lepton_down": 1,
            "lepton_up": 1,
            "antiquark_triplet": 3,
            "quark_triplet": 3,
        }
    )

    assert tuple(record.heisenberg_xy for record in obstruction.firewall_triads) == (
        (0, 0),
        (0, 1),
        (0, 2),
        (2, 0),
        (1, 0),
        (2, 1),
        (1, 2),
        (2, 2),
        (1, 1),
    )

    assert obstruction.firewall_triads[0].slots == ("S", "H_2", "Hbar_2")
    assert obstruction.firewall_triads[1].slots == ("L_2", "e_c", "Hbar_1")
    assert obstruction.firewall_triads[2].slots == ("L_1", "nu_c", "H_1")
    assert obstruction.firewall_triads[3].slots == ("d_c_3", "u_c_2", "Tbar_1")
    assert obstruction.firewall_triads[6].slots == ("Q_1_1", "Q_2_2", "T_3")


def test_induced_quark_support_is_exactly_triplet_firewall_mediated():
    obstruction = build_quark_firewall_obstruction()

    assert obstruction.triplet_heavy_slots == (
        "T_1",
        "T_2",
        "T_3",
        "Tbar_1",
        "Tbar_2",
        "Tbar_3",
    )
    assert obstruction.quark_triad_indices == (6, 7, 8)
    assert obstruction.antiquark_triad_indices == (3, 4, 5)
    assert obstruction.support_light_source_e6ids == (
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
    )
    assert obstruction.up_triplet_pairs == (
        (6, 3),
        (6, 4),
        (6, 5),
        (7, 3),
        (7, 4),
        (7, 5),
        (8, 3),
        (8, 4),
        (8, 5),
    )
    assert obstruction.down_triplet_pairs == obstruction.up_triplet_pairs

    assert obstruction.quark_support_vanishes_without_triplets is True
    assert obstruction.leptonic_support_survives_without_triplets is True
    assert obstruction.triplet_only_support_is_quark_only is True

    subset_full, subset_nontriplet, subset_triplet = obstruction.heavy_subset_support
    assert subset_full.up_quark_support == 15
    assert subset_full.down_quark_support == 17
    assert subset_full.up_lepton_support == 2
    assert subset_full.down_lepton_support == 2
    assert subset_nontriplet.up_quark_support == 0
    assert subset_nontriplet.down_quark_support == 0
    assert subset_nontriplet.up_lepton_support == 2
    assert subset_nontriplet.down_lepton_support == 2
    assert subset_triplet.up_quark_support == 3
    assert subset_triplet.down_quark_support == 5
    assert subset_triplet.up_lepton_support == 0
    assert subset_triplet.down_lepton_support == 0


def test_full_su3_su2_screen_leaves_no_nonzero_clean_quark_block():
    obstruction = build_quark_firewall_obstruction()
    screen = obstruction.screen_summary

    assert screen.sample_weak_count == 2
    assert screen.sample_color_count == 2
    assert screen.sample_up_nullity == 4
    assert screen.sample_down_nullity == 4

    assert screen.full_weak_count == 3
    assert screen.full_color_count == 8
    assert screen.full_up_nullity == 0
    assert screen.full_down_nullity == 0
    assert obstruction.full_clean_quark_block_exists is False
