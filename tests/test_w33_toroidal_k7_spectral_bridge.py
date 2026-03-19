from w33_toroidal_k7_spectral_bridge import build_toroidal_k7_spectral_summary


def test_toroidal_k7_dictionary_is_exact() -> None:
    summary = build_toroidal_k7_spectral_summary()
    data = summary["toroidal_k7_dictionary"]

    assert data["toroidal_seed_order"] == 7
    assert data["csaszar_vertex_graph"] == "K7"
    assert data["szilassi_face_graph"] == "K7"
    assert data["adjacency_spectrum"] == [6, -1, -1, -1, -1, -1, -1]
    assert data["laplacian_spectrum"] == [0, 7, 7, 7, 7, 7, 7]
    assert data["selector_line_dimension"] == 1
    assert data["shared_six_channel"] == 6
    assert data["phi6"] == 7
    assert data["adjacency_square_trace"] == 42
    assert data["laplacian_trace"] == 42


def test_toroidal_k7_factorizations_hold() -> None:
    summary = build_toroidal_k7_spectral_summary()
    exact = summary["exact_factorizations"]

    assert exact["csaszar_vertex_graph_is_k7"] is True
    assert exact["szilassi_face_graph_is_k7"] is True
    assert exact["selector_plus_shared_six_equals_toroidal_seed_order"] is True
    assert exact["nontrivial_laplacian_mode_equals_phi6"] is True
    assert exact["nontrivial_adjacency_multiplicity_equals_shared_six"] is True
    assert exact["laplacian_trace_equals_shared_six_times_phi6"] is True
    assert exact["adjacency_square_trace_equals_shared_six_times_phi6"] is True
