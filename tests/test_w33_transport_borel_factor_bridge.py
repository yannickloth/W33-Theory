from exploration.w33_transport_borel_factor_bridge import (
    build_transport_borel_factor_summary,
)


def test_reduced_holonomy_is_exact_borel_group():
    summary = build_transport_borel_factor_summary()
    borel = summary["reduced_borel_group"]

    assert borel["group_order"] == 6
    assert borel["all_elements_have_form_upper_borel_1_c_0_s"] is True
    assert borel["parameter_counts_by_c_and_s"] == {
        "c=0,s=1": 528,
        "c=0,s=2": 766,
        "c=1,s=1": 1317,
        "c=1,s=2": 670,
        "c=2,s=1": 1275,
        "c=2,s=2": 724,
    }


def test_parity_zero_splits_into_flat_and_pure_nilpotent_channels():
    summary = build_transport_borel_factor_summary()
    split = summary["triangle_channel_split"]

    assert split["parity0_total"] == 3120
    assert split["parity1_total"] == 2160
    assert split["flat_total"] == 528
    assert split["pure_nilpotent_total"] == 2592
    assert split["semisimple_curved_total"] == 2160
    assert split["parity0_splits_as_flat_plus_pure_nilpotent"] is True


def test_channel_multiplicities_are_exact():
    summary = build_transport_borel_factor_summary()
    split = summary["triangle_channel_split"]

    assert split["pure_nilpotent_channel_counts"] == {"1": 1317, "2": 1275}
    assert split["semisimple_channel_counts"] == {"0": 766, "1": 670, "2": 724}
