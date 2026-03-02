"""
Tests for Pillar 134 - Quantum Error Correction from Classical Codes
"""
import pytest

from THEORY_PART_CCXXXIV_QUANTUM_ERROR_CORRECTION import (
    classical_code_parameters, quantum_code_parameters,
    css_construction, self_dual_to_css,
    steane_from_hamming, five_qubit_code, quantum_golay,
    quantum_hamming_bound, quantum_singleton_bound,
    pauli_group_order, stabilizer_group_size, num_generators,
    heisenberg_connection,
    fano_plane, fano_to_code_chain,
    golay_quantum_bridge, code_distance_comparison,
    twenty_four_appearances_qec,
    golay_weight_enumerator, quantum_weight_enumerator_connection,
    complete_chain, verify_all_bounds,
)


# -- Classical codes ------------------------------------------------

class TestClassicalCodes:
    def test_golay_24_params(self):
        cc = classical_code_parameters()
        g = cc['golay_24']
        assert (g['n'], g['k'], g['d']) == (24, 12, 8)

    def test_hamming_7_params(self):
        cc = classical_code_parameters()
        h = cc['hamming_7']
        assert (h['n'], h['k'], h['d']) == (7, 4, 3)

    def test_hexacode_params(self):
        cc = classical_code_parameters()
        h = cc['hexacode']
        assert (h['n'], h['k'], h['d']) == (6, 3, 4)

    def test_six_classical_codes(self):
        assert len(classical_code_parameters()) == 6


# -- Quantum codes --------------------------------------------------

class TestQuantumCodes:
    def test_steane_params(self):
        s = steane_from_hamming()
        assert (s['n'], s['k'], s['d']) == (7, 1, 3)

    def test_steane_stabilizer_count(self):
        s = steane_from_hamming()
        assert s['num_stabilizers'] == 6

    def test_steane_from_fano(self):
        assert steane_from_hamming()['from_fano'] is True

    def test_steane_corrects_1(self):
        assert steane_from_hamming()['corrects'] == 1

    def test_five_qubit_perfect(self):
        assert five_qubit_code()['is_perfect'] is True

    def test_five_qubit_hamming_saturated(self):
        assert five_qubit_code()['hamming_bound'] is True

    def test_five_qubit_generators(self):
        f = five_qubit_code()
        assert f['num_generators'] == 4  # n - k = 5 - 1

    def test_quantum_golay_params(self):
        qg = quantum_golay()
        assert (qg['n'], qg['k'], qg['d']) == (23, 1, 7)

    def test_quantum_golay_corrects_3(self):
        assert quantum_golay()['corrects'] == 3

    def test_quantum_golay_css(self):
        assert quantum_golay()['css_type'] is True

    def test_seven_quantum_codes(self):
        assert len(quantum_code_parameters()) == 7


# -- CSS construction -----------------------------------------------

class TestCSSConstruction:
    def test_self_dual_golay_css(self):
        golay = {'n': 24, 'k': 12, 'd': 8}
        result = self_dual_to_css(golay)
        assert result == {'n': 24, 'k': 0, 'd': 8, 'type': 'stabilizer_state'}

    def test_css_steane(self):
        c1 = {'n': 7, 'k': 4, 'd': 3}
        c2 = {'n': 7, 'k': 3, 'd': 4}  # dual Hamming
        result = css_construction(c1, c2)
        assert result['k'] == 1
        assert result['n'] == 7


# -- Bounds ---------------------------------------------------------

class TestBounds:
    def test_five_qubit_saturates_hamming(self):
        hb = quantum_hamming_bound(5, 1, 3)
        assert hb['saturated'] is True

    def test_steane_hamming_valid(self):
        hb = quantum_hamming_bound(7, 1, 3)
        assert hb['valid'] is True

    def test_golay_singleton(self):
        sb = quantum_singleton_bound(23, 1, 7)
        assert sb['valid'] is True

    def test_all_bounds_valid(self):
        bounds = verify_all_bounds()
        assert all(b['hamming_valid'] for b in bounds)
        assert all(b['singleton_valid'] for b in bounds)


# -- Stabilizer formalism ------------------------------------------

class TestStabilizer:
    def test_pauli_1_qubit(self):
        assert pauli_group_order(1) == 16  # 4^2

    def test_pauli_n_qubits(self):
        assert pauli_group_order(5) == 4**6

    def test_stabilizer_size(self):
        # [[7,1,3]]: stabilizer has 2^6 = 64 elements
        assert stabilizer_group_size(7, 1) == 64

    def test_num_generators(self):
        assert num_generators(7, 1) == 6
        assert num_generators(5, 1) == 4
        assert num_generators(23, 1) == 22


# -- Heisenberg connection -----------------------------------------

class TestHeisenberg:
    def test_both_extraspecial(self):
        h = heisenberg_connection()
        assert h['both_extraspecial'] is True

    def test_pauli_field_f2(self):
        h = heisenberg_connection()
        assert h['pauli_field'] == 'F_2'

    def test_w33_field_f3(self):
        h = heisenberg_connection()
        assert h['w33_field'] == 'F_3'


# -- Fano plane -----------------------------------------------------

class TestFano:
    def test_fano_7_points(self):
        assert fano_plane()['points'] == 7

    def test_fano_7_lines(self):
        assert fano_plane()['lines'] == 7

    def test_fano_3_per_line(self):
        assert fano_plane()['points_per_line'] == 3

    def test_fano_automorphisms(self):
        assert fano_plane()['automorphisms'] == 168

    def test_fano_chain_8_links(self):
        assert len(fano_to_code_chain()) == 8


# -- Golay quantum bridge ------------------------------------------

class TestGolayBridge:
    def test_golay_self_dual(self):
        assert golay_quantum_bridge()['golay_24_self_dual'] is True

    def test_css_24_0_8(self):
        css = golay_quantum_bridge()['css_24']
        assert (css['n'], css['k'], css['d']) == (24, 0, 8)

    def test_golay_weight_total(self):
        gwe = golay_weight_enumerator()
        assert gwe['total_codewords'] == 4096

    def test_golay_759_octads(self):
        assert golay_weight_enumerator()['weights'][8] == 759

    def test_golay_doubly_even(self):
        assert golay_weight_enumerator()['doubly_even'] is True


# -- Number 24 and complete chain -----------------------------------

class TestChain:
    def test_24_count(self):
        assert twenty_four_appearances_qec()['count'] == 8

    def test_complete_chain_length(self):
        assert len(complete_chain()) == 6

    def test_code_comparison_6_codes(self):
        assert len(code_distance_comparison()) == 6

    def test_golay_best_correction(self):
        codes = code_distance_comparison()
        golay_entry = [c for c in codes if c['n'] == 23][0]
        assert golay_entry['t'] == 3

    def test_quantum_weight_connection(self):
        qwc = quantum_weight_enumerator_connection()
        assert qwc['classical_d'] == 8
        assert qwc['corrects'] == 3
