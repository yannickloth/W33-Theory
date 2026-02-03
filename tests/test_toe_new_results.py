import json
from pathlib import Path


def _load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_toe_sm_decomposition_27_basic_counts():
    data = _load("artifacts/toe_sm_decomposition_27.json")
    assert data["status"] == "ok"
    tri = data["triads"]
    assert tri["total"] == 45
    assert tri["forbidden"] == 9
    assert tri["forbidden_partitions_vertices"] is True
    # Two Qψ patterns: 16·16·10 and 10·10·1 (scaled by 3)
    pats = {
        (tuple(x["qpsi3"]), x["count"], x["forbidden"])
        for x in tri["qpsi3_pattern_counts"]
    }
    assert (tuple([-2, 1, 1]), 40, 8) in pats
    assert (tuple([-2, -2, 4]), 5, 1) in pats


def test_toe_affine_plane_duality_counts():
    data = _load("artifacts/toe_affine_plane_duality.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts["bad_triads"] == 9
    assert counts["triads_total"] == 45
    assert counts["triads_allowed"] == 36
    assert counts["double_sixes"] == 36
    assert counts["affine_points"] == 9
    assert counts["affine_lines"] == 12
    assert counts["z3_lifts_per_line"] == 3
    lines = data["duality_by_line"]
    assert len(lines) == 12
    for row in lines:
        assert len(row["allowed_triads_cycle"]) == 3
        assert len(row["double_sixes_cycle"]) == 3
        assert len(row["z3_equivariant_pairing"]) == 3


def test_toe_three_generation_coupling_atlas_counts():
    data = _load("artifacts/toe_three_generation_coupling_atlas.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts["couplings_total"] == 1620
    assert counts["couplings_forbidden"] == 324
    assert counts["couplings_allowed"] == 1296
    pairs = counts["orbit_pairs"]
    assert len(pairs) == 6
    for row in pairs:
        assert row["total"] == 270
        assert row["forbidden"] == 54
        assert row["allowed"] == 216

    # Sanity spot-check: up-Yukawa-type triads are more suppressed (2/6 triads forbidden => 1/3)
    triad_types = {tuple(t["fields"]): t for t in data["triad_types"]}
    assert triad_types[("H_u", "Q", "u^c")]["forbidden_frac"] == 72 / 216


def test_toe_yukawa_textures_has_up_yukawa_texture():
    data = _load("artifacts/toe_yukawa_textures.json")
    assert data["status"] == "ok"
    blocks = {tuple(b["type"]): b for b in data["textures"]}
    up = blocks[("H_u", "Q", "u^c")]
    assert up["total"] == 6
    assert up["forbidden"] == 2


def test_toe_phase_diagram_charge_alignment_basic():
    data = _load("artifacts/toe_phase_diagram_charge_alignment.json")
    assert data["status"] == "ok"
    grid = data["grid"]
    fw = grid["firewall_strength"]
    sig = grid["phase_noise_sigma"]
    assert len(fw) >= 2 and len(sig) >= 2
    cells = data["cells"]
    assert len(cells) == len(fw)
    assert all(len(row) == len(sig) for row in cells)

    allowed = {"Y", "Qpsi", "Qchi", "T3"}
    for row in cells:
        for cell in row:
            assert cell["best"]["label"] in allowed
            sim = float(cell["best"]["sim"])
            assert 0.0 <= sim <= 1.0


def test_toe_affine_plane_interaction_dictionary_invariants():
    data = _load("artifacts/toe_affine_plane_interaction_dictionary.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts["blocks"] == 9
    assert counts["affine_lines"] == 12
    assert counts["triads_total"] == 45
    assert counts["triads_forbidden"] == 9
    assert counts["triads_allowed"] == 36
    assert counts["couplings_total"] == 1620
    assert counts["couplings_per_triad"] == 36
    assert counts["couplings_per_allowed_line"] == 108

    blocks = data["blocks"]
    assert len(blocks) == 9
    for b in blocks:
        assert b["couplings_total"] == 36
        assert b["couplings_forbidden"] == 36

    lines = data["lines"]
    assert len(lines) == 12
    for row in lines:
        assert row["couplings_total"] == 108
        assert len(row["allowed_triads_cycle"]) == 3
        assert len(row["double_sixes_cycle"]) == 3


def test_toe_d5_root_fragility_counts_and_zero_bad_mass():
    data = _load("artifacts/toe_d5_root_fragility.json")
    assert data["status"] == "ok"
    assert data["d5_deleted_node"] == 0
    assert data["counts"] == {"D5_root": 40, "compl_minus": 16, "compl_plus": 16}
    for r in data["roots"]:
        assert r["mass"]["bad"] == 0.0
        assert r["mass"]["bad_frac"] == 0.0


def test_toe_z3_lift_constraint_offsets_and_examples():
    data = _load("artifacts/toe_z3_lift_constraint.json")
    assert data["status"] == "ok"
    blocks = data["blocks"]
    assert blocks["rank"] == 6
    assert blocks["offsets_z3"] == [2, 1, 0, 1, 1, 0, 1, 0, 0]
    # Check sample triads satisfy sum(t')=0 mod 3
    for ex in data["triads"]["examples"]:
        assert sum(ex["t_shifted"]) % 3 == 0


def test_toe_affine_plane_z3_connection_invariants():
    data = _load("artifacts/toe_affine_plane_z3_connection.json")
    assert data["status"] == "ok"
    assert data["compiled_allowed_triads_match_reference"] is True
    counts = data["counts"]
    assert counts["blocks"] == 9
    assert counts["vertices"] == 27
    assert counts["affine_lines"] == 12
    assert counts["parallel_classes"] == 4
    assert counts["orbit_type_hist"] == {"(0, 0, 0)": 4, "(0, 1, 2)": 4, "(0, 2, 1)": 4}
    assert counts["lambda_hist"] == {"0": 4, "1": 4, "2": 4}

    blocks = data["blocks"]
    assert len(blocks) == 9
    coords = {tuple(b["coord_f3_2"]) for b in blocks}
    assert len(coords) == 9

    lines = data["lines"]
    assert len(lines) == 12
    for row in lines:
        assert len(row["blocks"]) == 3
        assert len(row["allowed_triads_cycle"]) == 3
        for tri in row["allowed_triads_cycle"]:
            assert sum(tri["t_shifted_param_order"]) % 3 == 0


def test_toe_affine_plane_z3_holonomy_basic():
    data = _load("artifacts/toe_affine_plane_z3_holonomy.json")
    assert data["status"] == "ok"
    assert data["constant_curvature_minus_det"] is True
    counts = data["counts"]
    assert counts["points"] == 9
    assert counts["direction_pairs"] == 6
    assert counts["loops"] == 54
    hist = {k: int(v) for k, v in data["holonomy_hist"].items()}
    assert sum(hist.values()) == counts["loops"]
    # Current canonical gauge has maximally nontrivial Z3 curvature (no zero-holonomy plaquettes).
    assert hist == {"1": 27, "2": 27}
    for row in data["by_direction_pair"]:
        det = int(row["det"])
        expected = (-det) % 3
        assert int(row["expected_hol_minus_det"]) == expected
        keys = list(row["hist"].keys())
        assert len(keys) == 1
        assert int(keys[0]) == expected


def test_toe_compiled_coupling_mask_counts_and_lines():
    data = _load("artifacts/toe_compiled_coupling_mask.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts["triads_total"] == 45
    assert counts["triads_forbidden"] == 9
    assert counts["triads_allowed"] == 36
    assert counts["couplings_per_triad"] == 36
    assert counts["couplings_total"] == 1620
    assert counts["couplings_forbidden"] == 324
    assert counts["couplings_allowed"] == 1296
    assert len(data["forbidden_triads"]) == 9
    assert len(data["allowed_triads"]) == 36
    assert len(data["affine_line_block_triples"]) == 12
    assert data["affine_line_lifts_per_line"] == [3]


def test_toe_compiled_superpotential_terms_basic():
    data = _load("artifacts/toe_compiled_superpotential_terms.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts == {
        "blocks": 9,
        "affine_lines": 12,
        "triads_total": 45,
        "triads_forbidden": 9,
        "triads_allowed": 36,
    }
    blocks = data["blocks"]
    assert len(blocks) == 9
    # Spot-check: two distinct forbidden blocks are up-Yukawa (Hu,Q,uc)
    up = [b for b in blocks if b["forbidden_triad"]["fields"] == ["H_u", "Q", "u^c"]]
    assert len(up) == 2
    lines = data["lines"]
    assert len(lines) == 12
    for row in lines:
        assert len(row["allowed_triads_cycle"]) == 3
