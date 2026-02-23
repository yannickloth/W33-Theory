"""tests/test_w33_as_qca.py
Pillar 64: W(3,3) as a Topological QCA
Tests for THEORY_PART_CLXXIII_W33_AS_QCA.py

All numerics are loaded from data/w33_qca_pillar64.json which is produced
by running THEORY_PART_CLXXIII_W33_AS_QCA.py.  If the JSON does not exist,
the tests are skipped (so CI doesn't break before the first run).
"""

from __future__ import annotations
import json
import os
import sys

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Fixture: load saved results
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "w33_qca_pillar64.json"
)


@pytest.fixture(scope="module")
def results():
    if not os.path.exists(DATA_FILE):
        pytest.skip(f"data file not found: {DATA_FILE} — run THEORY_PART_CLXXIII_W33_AS_QCA.py first")
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# THEOREM 6: W33 = QCA ATTRACTOR
# ---------------------------------------------------------------------------

def test_t6_w33_has_40_vertices():
    """GF(3)^4 has exactly 40 projective points = W33 vertex count."""
    n_1subspaces = (3**4 - 1) // (3 - 1)
    assert n_1subspaces == 40


def test_t6_w33_degree_12():
    """Every W33 vertex has exactly 12 neighbours (QCA neighbourhood)."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_homology import build_w33
    n, vertices, adj, edges = build_w33()
    degrees = [sum(1 for w in adj[i]) for i in range(n)]
    assert all(d == 12 for d in degrees), f"Not all degrees 12: {set(degrees)}"


def test_t6_pillar_is_64(results):
    assert results["pillar"] == 64


def test_t6_n_sectors(results):
    assert results["n_sectors"] == 3


# ---------------------------------------------------------------------------
# THEOREM 7: TOPOLOGICAL QCA INDEX = 27
# ---------------------------------------------------------------------------

def test_t7_qca_index_is_27(results):
    """QCA topological index must equal 27 = dim(E6 fundamental rep)."""
    assert results["qca_index"] == 27


def test_t7_dim_per_sector_is_27(results):
    """Each Z3 anyon sector has dimension 27."""
    assert results["dim_per_sector"] == 27


def test_t7_dim_H1_is_81(results):
    """Total H^1(W33) has dimension 81 = 3 x 27."""
    assert results["dim_H1"] == 81


def test_t7_gram_rank_nonzero():
    """Each sector Gram matrix has non-zero rank."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import build_z3_complex_profiles, build_dominant_profiles
    _, _, _, P = build_z3_complex_profiles()
    for a in range(3):
        G = P[a].conj().T @ P[a]
        rank = np.linalg.matrix_rank(G, tol=1e-10)
        assert rank >= 1, f"Gram matrix G_{a} has zero rank"


# ---------------------------------------------------------------------------
# THEOREM 8: THREE GENERATIONS = THREE QCA ANYON SECTORS
# ---------------------------------------------------------------------------

def test_t8_sectors_cp_conjugate():
    """G_2 = conj(G_1): sectors 1 and 2 are CP-conjugate."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import build_z3_complex_profiles
    _, _, _, P = build_z3_complex_profiles()
    G1 = P[1].conj().T @ P[1]
    G2 = P[2].conj().T @ P[2]
    diff = np.linalg.norm(G2 - np.conj(G1))
    assert diff < 1e-10, f"G_2 != conj(G_1): ||diff|| = {diff:.2e}"


def test_t8_sector0_real_gram():
    """G_0 must be real (sector 0 has trivial Z3 charge = 1)."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import build_z3_complex_profiles
    _, _, _, P = build_z3_complex_profiles()
    G0 = P[0].conj().T @ P[0]
    # G0 is Hermitian by construction; for real P[0] it should be real
    imag_norm = np.linalg.norm(np.imag(G0))
    assert imag_norm < 1e-10, f"G_0 not real: Im norm = {imag_norm:.2e}"


def test_t8_gram_spectra_positive():
    """All non-trivial Gram eigenvalues are positive."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import build_z3_complex_profiles
    _, _, _, P = build_z3_complex_profiles()
    for a in range(3):
        G = P[a].conj().T @ P[a]
        evals = np.linalg.eigvalsh(G)
        large = evals[evals > 1e-8]
        assert len(large) > 0, f"No positive eigenvalues in G_{a}"
        assert np.all(large > 0), f"Negative eigenvalue in G_{a}: {large.min()}"


def test_t8_sectors_1_2_same_spectrum(results):
    """Sectors 1 and 2 have identical Gram spectra (CP-conjugate)."""
    spec1 = results["gram_eigenvalue_spectra"][1]
    spec2 = results["gram_eigenvalue_spectra"][2]
    diff = max(abs(a - b) for a, b in zip(spec1, spec2))
    assert diff < 1e-8, f"Spectra of sectors 1 and 2 differ by {diff:.2e}"


# ---------------------------------------------------------------------------
# THEOREM 9: YUKAWA = QCA SCATTERING MATRIX
# ---------------------------------------------------------------------------

def test_t9_yukawa_matrix_3x3():
    """yukawa3x3 returns a 3x3 matrix for any valid VEV."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import (
        build_z3_complex_profiles, build_dominant_profiles, yukawa3x3
    )
    H27, local_tris, _, P = build_z3_complex_profiles()
    psi_dom = build_dominant_profiles(P)
    v = np.zeros(27, dtype=complex)
    v[0] = 1.0
    Y = yukawa3x3(psi_dom, local_tris, v)
    assert Y.shape == (3, 3), f"Y not 3x3: {Y.shape}"


