from collections import Counter
from fractions import Fraction

import numpy as np

from w33_finite_spectral_triple import (
    GENERATION_COUNT,
    MATTER_DIM,
    PER_GENERATION_DIM,
    TOTAL_DIM,
    build_w33_finite_spectral_triple,
    canonical_generation_basis,
    color_factor_operator_27,
    finite_dirac_162,
    grading_162,
    higgs_contracted_mass_matrix_27,
    hypercharge_operator_27,
    hypercharge_operator_162,
    matter_basis,
    quaternion_matrix,
    real_structure_162,
    source_order_per_canonical,
    weak_doublet_blocks_27,
    weak_factor_operator_27,
)


def test_generation_basis_has_expected_particle_content():
    basis = canonical_generation_basis()
    assert len(basis) == PER_GENERATION_DIM
    assert sorted(source_order_per_canonical()) == list(range(PER_GENERATION_DIM))

    counts = Counter(state.sm for state in basis)
    assert counts == Counter(
        {
            "S": 1,
            "Q": 6,
            "u_c": 3,
            "d_c": 3,
            "L": 2,
            "e_c": 1,
            "nu_c": 1,
            "T": 3,
            "H": 2,
            "Tbar": 3,
            "Hbar": 2,
        }
    )


def test_generation_basis_has_expected_hypercharge_multiset():
    basis = canonical_generation_basis()
    hypercharges = Counter(state.hypercharge for state in basis)
    assert hypercharges == Counter(
        {
            Fraction(0, 1): 2,
            Fraction(1, 6): 6,
            Fraction(-2, 3): 3,
            Fraction(1, 3): 6,
            Fraction(-1, 2): 4,
            Fraction(1, 1): 1,
            Fraction(-1, 3): 3,
            Fraction(1, 2): 2,
        }
    )


def test_matter_basis_lifts_canonical_27_to_three_generations():
    basis = matter_basis()
    assert len(basis) == MATTER_DIM
    assert {state.generation for state in basis} == set(range(GENERATION_COUNT))

    for generation in range(GENERATION_COUNT):
        start = generation * PER_GENERATION_DIM
        block = basis[start : start + PER_GENERATION_DIM]
        assert [state.slot for state in block] == [state.slot for state in canonical_generation_basis()]
        assert [state.matter_index for state in block] == list(range(start, start + PER_GENERATION_DIM))


def test_higgs_contracted_mass_kernel_is_integer_symmetric_and_full_rank():
    mass = higgs_contracted_mass_matrix_27()
    assert mass.shape == (PER_GENERATION_DIM, PER_GENERATION_DIM)
    assert np.array_equal(mass, mass.T)
    assert np.array_equal(mass, np.rint(mass))
    assert int(np.trace(mass)) == 384
    assert np.linalg.matrix_rank(mass) == PER_GENERATION_DIM

    evals = np.linalg.eigvalsh(mass.astype(float))
    assert evals[0] > 1.7
    assert evals[-1] < 57.3


def test_ko_dimension_six_sign_pattern_holds_for_candidate():
    dirac = finite_dirac_162()
    grading = grading_162()
    real_structure = real_structure_162()
    identity = np.eye(TOTAL_DIM)

    assert dirac.shape == (TOTAL_DIM, TOTAL_DIM)
    assert np.array_equal(dirac, dirac.T)
    assert np.array_equal(grading @ grading, identity)
    assert np.array_equal(real_structure @ real_structure, identity)
    assert np.array_equal(grading @ dirac, -dirac @ grading)
    assert np.array_equal(real_structure @ dirac, dirac @ real_structure)
    assert np.array_equal(real_structure @ grading, -grading @ real_structure)


def test_weak_factor_operator_acts_only_on_doublets():
    alpha = 1 + 2j
    beta = -3 + 1j
    block = quaternion_matrix(alpha, beta)
    operator = weak_factor_operator_27(alpha, beta)
    touched = set()

    for indices in weak_doublet_blocks_27():
        touched.update(indices)
        assert np.allclose(operator[np.ix_(indices, indices)], block)

    for index in range(PER_GENERATION_DIM):
        if index not in touched:
            row = operator[index]
            col = operator[:, index]
            assert np.isclose(row[index], 1.0)
            assert np.isclose(col[index], 1.0)
            assert np.allclose(np.delete(row, index), 0.0)
            assert np.allclose(np.delete(col, index), 0.0)


def test_color_factor_operator_acts_on_triplets_with_correct_conjugation():
    candidate = build_w33_finite_spectral_triple()
    color_matrix = np.array(
        [
            [1 + 1j, 2 - 1j, 0.5],
            [0.25j, -2 + 0.5j, 3],
            [1.5, -0.75j, 4 - 2j],
        ],
        dtype=complex,
    )
    operator = color_factor_operator_27(color_matrix)

    q_block = candidate.q_color_block_27
    assert np.allclose(
        operator[np.ix_(q_block, q_block)],
        np.kron(color_matrix, np.eye(2)),
    )
    for indices in candidate.color_triplet_blocks_27:
        assert np.allclose(operator[np.ix_(indices, indices)], color_matrix)
    for indices in candidate.color_antitriplet_blocks_27:
        assert np.allclose(operator[np.ix_(indices, indices)], np.conjugate(color_matrix))


def test_hypercharge_commutes_with_sample_weak_and_color_actions():
    hypercharge = hypercharge_operator_27()
    weak = weak_factor_operator_27(2 - 1j, 0.5 + 3j)
    color = color_factor_operator_27(
        np.array(
            [
                [2, 1j, 0],
                [-1j, 3, 0.5],
                [1, -0.25, -2],
            ],
            dtype=complex,
        )
    )

    assert np.allclose(hypercharge @ weak, weak @ hypercharge)
    assert np.allclose(hypercharge @ color, color @ hypercharge)


def test_hypercharge_flips_sign_on_conjugate_sector():
    hypercharge = hypercharge_operator_162()
    matter_diag = np.diag(hypercharge)[:MATTER_DIM]
    antimatter_diag = np.diag(hypercharge)[MATTER_DIM:]
    assert np.allclose(antimatter_diag, -matter_diag)
