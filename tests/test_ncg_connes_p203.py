"""Tests for Pillar 203 - Noncommutative Geometry (Connes)."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P203():
    return importlib.import_module("THEORY_PART_CCCIII_NONCOMMUTATIVE_GEOMETRY_CONNES")

class TestSpectralTriples:
    def test_dirac(self, P203):
        r = P203.spectral_triples()
        assert 'D' in r['definition']['dirac'] or 'operator' in r['definition']['dirac']
    def test_connes_2008(self, P203):
        r = P203.spectral_triples()
        assert 'Connes' in r['reconstruction']['connes_2008']
    def test_ko_dim(self, P203):
        r = P203.spectral_triples()
        assert 'KO' in r['real_structure']['ko_dimension']

class TestNCGStandardModel:
    def test_chamseddine(self, P203):
        r = P203.ncg_standard_model()
        assert 'Chamseddine' in r['spectral_action']['chamseddine_connes']
    def test_higgs(self, P203):
        r = P203.ncg_standard_model()
        assert 'Higgs' in r['higgs_mechanism']['inner_fluctuations'] or 'inner' in r['higgs_mechanism']['inner_fluctuations'].lower()
    def test_neutrino(self, P203):
        r = P203.ncg_standard_model()
        assert 'neutrino' in r['higgs_mechanism']['neutrino'].lower()

class TestCyclicHomology:
    def test_cyclic(self, P203):
        r = P203.cyclic_homology()
        assert 'cyclic' in r['cyclic_cohomology']['definition'].lower() or 'Cyclic' in r['cyclic_cohomology']['definition']
    def test_connes_moscovici(self, P203):
        r = P203.cyclic_homology()
        assert 'Connes' in r['local_index']['connes_moscovici']
    def test_chern(self, P203):
        r = P203.cyclic_homology()
        assert 'Chern' in r['chern_character']['k_theory'] or 'chern' in r['chern_character']['k_theory'].lower()

class TestQuantumGroupsNCG:
    def test_moyal(self, P203):
        r = P203.quantum_groups_ncg()
        assert 'Moyal' in r['nc_torus']['moyal']
    def test_woronowicz(self, P203):
        r = P203.quantum_groups_ncg()
        assert 'Woronowicz' in r['compact_quantum']['woronowicz']
    def test_podles(self, P203):
        r = P203.quantum_groups_ncg()
        assert 'Podle' in r['compact_quantum']['podles_sphere']

class TestIndexTheory:
    def test_kasparov(self, P203):
        r = P203.index_theory_ncg()
        assert 'Kasparov' in r['kk_theory']['kasparov']
    def test_poincare(self, P203):
        r = P203.index_theory_ncg()
        assert 'Poincar' in r['kk_theory']['poincare_duality']

class TestW33NCG:
    def test_sp6f2_order(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '1451520' in r['sp6f2_spectral']['order']
    def test_dirac_w33(self, P203):
        r = P203.w33_ncg_synthesis()
        assert 'Dirac' in r['w33_spectral_triple']['dirac'] or 'adjacency' in r['w33_spectral_triple']['dirac'].lower()
    def test_three_families(self, P203):
        r = P203.w33_ncg_synthesis()
        assert 'three' in r['physics_w33']['three_families'].lower()
    def test_finite_candidate(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '162' in r['w33_finite_candidate']['hilbert']
        assert 'Higgs-contracted' in r['w33_finite_candidate']['dirac']
    def test_fermionic_candidate(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '96' in r['w33_fermionic_candidate']['hilbert']
        assert 'H_2' in r['w33_fermionic_candidate']['clean_higgs']
        assert 'Hbar_2' in r['w33_fermionic_candidate']['clean_higgs']
    def test_almost_commutative_candidate(self, P203):
        r = P203.w33_ncg_synthesis()
        assert 'A_F = C (+) H (+) M_3(C)' in r['w33_almost_commutative_candidate']['algebra']
        assert 'leptoquark' in r['w33_almost_commutative_candidate']['residual_source']
    def test_induced_quark_candidate(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '(3, -3, -2)' in r['w33_induced_quark_candidate']['background']
        assert 'Q-u_c' in r['w33_induced_quark_candidate']['channels']
        assert 'Q-d_c' in r['w33_induced_quark_candidate']['channels']
        assert 'quark = 32' in r['w33_induced_quark_candidate']['support']
    def test_quark_firewall_obstruction(self, P203):
        r = P203.w33_ncg_synthesis()
        assert 'Heisenberg fibers' in r['w33_quark_firewall_obstruction']['firewall']
        assert 'T/Tbar' in r['w33_quark_firewall_obstruction']['mediation']
        assert 'nullity 0' in r['w33_quark_firewall_obstruction']['screen']
    def test_balanced_triplet_family(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '1 : -n : -n : n : n' in r['w33_balanced_triplet_family']['family']
        assert 'improves from' in r['w33_balanced_triplet_family']['improvement']
        assert 'nullity remains zero' in r['w33_balanced_triplet_family']['status']
    def test_l4_quark_self_energy(self, P203):
        r = P203.w33_ncg_synthesis()
        assert 'rank 27' in r['w33_l4_quark_self_energy']['cubic_no_go']
        assert 'nullity 0' in r['w33_l4_quark_self_energy']['cubic_no_go']
        assert '4-dimensional quark-only image' in r['w33_l4_quark_self_energy']['subspace']
        assert 'higher-tower quark self-energy sector' in r['w33_l4_quark_self_energy']['status']
    def test_l4_dirac_bridge(self, P203):
        r = P203.w33_ncg_synthesis()
        assert "('ud_23', 'ud_13', 'q23_ud23', 'q13_ud13')" in r['w33_l4_dirac_bridge']['basis']
        assert 'from 2.034426 to 1.691947' in r['w33_l4_dirac_bridge']['fit']
        assert 'rank 2 to rank 3' in r['w33_l4_dirac_bridge']['rank_lift']
        assert 'does not close the residual' in r['w33_l4_dirac_bridge']['status']
    def test_l4_bridge_obstruction(self, P203):
        r = P203.w33_ncg_synthesis()
        assert "12-mode" in r['w33_l4_bridge_obstruction']['collapse']
        assert "('ud_23', 'ud_13')" in r['w33_l4_bridge_obstruction']['collapse']
        assert 'rank 6' in r['w33_l4_bridge_obstruction']['rank']
        assert 'rank 7' in r['w33_l4_bridge_obstruction']['rank']
        assert '1.691947' in r['w33_l4_bridge_obstruction']['no_go']
        assert 'beyond-l4 tower data' in r['w33_l4_bridge_obstruction']['status']
    def test_ce2_quark_bridge(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '144' in r['w33_ce2_quark_bridge']['source_algebra']
        assert 'simple-family-only count = 90' in r['w33_ce2_quark_bridge']['source_algebra']
        assert '36 left Q modes' in r['w33_ce2_quark_bridge']['projected_modes']
        assert '9 right u_c modes' in r['w33_ce2_quark_bridge']['projected_modes']
        assert '9 right d_c modes' in r['w33_ce2_quark_bridge']['projected_modes']
        assert 'rank 28' in r['w33_ce2_quark_bridge']['closure']
        assert '((10, 10), (6, 6), (4, 4))' in r['w33_ce2_quark_bridge']['closure']
        assert 'rank 36' in r['w33_ce2_quark_bridge']['no_go']
        assert 'nullity 0' in r['w33_ce2_quark_bridge']['no_go']
        assert 'only trivially' in r['w33_ce2_quark_bridge']['status']
    def test_l6_chiral_bridge(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '6 A2 roots plus 8 Cartan directions' in r['w33_l6_chiral_bridge']['modes']
        assert 'response rank 9' in r['w33_l6_chiral_bridge']['modes']
        assert 'augmented rank 10' in r['w33_l6_chiral_bridge']['modes']
        assert '3.523729' in r['w33_l6_chiral_bridge']['fit']
        assert '0.826695' in r['w33_l6_chiral_bridge']['fit']
        assert 'all A2 coefficients vanish' in r['w33_l6_chiral_bridge']['active_slice']
        assert 'rank 6 to rank 9' in r['w33_l6_chiral_bridge']['rank_lift']
        assert 'linearized l6 level' in r['w33_l6_chiral_bridge']['status']

class TestSelfChecks:
    def test_all_pass(self, P203):
        assert P203.run_self_checks() is True
