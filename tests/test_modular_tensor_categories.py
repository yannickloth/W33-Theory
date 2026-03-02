"""
Tests for Pillar 162 (CCLXII): Modular Tensor Categories
"""

import pytest
from THEORY_PART_CCLXII_MODULAR_TENSOR_CATEGORIES import (
    modular_tensor_category_foundations,
    modular_data,
    fusion_and_verlinde,
    reshetikhin_turaev,
    quantum_group_mtcs,
    fibonacci_anyons,
    drinfeld_center,
    rational_cft_connection,
    subfactor_mtcs,
    witt_group,
    anyon_condensation,
    connections_to_prior,
    mtc_e8,
    w33_chain,
    complete_chain,
)


# ---- 1. Foundations -------------------------------------------------------

class TestFoundations:
    def test_definition_components(self):
        f = modular_tensor_category_foundations()
        assert len(f['definition']['components']) == 5

    def test_braided_spherical(self):
        f = modular_tensor_category_foundations()
        assert 'braided' in f['definition']['short'].lower()
        assert 'non-degenerate' in f['definition']['short'].lower()

    def test_year(self):
        f = modular_tensor_category_foundations()
        assert f['year'] == 1989

    def test_physical_motivation(self):
        f = modular_tensor_category_foundations()
        assert 'anyon' in f['physical_motivation']['monoidal'].lower()

    def test_non_degeneracy(self):
        f = modular_tensor_category_foundations()
        assert 'transparent' in f['physical_motivation']['non_degenerate'].lower() or \
               'invisible' in f['physical_motivation']['non_degenerate'].lower()


# ---- 2. Modular Data -----------------------------------------------------

class TestModularData:
    def test_s_matrix_invertible(self):
        md = modular_data()
        assert 'invertible' in md['s_matrix']['bruguieres']

    def test_sl2z(self):
        md = modular_data()
        assert 'SL(2,Z)' in md['modular_group']['representation']

    def test_quantum_dimension(self):
        md = modular_data()
        assert 'S_{a0}/S_{00}' in md['s_matrix']['quantum_dimension']

    def test_rank_finiteness(self):
        md = modular_data()
        assert 'finitely many' in md['rank_finiteness']['statement'].lower()


# ---- 3. Verlinde ---------------------------------------------------------

class TestVerlinde:
    def test_verlinde_formula(self):
        fv = fusion_and_verlinde()
        assert 'S_{aσ}' in fv['verlinde_formula']['formula']

    def test_freed_hopkins_teleman(self):
        fv = fusion_and_verlinde()
        assert 'K-theory' in fv['verlinde_k_theory']['statement']

    def test_fusion_associative(self):
        fv = fusion_and_verlinde()
        assert any('associative' in p.lower() for p in fv['fusion_rules']['properties'])


# ---- 4. Reshetikhin-Turaev -----------------------------------------------

class TestRT:
    def test_authors(self):
        rt = reshetikhin_turaev()
        assert 'Reshetikhin' in rt['authors']
        assert 'Turaev' in rt['authors']

    def test_tqft_output(self):
        rt = reshetikhin_turaev()
        assert '(2+1)' in rt['construction']['output']

    def test_witten(self):
        rt = reshetikhin_turaev()
        assert 'Jones' in rt['witten_connection']['formula']

    def test_turaev_viro(self):
        rt = reshetikhin_turaev()
        assert 'Drinfeld center' in rt['turaev_viro']['relation']


# ---- 5. Quantum Groups ---------------------------------------------------

class TestQuantumGroups:
    def test_root_of_unity(self):
        qg = quantum_group_mtcs()
        assert 'root of unity' in qg['construction']['quantum_parameter']

    def test_su2_rank(self):
        qg = quantum_group_mtcs()
        assert qg['examples']['su2_k']['rank'] == 'k + 1'

    def test_ising_fusion(self):
        qg = quantum_group_mtcs()
        assert 'σ ⊗ σ = 1 ⊕ ψ' in qg['examples']['su2_2_ising']['fusion']

    def test_chern_simons(self):
        qg = quantum_group_mtcs()
        assert 'Witten' in qg['chern_simons']['physicist']


# ---- 6. Fibonacci Anyons -------------------------------------------------

class TestFibonacci:
    def test_fusion_rule(self):
        fi = fibonacci_anyons()
        assert 'τ ⊗ τ = 1 ⊕ τ' in fi['fibonacci_category']['fusion_rule']

    def test_golden_ratio(self):
        fi = fibonacci_anyons()
        assert 'golden ratio' in fi['fibonacci_category']['quantum_dimension']

    def test_kitaev(self):
        fi = fibonacci_anyons()
        assert 'Kitaev' in fi['topological_quantum_computing']['proposal']

    def test_universality(self):
        fi = fibonacci_anyons()
        assert 'universal' in fi['topological_quantum_computing']['universality'].lower()


# ---- 7. Drinfeld Center --------------------------------------------------

class TestDrinfeldCenter:
    def test_muger(self):
        dc = drinfeld_center()
        assert 'modular' in dc['drinfeld_center']['muger_theorem'].lower()

    def test_toric_code(self):
        dc = drinfeld_center()
        assert 'Z_2' in dc['kitaev_model']['toric_code']

    def test_dijkgraaf_witten(self):
        dc = drinfeld_center()
        assert 'Dijkgraaf-Witten' in dc['quantum_double']['dijkgraaf_witten']


# ---- 8. Rational CFT  ----------------------------------------------------

class TestRCFT:
    def test_moore_seiberg(self):
        rc = rational_cft_connection()
        assert 'Moore-Seiberg' in rc['moore_seiberg']['paper']

    def test_huang(self):
        rc = rational_cft_connection()
        assert 'Huang' in rc['voa_connection']['theorem']

    def test_frs(self):
        rc = rational_cft_connection()
        assert 'Frobenius' in rc['frs_construction']['theorem']


# ---- 9. Subfactors -------------------------------------------------------

class TestSubfactors:
    def test_jones(self):
        sf = subfactor_mtcs()
        assert 'Fields Medal' in sf['key_contributors']['jones']

    def test_haagerup(self):
        sf = subfactor_mtcs()
        assert 'exotic' in sf['examples']['haagerup']


# ---- 10. Witt Group & Classification -------------------------------------

class TestWittGroup:
    def test_deligne_product(self):
        wg = witt_group()
        assert 'Deligne' in wg['witt_group']['group_operation']

    def test_rowell_stong_wang(self):
        wg = witt_group()
        assert '2009' in wg['classification']['rowell_stong_wang']


# ---- 11. Anyon Condensation ----------------------------------------------

class TestAnyonCondensation:
    def test_condensation(self):
        ac = anyon_condensation()
        assert 'boson' in ac['condensation']['idea']

    def test_bulk_boundary(self):
        ac = anyon_condensation()
        assert 'Drinfeld center' in ac['bulk_boundary']['msr']


# ---- 12-15. Integration --------------------------------------------------

class TestIntegration:
    def test_e8_rank_1(self):
        e8 = mtc_e8()
        assert e8['e8_level_1']['rank'] == 1

    def test_w33_chain(self):
        wc = w33_chain()
        assert any('W(3,3)' in p for p in wc['path'])

    def test_complete_links(self):
        cc = complete_chain()
        assert len(cc['links']) == 6

    def test_miracle(self):
        cc = complete_chain()
        assert 'MODULAR S-MATRIX' in cc['miracle']['statement']

    def test_freedman(self):
        cc = complete_chain()
        assert 'Freedman' in cc['universal_quantum']['freedman_theorem']
