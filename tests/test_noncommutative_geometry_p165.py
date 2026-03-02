"""
Tests for Pillar 165 — Noncommutative Geometry (Advanced NCG).
"""

import pytest
from THEORY_PART_CCLXV_NONCOMMUTATIVE_GEOMETRY import (
    ncg_foundations,
    spectral_triple,
    spectral_action,
    ncg_standard_model,
    cyclic_homology,
    noncommutative_torus,
    connections_to_prior,
    von_neumann_algebras,
    index_theory_ncg,
    ncg_physics,
    e8_ncg,
    w33_chain,
    moyal_product,
    bost_connes,
    complete_chain,
)


class TestFoundationsP165:
    def test_connes(self):
        f = ncg_foundations()
        assert 'Connes' in f['founder']
        assert f['year'] == 1985

    def test_gelfand(self):
        f = ncg_foundations()
        assert 'Gelfand' in f['philosophy']['gelfand_naimark']

    def test_layers(self):
        f = ncg_foundations()
        assert 'C*-algebra' in f['layers']['topology']
        assert 'von Neumann' in f['layers']['measure_theory']


class TestSpectralTripleP165:
    def test_definition(self):
        st = spectral_triple()
        assert '(A, H, D)' in st['definition']['data']
        assert 'compact resolvent' in st['definition']['D']

    def test_metric(self):
        st = spectral_triple()
        assert 'd(φ,ψ)' in st['connes_metric']['formula']

    def test_reconstruction(self):
        st = spectral_triple()
        assert 'Connes' in st['reconstruction']['theorem']
        assert len(st['reconstruction']['axioms']) == 5


class TestSpectralActionP165:
    def test_authors(self):
        sa = spectral_action()
        assert 'Chamseddine' in sa['authors']
        assert 'Connes' in sa['authors']

    def test_action(self):
        sa = spectral_action()
        assert 'Tr(f(D/Λ))' in sa['action']['bosonic']

    def test_expansion(self):
        sa = spectral_action()
        assert len(sa['expansion']['yields']) == 5
        assert 'Einstein' in sa['expansion']['yields'][1]


class TestNCGStandardModelP165:
    def test_algebra(self):
        sm = ncg_standard_model()
        assert 'C ⊕ H ⊕ M₃(C)' in sm['geometry']['algebra']

    def test_output(self):
        sm = ncg_standard_model()
        assert 'SU(3)' in sm['output']['gauge_group']
        assert 'Higgs' in sm['output']['higgs']

    def test_evolution(self):
        sm = ncg_standard_model()
        assert 'Pati-Salam' in sm['evolution']['pati_salam_2013']


class TestCyclicHomologyP165:
    def test_discoverers(self):
        ch = cyclic_homology()
        assert 'Connes' in ch['cyclic_homology']['discoverers']

    def test_chern(self):
        ch = cyclic_homology()
        assert 'Chern' in ch['connes_chern']['name']

    def test_k_theory(self):
        ch = cyclic_homology()
        assert 'Bott' in ch['k_theory']['bott']


class TestNCTorusP165:
    def test_definition(self):
        nt = noncommutative_torus()
        assert 'e^{2πiθ}' in nt['definition']['generators']

    def test_morita(self):
        nt = noncommutative_torus()
        assert 'SL(2,Z)' in nt['definition']['morita']

    def test_physics(self):
        nt = noncommutative_torus()
        assert 'D-brane' in nt['physics']['string_theory']


class TestVonNeumannP165:
    def test_types(self):
        vn = von_neumann_algebras()
        assert 'B(H)' in vn['classification']['type_I']

    def test_modular(self):
        vn = von_neumann_algebras()
        assert 'modular' in vn['ncg_role']['tomita_takesaki'].lower()

    def test_kms(self):
        vn = von_neumann_algebras()
        assert 'KMS' in vn['physics']['thermodynamics']


class TestIndexTheoryP165:
    def test_classical(self):
        it = index_theory_ncg()
        assert 'Atiyah' in it['classical']['atiyah_singer']

    def test_novikov(self):
        it = index_theory_ncg()
        assert 'Novikov' in it['applications']['novikov']

    def test_local_index(self):
        it = index_theory_ncg()
        assert 'Connes-Moscovici' in it['ncg_extension']['local_index']


class TestNCGPhysicsP165:
    def test_gravity(self):
        np = ncg_physics()
        assert 'Einstein-Hilbert' in np['gravity']['einstein_hilbert']

    def test_dark_matter(self):
        np = ncg_physics()
        assert 'σ-field' in np['dark_matter']['sigma_field']


class TestE8NCGP165:
    def test_248(self):
        e8 = e8_ncg()
        assert '248' in e8['e8_spectral']['dimension']

    def test_heterotic(self):
        e8 = e8_ncg()
        assert 'heterotic' in e8['heterotic']['heterotic_string'].lower()


class TestW33P165:
    def test_path(self):
        wc = w33_chain()
        assert any('W(3,3)' in p for p in wc['path'])

    def test_deep(self):
        wc = w33_chain()
        assert 'Standard Model' in wc['deep_connection']


class TestMoyalP165:
    def test_formula(self):
        mp = moyal_product()
        assert '★' in mp['moyal']['formula']

    def test_seiberg_witten(self):
        mp = moyal_product()
        assert 'Seiberg-Witten' in mp['noncommutative_field_theory']['seiberg_witten']


class TestBostConnesP165:
    def test_authors(self):
        bc = bost_connes()
        assert 'Bost' in bc['authors']

    def test_zeta(self):
        bc = bost_connes()
        assert 'ζ(β)' in bc['system']['partition_function']

    def test_galois(self):
        bc = bost_connes()
        assert 'Galois' in bc['number_theory']['class_field']


class TestCompleteP165:
    def test_links(self):
        cc = complete_chain()
        assert len(cc['links']) == 6

    def test_miracle(self):
        cc = complete_chain()
        assert 'MIRACLE' in cc['miracle']['statement']

    def test_dirac(self):
        cc = complete_chain()
        assert 'Dirac' in cc['miracle']['depth']