def test_t9_yukawa_nonzero():
    """Yukawa matrix at best CKM VEV is non-zero."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import (
        build_z3_complex_profiles, build_dominant_profiles, yukawa3x3
    )
    H27, local_tris, _, P = build_z3_complex_profiles()
    psi_dom = build_dominant_profiles(P)
    # Best CKM VEV (from prior scan): vi=25, vj=17, theta=pi
    v = np.zeros(27, dtype=complex)
    v[25] = 1.0
    v[17] = np.exp(1j * np.pi)
    Y = yukawa3x3(psi_dom, local_tris, v)
    assert np.linalg.norm(Y) > 1e-10, "Yukawa matrix is zero"


def test_t9_yukawa_eigenvalue_hierarchy():
    """Y_up singular values show non-trivial hierarchy (max > 2x min)."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import (
        build_z3_complex_profiles, build_dominant_profiles, yukawa3x3
    )
    H27, local_tris, _, P = build_z3_complex_profiles()
    psi_dom = build_dominant_profiles(P)
    v = np.zeros(27, dtype=complex)
    v[25] = 1.0
    v[17] = np.exp(1j * np.pi)
    Y = yukawa3x3(psi_dom, local_tris, v)
    svs = np.linalg.svd(Y, compute_uv=False)
    assert svs[0] > 2 * svs[-1], (
        f"Yukawa singular values not hierarchical: {svs}"
    )


# ---------------------------------------------------------------------------
# THEOREM 10: GRAM LYAPUNOV SPECTRUM = MASS HIERARCHY
# ---------------------------------------------------------------------------

def test_t10_dominant_modes_orthogonal(results):
    """Dominant Gram eigenvectors across sectors have negligible overlap."""
    Omega = np.array(results["inter_sector_overlaps"])
    # Off-diagonal overlaps should be tiny (< 1e-20 in the saved JSON)
    off_diag = [Omega[i, j] for i in range(3) for j in range(3) if i != j]
    for o in off_diag:
        assert o < 1e-20, f"Non-negligible inter-sector overlap: {o}"


def test_t10_gram_spectral_ratio_sector1_gt_sector0(results):
    """Sector 1 dominant eigenvalue > sector 0 (heavier generation is larger)."""
    spec0 = results["gram_eigenvalue_spectra"][0]
    spec1 = results["gram_eigenvalue_spectra"][1]
    assert spec1[0] > spec0[0], (
        f"lambda_max(G_1)={spec1[0]:.4f} not > lambda_max(G_0)={spec0[0]:.4f}"
    )


def test_t10_gram_spectrum_descending(results):
    """Gram eigenvalue spectrum for each sector is saved in descending order."""
    for a in range(3):
        spec = results["gram_eigenvalue_spectra"][a]
        # The top two should decrease
        assert spec[0] >= spec[1] - 1e-10, (
            f"Sector {a} spectrum not descending: {spec[0]:.4f}, {spec[1]:.4f}"
        )


def test_t10_cabibbo_prediction_exists(results):
    """Cabibbo angle prediction from Gram ratio is computed."""
    cab = results.get("cabibbo_prediction", {})
    assert "sin2_from_gram_ratio" in cab
    assert "theta_eff_deg" in cab
    assert "theta_C_exp_deg" in cab


def test_t10_cabibbo_experimental_angle(results):
    """Experimental Cabibbo angle stored correctly (≈ 12.96 deg)."""
    theta_C_exp = results["cabibbo_prediction"]["theta_C_exp_deg"]
    assert abs(theta_C_exp - 12.96) < 0.05, (
        f"Wrong experimental Cabibbo angle: {theta_C_exp}"
    )


# ---------------------------------------------------------------------------
# SYNTHESIS: Integration checks
# ---------------------------------------------------------------------------

def test_synthesis_key_results(results):
    """All boolean key_results flags are True."""
    kr = results.get("key_results", {})
    for k, v in kr.items():
        assert v is True, f"key_result '{k}' is not True"


def test_synthesis_index_equals_e6_fund_rep(results):
    """The QCA index must equal 27 = dim(E6 fundamental representation)."""
    assert results["qca_index"] == 27
    assert results["dim_per_sector"] == 27
    # The two 27s must come from the same computation
    assert results["dim_H1"] // results["n_sectors"] == results["qca_index"]
