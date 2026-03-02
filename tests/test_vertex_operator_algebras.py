"""Tests for Pillar 160 — Vertex Operator Algebras."""
import pytest, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT / "pillars") not in sys.path:
    sys.path.insert(0, str(ROOT / "pillars"))

from THEORY_PART_CCLX_VERTEX_OPERATOR_ALGEBRAS import (
    vertex_algebra_foundations,
    voa_definition,
    ope_structure,
    monster_voa,
    lattice_voa,
    affine_voa,
    voa_modules,
    virasoro_minimal,
    extended_algebras,
    chiral_algebras,
    voa_e8,
    complete_chain,
    run_all_checks,
)


class TestVertexAlgebraFoundations:
    def test_founder(self):
        assert vertex_algebra_foundations()['founder'] == 'Richard Borcherds'

    def test_year(self):
        assert vertex_algebra_foundations()['year'] == 1986

    def test_state_field(self):
        r = vertex_algebra_foundations()
        assert 'V((z))' in r['data']['multiplication']

    def test_locality(self):
        r = vertex_algebra_foundations()
        assert 'locality' in r['axioms']


class TestVOADefinition:
    def test_year(self):
        assert voa_definition()['year'] == 1988

    def test_authors(self):
        r = voa_definition()
        assert 'Frenkel' in r['introduced_by'][0]

    def test_virasoro(self):
        r = voa_definition()
        assert 'L_m' in r['conformal_structure']['virasoro_relations']

    def test_central_charge(self):
        r = voa_definition()
        assert 'central charge' in r['conformal_structure']['central_charge']


class TestOPE:
    def test_virasoro_tt(self):
        r = ope_structure()
        assert 'T(z)T(w)' in r['examples']['virasoro_tt']

    def test_free_boson(self):
        r = ope_structure()
        assert 'b(z)b(w)' in r['examples']['free_boson']


class TestMonsterVOA:
    def test_central_charge(self):
        assert monster_voa()['properties']['central_charge'] == 24

    def test_monster_group(self):
        assert 'Monster' in monster_voa()['properties']['automorphism_group']

    def test_character(self):
        r = monster_voa()
        assert '196884' in r['properties']['character']

    def test_moonshine_proof(self):
        r = monster_voa()
        assert 'Borcherds' in r['moonshine']['proved_by']

    def test_fields_medal(self):
        r = monster_voa()
        assert '1998' in r['moonshine']['fields_medal']

    def test_leech_orbifold(self):
        r = monster_voa()
        assert 'Leech' in r['construction']['method']


class TestLatticeVOA:
    def test_e8_lattice(self):
        r = lattice_voa()
        assert 'E8' in r['examples']['e8_lattice']['lattice']

    def test_e8_simplest(self):
        r = lattice_voa()
        assert '248' in r['examples']['e8_lattice']['significance']

    def test_frenkel_kac(self):
        r = lattice_voa()
        assert 'ADE' in r['frenkel_kac']['theorem']


class TestAffineVOA:
    def test_sugawara(self):
        r = affine_voa()
        assert 'omega' in r['construction']['sugawara']

    def test_wzw(self):
        r = affine_voa()
        assert 'WZW' in r['physics']['wzw'] or 'Wess' in r['physics']['wzw']


class TestModules:
    def test_zhu(self):
        r = voa_modules()
        assert 'SL(2,Z)' in r['zhu_theorem']['statement']

    def test_verlinde(self):
        r = voa_modules()
        assert 'Verlinde' in r['huang_theorem']['verlinde']


class TestMinimalModels:
    def test_ising(self):
        r = virasoro_minimal()
        assert r['central_charges']['examples']['ising']['c'] == 0.5

    def test_ising_modules(self):
        assert virasoro_minimal()['ising_detail']['modules'] == 3


class TestExtendedAlgebras:
    def test_n1_superconformal(self):
        r = extended_algebras()
        assert 'Neveu-Schwarz' in r['superconformal']['N1']['algebras']

    def test_w_algebras(self):
        r = extended_algebras()
        assert 'BRST' in r['w_algebras']['construction']


class TestChiralAlgebras:
    def test_beilinson_drinfeld(self):
        r = chiral_algebras()
        assert 'Beilinson' in r['chiral']['introduced_by'][0]

    def test_langlands(self):
        r = chiral_algebras()
        assert 'Langlands' in r['langlands']['connection']


class TestE8Connection:
    def test_w33_chain(self):
        r = voa_e8()
        assert any('W(3,3)' in p for p in r['w33_chain']['path'])

    def test_heterotic(self):
        r = voa_e8()
        assert 'E8 x E8' in r['connections']['heterotic']['right_movers']


class TestCompleteChain:
    def test_links(self):
        assert len(complete_chain()['links']) == 6

    def test_miracle(self):
        assert 'VERTEX OPERATORS' in complete_chain()['miracle']['statement']


class TestAllChecks:
    def test_run_all(self):
        assert run_all_checks() is True
