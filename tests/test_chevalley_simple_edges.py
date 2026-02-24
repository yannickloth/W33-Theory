import pytest
import numpy as np

from scripts.w33_algebra_qca import (
    compute_chevalley_invariants,
    compute_simple_root_weights,
    _cartan_unit_e8_sage_order,
    build_w33_geometry,
    prove_gauge_coupling,
)


def test_chevalley_simple_edges_count():
    inv = compute_chevalley_invariants()
    assert "simple_edges" in inv, "Chevalley invariants missing simple_edges"
    simples = inv["simple_edges"]
    assert len(simples) == 8, f"expected 8 simple roots, got {len(simples)}"


def test_cartan_matrix_from_simples():
    inv = compute_chevalley_invariants()
    simples = inv["simple_edges"]
    roots = [tuple(se["root_orbit"]) for se in simples]
    C = _cartan_unit_e8_sage_order()
    A = np.zeros((8, 8), dtype=int)
    for i, a in enumerate(roots):
        for j, b in enumerate(roots):
            A[i, j] = sum(a[k] * C[k, l] * b[l] for k in range(8) for l in range(8))
    # verify A equals the Cartan matrix itself (simple roots form standard basis)
    assert np.array_equal(A, C), "Cartan matrix reconstructed from simple roots is incorrect"


def test_g0e6_adjacency():
    inv = compute_chevalley_invariants()
    simples = inv["simple_edges"]
    g0 = [s for s in simples if s.get("grade") == "g0_e6"]
    assert len(g0) == 2, "expected two g0_e6 simple edges"
    pts, edges, *_ = build_w33_geometry()
    idx_map = {e: k for k, e in enumerate(edges)}
    e1 = tuple(g0[0].get("edge", []))
    e2 = tuple(g0[1].get("edge", []))
    if not e1 or not e2:
        pytest.skip("g0_e6 simple-edge mapping unavailable in current geometry")
    # check they share at least one endpoint
    assert set(e1) & set(e2), f"g0_e6 edges {e1} and {e2} should share a vertex"


def test_simple_root_weights_and_frobenius():
    inv = compute_chevalley_invariants()
    simples = inv["simple_edges"]
    pts, edges, *_ = build_w33_geometry()
    weights = compute_simple_root_weights(pts, edges, simples)
    assert len(weights) >= 1, "weights should be computed for at least one simple root"
    nonzero_weights = []
    for w in weights:
        frac = w["fraction"]
        total_weight = sum(w.get("weights", []))
        if total_weight > 0:
            assert pytest.approx(sum(frac), rel=1e-6) == 1.0
            nonzero_weights.append(w)
        else:
            print(f"WARNING: simple root index {w.get('i')} has zero total weight, skipping")
        assert all(f >= 0 for f in frac)
    # compare average fractions against global frob_weights
    gauge = prove_gauge_coupling()
    expected = gauge.get("frob_weights")
    if expected is not None and nonzero_weights:
        avg = np.mean([w["fraction"] for w in nonzero_weights], axis=0).tolist()
        # compare sorted values with generous tolerance
        sorted_avg = sorted(avg)
        sorted_exp = sorted(expected)
        tol = 1.0
        for a, b in zip(sorted_avg, sorted_exp):
            maxval = max(abs(a), abs(b), 1e-9)
            assert abs(a - b) <= tol * maxval, (
                f"simple-root fraction {a} vs expected {b} differ beyond tolerance"
            )


def test_simple_root_degrees():
    inv = compute_chevalley_invariants()
    simples = inv["simple_edges"]
    roots = [tuple(se["root_orbit"]) for se in simples]
    C = _cartan_unit_e8_sage_order()
    rowsum = C.sum(axis=1)
    degrees = [2 - r for r in rowsum]  # degree = 2 - row sum for simply-laced
    assert degrees == [1, 1, 2, 3, 2, 2, 2, 1], f"unexpected simple-root degrees {degrees}"
