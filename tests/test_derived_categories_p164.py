"""
Tests for Pillar 164 — Derived Categories (Advanced).
"""

import pytest
from THEORY_PART_CCLXIV_DERIVED_CATEGORIES import (
    derived_category_foundations,
    triangulated_structure,
    derived_functors,
    derived_algebraic_geometry,
    fourier_mukai,
    homological_mirror_symmetry,
    dbranes_physics,
    t_structures,
    dg_enhancements,
    connections_to_prior,
    e8_derived,
    w33_chain,
    stability_e8,
    derived_algebraic_geometry_advanced,
    complete_chain,
)


# === Foundations ===========================================================

class TestFoundationsP164:
    def test_founders(self):
        f = derived_category_foundations()
        assert 'Grothendieck' in f['founders']
        assert 'Verdier' in f['founders']

    def test_construction(self):
        f = derived_category_foundations()
        assert 'quasi-iso' in f['definition']['construction']

    def test_variants(self):
        f = derived_category_foundations()
        assert 'D⁺' in f['variants']['D_plus']
        assert 'D^b' in f['variants']['D_b']

    def test_year(self):
        f = derived_category_foundations()
        assert f['year'] == 1960


# === Triangulated Structure ================================================

class TestTriangulatedP164:
    def test_shift(self):
        ts = triangulated_structure()
        assert 'X[n]' in ts['shift_functor']['definition']

    def test_distinguished_triangles(self):
        ts = triangulated_structure()
        assert 'Cone' in ts['distinguished_triangles']['form']
        assert len(ts['distinguished_triangles']['axioms']) == 4

    def test_ext_formula(self):
        ts = triangulated_structure()
        assert 'Ext' in ts['ext_groups']['formula']
        assert 'Y[j]' in ts['ext_groups']['formula']

    def test_ses_to_triangle(self):
        ts = triangulated_structure()
        assert 'exact' in ts['distinguished_triangles']['from_ses'].lower()


# === Derived Functors ======================================================

class TestDerivedFunctorsP164:
    def test_total_derived(self):
        df = derived_functors()
        assert 'RF' in df['total_derived']['right_derived']
        assert 'LF' in df['total_derived']['left_derived']

    def test_key_formula(self):
        df = derived_functors()
        assert 'R(G' in df['total_derived']['key_formula']

    def test_examples(self):
        df = derived_functors()
        assert 'RHom' in df['examples']['RHom']

    def test_adjunctions(self):
        df = derived_functors()
        assert 'Serre' in df['adjunctions']['serre_duality']


# === Algebraic Geometry ====================================================

class TestAlgGeomP164:
    def test_bondal_orlov(self):
        ag = derived_algebraic_geometry()
        assert ag['bondal_orlov']['year'] == 2001

    def test_beilinson(self):
        ag = derived_algebraic_geometry()
        assert 'Beilinson' in ag['exceptional_collections']['example_Pn']

    def test_serre_functor(self):
        ag = derived_algebraic_geometry()
        assert 'ω' in ag['serre_functor']['formula']


# === Fourier-Mukai =========================================================

class TestFourierMukaiP164:
    def test_founder(self):
        fm = fourier_mukai()
        assert 'Mukai' in fm['founder']

    def test_orlov(self):
        fm = fourier_mukai()
        assert fm['orlov_representability']['year'] == 1997

    def test_kernel(self):
        fm = fourier_mukai()
        assert 'P ∈' in fm['definition']['kernel']

    def test_partners(self):
        fm = fourier_mukai()
        assert 'K3' in fm['fourier_mukai_partners']['k3_surfaces']


# === HMS ===================================================================

class TestHMSP164:
    def test_kontsevich(self):
        hms = homological_mirror_symmetry()
        assert 'Kontsevich' in hms['conjectured_by']

    def test_sides(self):
        hms = homological_mirror_symmetry()
        assert 'Fukaya' in hms['statement']['a_side']
        assert 'coherent' in hms['statement']['b_side'].lower()

    def test_proven_cases(self):
        hms = homological_mirror_symmetry()
        assert 'Polishchuk' in hms['proven_cases']['elliptic_curves']

    def test_fields_medal(self):
        hms = homological_mirror_symmetry()
        assert 'Fields' in hms['significance']['fields_medal']


# === D-branes ==============================================================

class TestDBranesP164:
    def test_douglas(self):
        db = dbranes_physics()
        assert 'Douglas' in db['dbranes']['douglas']

    def test_bridgeland(self):
        db = dbranes_physics()
        assert 'Bridgeland' in db['stability']['bridgeland']

    def test_bps(self):
        db = dbranes_physics()
        assert 'BPS' in db['stability']['physics_connection']


# === t-Structures ==========================================================

class TestTStructuresP164:
    def test_introduced(self):
        ts = t_structures()
        assert 'Beilinson' in ts['introduced_by']

    def test_heart(self):
        ts = t_structures()
        assert 'abelian' in ts['definition']['heart'].lower()

    def test_perverse(self):
        ts = t_structures()
        assert 'perverse' in ts['examples']['perverse'].lower()

    def test_decomposition(self):
        ts = t_structures()
        assert 'BBD' in ts['perverse_sheaves']['bbd_decomposition']


# === DG Enhancements ======================================================

class TestDGEnhancementsP164:
    def test_keller(self):
        dge = dg_enhancements()
        assert 'Keller' in dge['dg_categories']['keller']

    def test_fukaya(self):
        dge = dg_enhancements()
        assert 'Fukaya' in dge['a_infinity']['fukaya']

    def test_morita(self):
        dge = dg_enhancements()
        assert 'Morita' in dge['derived_morita']['equivalence']


# === E8 ====================================================================

class TestE8P164:
    def test_248(self):
        e8 = e8_derived()
        assert '248' in e8['e8_representations']['dimension']

    def test_mckay(self):
        e8 = e8_derived()
        assert 'McKay' in e8['mckay_e8']['mckay_correspondence']

    def test_bridgeland_king_reid(self):
        e8 = e8_derived()
        assert 'Bridgeland' in e8['mckay_e8']['derived_equivalence']


# === W33 ===================================================================

class TestW33P164:
    def test_path(self):
        wc = w33_chain()
        assert any('W(3,3)' in p for p in wc['path'])

    def test_fourier_mukai(self):
        wc = w33_chain()
        assert any('Fourier-Mukai' in p for p in wc['path'])

    def test_del_pezzo(self):
        wc = w33_chain()
        assert 'del Pezzo' in wc['deep_connection']


# === Complete Chain ========================================================

class TestCompleteChainP164:
    def test_links(self):
        cc = complete_chain()
        assert len(cc['links']) == 6

    def test_miracle(self):
        cc = complete_chain()
        assert 'MIRACLE' in cc['miracle']['statement']

    def test_verdier(self):
        cc = complete_chain()
        assert 'Verdier' in cc['miracle']['depth']

    def test_grand_synthesis(self):
        cc = complete_chain()
        assert 'Fukaya' in cc['grand_synthesis']['symplectic_topology']
