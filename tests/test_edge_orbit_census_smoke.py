import os
import pytest


@pytest.mark.skipif(os.environ.get("RUN_LONG_TESTS") != "1", reason="long tests disabled")
def test_edge_orbit_census_smoke():
    from scripts.edge_to_e8_mapping import compute_edge_orbit_ids

    edge_to_orbit, orbit_sizes = compute_edge_orbit_ids()
    assert isinstance(edge_to_orbit, list)
    assert len(edge_to_orbit) == 240
    assert isinstance(orbit_sizes, dict)
    assert sum(orbit_sizes.values()) >= 1