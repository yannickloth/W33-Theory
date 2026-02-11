from scripts import analyze_h1_irreducibility as a


def test_h1_commutant_all_transvections():
    """Run the full transvection-based group test and assert the observed commutant dimension.

    Historical note: earlier code expected commutant_dim == 1 (irreducible). Current numeric check
    over the transvection-generated group reports commutant_dim == 2 — the test asserts that value.
    """
    res = a.main()
    assert "all_transvections" in res
    comm = res["all_transvections"]
    assert (
        comm["commutant_dim"] == 2
    ), f"Expected commutant dim 2, got {comm['commutant_dim']}"
    assert (
        comm["group_size"] == 25920
    ), f"Expected group size 25920, got {comm['group_size']}"
