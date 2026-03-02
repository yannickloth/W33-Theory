"""
Tests for Pillar 163 — Geometric Quantization.
"""

import pytest
from THEORY_PART_CCLXIII_GEOMETRIC_QUANTIZATION import (
    geometric_quantization_foundations,
    prequantization,
    polarization,
    metaplectic_correction,
    coadjoint_orbits,
    quantization_commutes_with_reduction,
    bohr_sommerfeld,
    kahler_quantization,
    deformation_vs_geometric,
    spinc_quantization,
    connections_to_prior,
    e8_geometric_quantization,
    w33_chain,
    symplectic_bridge,
    complete_chain,
)


# === Foundations ===========================================================

class TestFoundations:
    def test_founders(self):
        f = geometric_quantization_foundations()
        assert 'Kostant' in f['founders']
        assert 'Souriau' in f['founders']

    def test_year(self):
        f = geometric_quantization_foundations()
        assert f['year'] == 1970

    def test_three_steps(self):
        f = geometric_quantization_foundations()
        assert len(f['three_steps']) == 3
        assert 'PREQUANTIZATION' in f['three_steps'][0]
        assert 'POLARIZATION' in f['three_steps'][1]
        assert 'METAPLECTIC' in f['three_steps'][2]

    def test_motivation(self):
        f = geometric_quantization_foundations()
        assert 'Poisson' in f['motivation']['quantum_side'] or 'Hilbert' in f['motivation']['quantum_side']
        assert 'symplectic' in f['motivation']['classical_side'].lower()


# === Prequantization =======================================================

class TestPrequantization:
    def test_integrality(self):
        pq = prequantization()
        assert 'integral' in pq['integrality_condition']['statement'].lower()
        assert 'H²' in pq['integrality_condition']['statement']

    def test_kostant_souriau_operator(self):
        pq = prequantization()
        assert 'Q(f)' in pq['kostant_souriau_operator']['formula']
        assert '∇' in pq['kostant_souriau_operator']['formula']

    def test_commutator_property(self):
        pq = prequantization()
        assert 'Poisson' in pq['kostant_souriau_operator']['significance']

    def test_examples(self):
        pq = prequantization()
        assert 'cotangent' in pq['examples']['cotangent_bundle'].lower()
        assert 'S²' in pq['examples']['sphere_S2']


# === Polarization ==========================================================

class TestPolarization:
    def test_definition(self):
        pol = polarization()
        assert 'Lagrangian' in pol['definition']['formal']
        assert 'integrable' in pol['definition']['integrable'].lower()

    def test_real_polarization(self):
        pol = polarization()
        assert 'Schrödinger' in pol['types']['real_polarization']['result']

    def test_kahler_polarization(self):
        pol = polarization()
        assert 'holomorphic' in pol['types']['kahler_polarization']['result'].lower()

    def test_quantum_hilbert_space(self):
        pol = polarization()
        assert '∇' in pol['quantum_hilbert_space']['definition']


# === Metaplectic Correction ================================================

class TestMetaplecticCorrection:
    def test_half_form(self):
        mc = metaplectic_correction()
        assert '½' in mc['harmonic_oscillator_corrected']['with_half_forms']

    def test_canonical_bundle(self):
        mc = metaplectic_correction()
        assert 'K_P' in mc['construction']['canonical_bundle']

    def test_bks_pairing(self):
        mc = metaplectic_correction()
        assert 'BKS' in mc['bks_pairing']['name'].upper()
        assert 'Blattner' in mc['bks_pairing']['name']

    def test_problem_statement(self):
        mc = metaplectic_correction()
        assert 'zero' in mc['problem']['without_correction'].lower()


# === Coadjoint Orbits ======================================================

class TestCoadjointOrbits:
    def test_kirillov(self):
        co = coadjoint_orbits()
        assert 'Kirillov' in co['founder']
        assert co['kirillov_orbit_method']['proven_for'] is not None

    def test_compact_case(self):
        co = coadjoint_orbits()
        assert 'SU(2)' in co['compact_case']['example_su2']
        assert 'spin' in co['compact_case']['example_su2'].lower()

    def test_nilpotent_bijection(self):
        co = coadjoint_orbits()
        assert 'bijection' in co['nilpotent_case']['bijection'].lower()

    def test_significance(self):
        co = coadjoint_orbits()
        assert 'symplectic' in co['significance'].lower()


# === Quantization Commutes with Reduction ==================================

