"""
Tests for Pillar 204: Algebraic K-Theory and W(3,3)
Module: THEORY_PART_CCCIV_ALGEBRAIC_K_THEORY
"""
import importlib
import pytest

@pytest.fixture(scope="module")
def mod():
    return importlib.import_module("pillars.THEORY_PART_CCCIV_ALGEBRAIC_K_THEORY")


class TestKTheoryBasics:
    def test_k0_grothendieck(self, mod):
        r = mod.k_theory_basics()
        assert "Grothendieck" in r['k0']['grothendieck']

    def test_k0_swan(self, mod):
        r = mod.k_theory_basics()
        assert "Swan" in r['k0']['swan']

    def test_k1_whitehead(self, mod):
        r = mod.k_theory_basics()
        assert "Whitehead" in r['k1']['whitehead']

    def test_k1_determinant(self, mod):
        r = mod.k_theory_basics()
        assert isinstance(r['k1']['determinant'], str)

    def test_k2_milnor(self, mod):
        r = mod.k_theory_basics()
        assert "K2" in r['k2']['milnor'] or "Milnor" in r['k2']['milnor']

    def test_k2_matsumoto(self, mod):
        r = mod.k_theory_basics()
        assert "Matsumoto" in r['k2']['matsumoto']

    def test_higher_k_quillen(self, mod):
        r = mod.k_theory_basics()
        assert "Quillen" in r['higher_k']['quillen']

    def test_higher_k_plus_construction(self, mod):
        r = mod.k_theory_basics()
        assert isinstance(r['higher_k']['plus_construction'], str)

    def test_higher_k_localization(self, mod):
        r = mod.k_theory_basics()
        assert isinstance(r['higher_k']['localization'], str)

    def test_all_keys_present(self, mod):
        r = mod.k_theory_basics()
        for k in ['k0', 'k1', 'k2', 'higher_k']:
            assert k in r


class TestMilnorKTheory:
    def test_milnor_k_definition(self, mod):
        r = mod.milnor_k_theory()
        assert "Milnor" in r['milnor_k']['definition']

    def test_milnor_k_symbols(self, mod):
        r = mod.milnor_k_theory()
        assert isinstance(r['milnor_k']['symbols'], str)

    def test_norm_residue_voevodsky(self, mod):
        r = mod.milnor_k_theory()
        assert "Voevodsky" in r['norm_residue']['voevodsky_proof']

    def test_bloch_kato_rost(self, mod):
        r = mod.milnor_k_theory()
        assert "Rost" in r['bloch_kato']['rost_voevodsky'] or "Voevodsky" in r['bloch_kato']['rost_voevodsky']

    def test_applications_galois(self, mod):
        r = mod.milnor_k_theory()
        assert isinstance(r['applications_milnor']['galois'], str)


class TestAlgebraicKComputations:
    def test_finite_fields_quillen(self, mod):
        r = mod.algebraic_k_computations()
        assert "Quillen" in r['finite_fields']['quillen']

    def test_integers_k0(self, mod):
        r = mod.algebraic_k_computations()
        assert "K_0" in r['integers']['k0_z'] or "K0" in r['integers']['k0_z']

    def test_integers_k3(self, mod):
        r = mod.algebraic_k_computations()
        assert "48" in r['integers']['k3_z']

    def test_motivic_cohomology(self, mod):
        r = mod.algebraic_k_computations()
        assert isinstance(r['motivic']['motivic_cohomology'], str)

    def test_recent_tc(self, mod):
        r = mod.algebraic_k_computations()
        assert isinstance(r['recent']['tc'], str)


class TestTopologicalKTheory:
    def test_bott_periodicity_complex(self, mod):
        r = mod.topological_k_theory()
        assert "period" in r['bott_periodicity']['complex'].lower() or "2" in r['bott_periodicity']['complex']

    def test_bott_periodicity_real(self, mod):
        r = mod.topological_k_theory()
        assert "8" in r['bott_periodicity']['real']

    def test_tmf_definition(self, mod):
        r = mod.topological_k_theory()
        assert "tmf" in r['tmf']['definition'] or "modular" in r['tmf']['definition'].lower()

    def test_chromatic_filtration(self, mod):
        r = mod.topological_k_theory()
        assert isinstance(r['chromatic']['chromatic_filtration'], str)

    def test_atiyah_hirzebruch(self, mod):
        r = mod.topological_k_theory()
        assert isinstance(r['atiyah_hirzebruch']['definition'], str)


class TestWaldhausenKTheory:
    def test_s_construction(self, mod):
        r = mod.waldhausen_k_theory()
        assert "Waldhausen" in r['s_construction']['waldhausen']

    def test_a_theory(self, mod):
        r = mod.waldhausen_k_theory()
        assert isinstance(r['a_theory']['definition'], str)

    def test_trace_thh(self, mod):
        r = mod.waldhausen_k_theory()
        assert "THH" in r['trace_methods']['thh']

    def test_trace_tc(self, mod):
        r = mod.waldhausen_k_theory()
        assert "TC" in r['trace_methods']['tc'] or "topological cyclic" in r['trace_methods']['tc'].lower()

    def test_modern_nikolaus_scholze(self, mod):
        r = mod.waldhausen_k_theory()
        assert "Nikolaus" in r['modern']['nikolaus_scholze'] or "Scholze" in r['modern']['nikolaus_scholze']


class TestW33KTheorySynthesis:
    def test_sp6f2_order(self, mod):
        r = mod.w33_k_theory_synthesis()
        assert "1451520" in r['sp6f2_counting']['order']

    def test_k_f2_quillen(self, mod):
        r = mod.w33_k_theory_synthesis()
        assert "Quillen" in r['k_f2']['quillen_computation'] or "K" in r['k_f2']['quillen_computation']

    def test_k0_w33_forty(self, mod):
        r = mod.w33_k_theory_synthesis()
        assert "40" in r['k0_w33']['forty_points']

    def test_bott_w33(self, mod):
        r = mod.w33_k_theory_synthesis()
        assert isinstance(r['bott_w33']['bott_periodicity'], str)

    def test_k_f2_k3(self, mod):
        r = mod.w33_k_theory_synthesis()
        assert "7" in r['k_f2']['k3']
