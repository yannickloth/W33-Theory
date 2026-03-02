"""Tests for Pillar 187 - Arithmetic Dynamics & Dynamical Systems."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P187():
    return importlib.import_module("THEORY_PART_CCLXXXVII_ARITHMETIC_DYNAMICS")

# ── rational_dynamics ──────────────────────────────────────
class TestRationalDynamics:
    def test_vertices_40(self, P187):
        r = P187.rational_dynamics()
        assert r['w33_dynamics']['vertices'] == 40

    def test_orbit(self, P187):
        r = P187.rational_dynamics()
        assert 'orbit' in r['iteration']['orbit'].lower()

    def test_preperiodic(self, P187):
        r = P187.rational_dynamics()
        assert 'preperiodic' in r['iteration']['preperiodic']

    def test_poonen(self, P187):
        r = P187.rational_dynamics()
        assert 'Poonen' in r['uniform_boundedness']['quadratic']

    def test_entropy(self, P187):
        r = P187.rational_dynamics()
        assert 'entropy' in r['w33_dynamics']['entropy'].lower()

    def test_julia_set(self, P187):
        r = P187.rational_dynamics()
        assert 'Julia' in r['iteration']['julia_set'] or 'repelling' in r['iteration']['julia_set']

# ── dynamical_moduli ──────────────────────────────────────
class TestDynamicalModuli:
    def test_dimension(self, P187):
        r = P187.dynamical_moduli()
        assert '2d - 2' in r['moduli']['dimension'] or '2d-2' in r['moduli']['dimension']

    def test_mandelbrot_connected(self, P187):
        r = P187.dynamical_moduli()
        assert 'connected' in r['mandelbrot']['connectivity']

    def test_shishikura(self, P187):
        r = P187.dynamical_moduli()
        assert 'Shishikura' in r['mandelbrot']['boundary'] or 'dimension 2' in r['mandelbrot']['boundary']

    def test_sp6f2_moduli(self, P187):
        r = P187.dynamical_moduli()
        assert '1451520' in r['w33_moduli']['finite_moduli']

    def test_multiplier(self, P187):
        r = P187.dynamical_moduli()
        assert 'multiplier' in r['moduli']['multiplier_map']

# ── canonical_heights ──────────────────────────────────────
class TestCanonicalHeights:
    def test_canonical_height(self, P187):
        r = P187.canonical_heights()
        assert 'canonical' in r['heights']['canonical']

    def test_northcott(self, P187):
        r = P187.canonical_heights()
        assert 'Northcott' in r['heights']['northcott']

    def test_yuan(self, P187):
        r = P187.canonical_heights()
        assert 'Yuan' in r['equidistribution']['yuan_zhang']

    def test_baker_rumely(self, P187):
        r = P187.canonical_heights()
        assert 'Baker' in r['equidistribution']['baker_rumely']

    def test_w33_preperiodic(self, P187):
        r = P187.canonical_heights()
        assert 'preperiodic' in r['w33_heights']['preperiodic'].lower()

# ── p_adic_dynamics ────────────────────────────────────────
class TestPAdicDynamics:
    def test_berkovich(self, P187):
        r = P187.p_adic_dynamics()
        assert 'Berkovich' in r['p_adic']['berkovich']

    def test_rivera_letelier(self, P187):
        r = P187.p_adic_dynamics()
        assert 'Rivera-Letelier' in r['rivera_letelier']['classification']

    def test_f2(self, P187):
        r = P187.p_adic_dynamics()
        assert 'F_2' in r['w33_finite']['over_f2']

    def test_good_reduction(self, P187):
        r = P187.p_adic_dynamics()
        assert 'good reduction' in r['rivera_letelier']['good_reduction'].lower()

    def test_frobenius(self, P187):
        r = P187.p_adic_dynamics()
        assert 'Frobenius' in r['w33_finite']['frobenius']

# ── thurston_rigidity ──────────────────────────────────────
class TestThurstonRigidity:
    def test_pcf(self, P187):
        r = P187.thurston_rigidity()
        assert 'critically finite' in r['thurston']['pcf'].lower() or 'post-critically' in r['thurston']['pcf'].lower()

    def test_thurston_theorem(self, P187):
        r = P187.thurston_rigidity()
        assert 'Thurston' in r['thurston']['thurston_theorem']

    def test_teichmuller(self, P187):
        r = P187.thurston_rigidity()
        assert 'Teich' in r['teichmuller']['pullback']

    def test_w33_rigid(self, P187):
        r = P187.thurston_rigidity()
        assert 'rigid' in r['w33_thurston']['rigidity'].lower()

# ── dynamical_galois_theory ────────────────────────────────
class TestDynamicalGaloisTheory:
    def test_arboreal(self, P187):
        r = P187.dynamical_galois_theory()
        assert 'arboreal' in r['iterated_galois']['arboreal'].lower()

    def test_dynatomic(self, P187):
        r = P187.dynamical_galois_theory()
        assert 'Phi_n' in r['dynatomic']['definition'] or 'dynatomic' in r['dynatomic']['definition']

    def test_sp6f2_galois(self, P187):
        r = P187.dynamical_galois_theory()
        assert 'Sp(6,F2)' in r['w33_galois']['galois_action']

    def test_dessins(self, P187):
        r = P187.dynamical_galois_theory()
        assert 'Belyi' in r['w33_galois']['dessins'] or 'dessin' in r['w33_galois']['dessins'].lower()

# ── self-checks ────────────────────────────────────────────
class TestSelfChecks:
    def test_all_pass(self, P187):
        assert P187.run_self_checks() is True