class TestQR:
    def test_guillemin_sternberg(self):
        qr = quantization_commutes_with_reduction()
        assert 'Guillemin' in qr['conjectured_by']
        assert '1982' in qr['conjectured_by']

    def test_proven(self):
        qr = quantization_commutes_with_reduction()
        assert 'Meinrenken' in qr['proven_by']

    def test_statement(self):
        qr = quantization_commutes_with_reduction()
        assert 'commute' in qr['statement']['significance'].lower()

    def test_moment_map(self):
        qr = quantization_commutes_with_reduction()
        assert 'μ' in qr['symplectic_reduction']['marsden_weinstein']


# === Bohr-Sommerfeld =======================================================

class TestBohrSommerfeld:
    def test_classical_condition(self):
        bs = bohr_sommerfeld()
        assert 'n + ½' in bs['classical_condition']['corrected']

    def test_maslov(self):
        bs = bohr_sommerfeld()
        assert 'Maslov' in bs['classical_condition']['maslov_index']

    def test_geometric_form(self):
        bs = bohr_sommerfeld()
        assert 'holonomy' in bs['geometric_form']['condition'].lower()

    def test_sniatycki(self):
        bs = bohr_sommerfeld()
        assert 'niatycki' in bs['geometric_form']['sniatycki_theorem']


# === Kähler Quantization ===================================================

class TestKahlerQuantization:
    def test_holomorphic_sections(self):
        kq = kahler_quantization()
        assert 'holomorphic' in kq['quantum_hilbert_space']['definition'].lower()

    def test_berezin_toeplitz(self):
        kq = kahler_quantization()
        assert 'Berezin' in kq['berezin_toeplitz']['name']
        assert 'Toeplitz' in kq['berezin_toeplitz']['name']

    def test_borel_weil(self):
        kq = kahler_quantization()
        assert 'Borel-Weil' in kq['examples']['flag_manifold']

    def test_bargmann_fock(self):
        kq = kahler_quantization()
        assert 'Bargmann' in kq['examples']['complex_plane']


# === Deformation vs Geometric ==============================================

class TestDeformationVsGeometric:
    def test_kontsevich(self):
        dg = deformation_vs_geometric()
        assert 'Kontsevich' in dg['deformation_quantization']['kontsevich_theorem']

    def test_star_product(self):
        dg = deformation_vs_geometric()
        assert '★' in dg['deformation_quantization']['star_product']

    def test_fedosov(self):
        dg = deformation_vs_geometric()
        assert 'Fedosov' in dg['fedosov_quantization']['name']

    def test_bridge(self):
        dg = deformation_vs_geometric()
        assert 'Kähler' in dg['comparison']['bridge'] or 'Kahler' in dg['comparison']['bridge']


# === Spin^c Quantization ===================================================

class TestSpincQuantization:
    def test_dirac_operator(self):
        sc = spinc_quantization()
        assert 'Dirac' in sc['setup']['dirac_operator']

    def test_index(self):
        sc = spinc_quantization()
        assert 'index' in sc['setup']['quantization'].lower()

    def test_polarization_free(self):
        sc = spinc_quantization()
        assert 'Avoids' in sc['advantages']['polarization_free']


# === E8 ====================================================================

class TestE8:
    def test_e8_orbits(self):
        e8 = e8_geometric_quantization()
        assert '248' in e8['e8_coadjoint_orbits']['lie_algebra']

    def test_borel_weil_e8(self):
        e8 = e8_geometric_quantization()
        assert 'Borel-Weil' in e8['borel_weil_for_e8']['theorem']

    def test_flag_manifold(self):
        e8 = e8_geometric_quantization()
        assert '120' in e8['borel_weil_for_e8']['flag_manifold']


# === W33 Chain =============================================================

class TestW33Chain:
    def test_path(self):
        wc = w33_chain()
        assert any('W(3,3)' in p for p in wc['path'])
        assert any('Kirillov' in p for p in wc['path'])

    def test_deep_connection(self):
        wc = w33_chain()
        assert 'orbit method' in wc['deep_connection'].lower()


# === Complete Chain =========================================================

class TestCompleteChain:
    def test_links(self):
        cc = complete_chain()
        assert len(cc['links']) == 6

    def test_miracle(self):
        cc = complete_chain()
        assert 'MIRACLE' in cc['miracle']['statement']

    def test_integrality(self):
        cc = complete_chain()
        assert 'integrality' in cc['miracle']['depth']

    def test_grand_unification(self):
        cc = complete_chain()
        assert 'Kirillov' in cc['grand_unification']['kirillov_philosophy']
