import math

import numpy as np
import pytest

from scripts.w33_entropic_gravity import (
    analyze_entropic_gravity,
    compute_bekenstein_and_channel,
    compute_entanglement_entropy,
    compute_entropic_force,
    compute_graph_entropy,
    compute_hodge_entropy,
    compute_mutual_information_matrix,
)
from scripts.w33_homology import build_clique_complex, build_w33


def test_graph_entropy_basic():
    n, vertices, adj, edges = build_w33()
    ge = compute_graph_entropy(adj, n)
    assert "von_neumann_entropy_laplacian" in ge
    assert ge["von_neumann_entropy_laplacian"] >= 0.0
    assert ge["degree_entropy"] >= 0.0
    assert ge["partition_function_Z"] > 0.0


def test_hodge_entropy_values():
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    he = compute_hodge_entropy(simplices, edges)
    assert math.isclose(he["S_matter_log81"], math.log(81), rel_tol=1e-12)
    assert math.isclose(he["S_total_log240"], math.log(240), rel_tol=1e-12)
    # multiplicities present
    mults = he["hodge_multiplicities"]
    assert int(mults.get(0, 0)) == 81


def test_bekenstein_and_channel_checks():
    n, vertices, adj, edges = build_w33()
    bek = compute_bekenstein_and_channel(adj, n, edges)
    assert bek["area_edges"] == 240
    assert math.isclose(bek["bekenstein_entropy"], 60.0, rel_tol=1e-12)
    assert math.isclose(bek["lovasz_theta"], 10.0, rel_tol=1e-12)
    assert bek["independence_number"] == 7
    assert bek["channel_capacity_bits"] > 0


def test_entanglement_area_law():
    n, vertices, adj, edges = build_w33()
    ent = compute_entanglement_entropy(adj, n, edges)
    # expect 20 rows for subset_size 1..20
    assert len(ent) == 20
    mid = [r for r in ent if 3 <= r["subset_size"] <= 17]
    vals = [r["entropy_per_cut"] for r in mid]
    # area-law: entropy_per_cut should be relatively stable (low coef of variation)
    mean = float(np.mean(vals))
    std = float(np.std(vals))
    assert mean > 0
    assert (std / (mean + 1e-12)) < 0.6


def test_entropic_force_properties():
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    force = compute_entropic_force(simplices)
    assert force["spectral_gap"] >= 0
    assert force["temperature"] > 0
    assert force["verlinde_force"] == force["temperature"] * force["entropic_force"]


def test_mutual_information_diameter():
    n, vertices, adj, edges = build_w33()
    mi = compute_mutual_information_matrix(adj, n)
    # W(3,3) is small-diameter (diameter 2)
    assert mi["diameter"] == 2


def test_analyze_entropic_gravity_runs():
    res = analyze_entropic_gravity()
    assert "bekenstein" in res
    assert "hodge_entropy" in res
    assert "entropic_force" in res
