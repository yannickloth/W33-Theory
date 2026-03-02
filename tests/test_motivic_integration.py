"""
Tests for Pillar 166 — Motivic Integration.
"""

import pytest
from THEORY_PART_CCLXVI_MOTIVIC_INTEGRATION import (
    motivic_integration_foundations,
    arc_spaces,
    motivic_measure,
    kontsevich_theorem,
    motivic_zeta,
    stringy_invariants,
    motivic_mckay,
    padic_connection,
    connections_to_prior,
    e8_motivic,
    w33_chain,
    motivic_dt,
    motivic_cohomology,
    applications,
    complete_chain,
)


class TestFoundations:
    def test_founder(self):
        f = motivic_integration_foundations()
        assert 'Kontsevich' in f['founder']
        assert f['year'] == 1995

    def test_grothendieck_ring(self):
        f = motivic_integration_foundations()
        assert 'scissor' in f['grothendieck_ring']['scissor'].lower()
        assert 'L = [A' in f['grothendieck_ring']['lefschetz']

    def test_motivation(self):
        f = motivic_integration_foundations()
        assert 'Calabi-Yau' in f['motivation']


class TestArcSpaces:
    def test_jet_spaces(self):
        arc = arc_spaces()
        assert 'J_n(X)' in arc['jet_spaces']['definition']

    def test_arc_space(self):
        arc = arc_spaces()
        assert 'lim' in arc['arc_space']['definition']

    def test_nash(self):
        arc = arc_spaces()
        assert 'Nash' in arc['nash_problem']['statement']


class TestMotivicMeasure:
    def test_values(self):
        mm = motivic_measure()
        assert 'K₀(Var_k)' in mm['measure']['values']

    def test_change_of_variables(self):
        mm = motivic_measure()
        assert 'Jacobian' in mm['change_of_variables']['key_tool']


class TestKontsevich:
    def test_theorem(self):
        kt = kontsevich_theorem()
        assert 'Hodge' in kt['theorem']['statement']
        assert 'birational' in kt['theorem']['statement'].lower()

    def test_calabi_yau(self):
        kt = kontsevich_theorem()
        assert 'K_X' in kt['calabi_yau']['definition']


class TestMotivicZeta:
    def test_authors(self):
        mz = motivic_zeta()
        assert 'Denef' in mz['authors']

    def test_rationality(self):
        mz = motivic_zeta()
        assert 'rational' in mz['definition']['rationality'].lower()

    def test_monodromy(self):
        mz = motivic_zeta()
        assert 'monodromy' in mz['monodromy_conjecture']['statement'].lower()


class TestStringy:
    def test_batyrev(self):
        si = stringy_invariants()
        assert 'Batyrev' in si['author']

    def test_independence(self):
        si = stringy_invariants()
        assert 'independent' in si['stringy_e_function']['independence'].lower()


class TestMcKay:
    def test_classical(self):
        mk = motivic_mckay()
        assert 'McKay' in mk['classical_mckay']['statement']

    def test_e8(self):
        mk = motivic_mckay()
        assert 'E8' in mk['e8_connection']['e8_singularity']


class TestPadic:
    def test_igusa(self):
        pa = padic_connection()
        assert 'Igusa' in pa['padic_integration']['igusa']

    def test_ngo(self):
        pa = padic_connection()
        assert 'Fields' in pa['fundamental_lemma']['ngo']


class TestE8Motivic:
    def test_singularity(self):
        e8 = e8_motivic()
        assert 'x² + y³ + z⁵' in e8['e8_singularity']['surface']

    def test_27_lines(self):
        e8 = e8_motivic()
        assert '27 lines' in e8['del_pezzo']['w33']


class TestW33:
    def test_path(self):
        wc = w33_chain()
        assert any('W(3,3)' in p for p in wc['path'])

    def test_deep(self):
        wc = w33_chain()
        assert 'Grothendieck' in wc['deep_connection']


class TestMotivicDT:
    def test_authors(self):
        dt = motivic_dt()
        assert 'Kontsevich-Soibelman' in dt['authors']

    def test_wall_crossing(self):
        dt = motivic_dt()
        assert 'wall-crossing' in dt['motivic_lift']['wall_crossing'].lower()


class TestMotivicCohomology:
    def test_voevodsky(self):
        mc = motivic_cohomology()
        assert 'Voevodsky' in mc['voevodsky']['founder']

    def test_milnor(self):
        mc = motivic_cohomology()
        assert 'Milnor' in mc['voevodsky']['milnor']


class TestApplications:
    def test_birational(self):
        ap = applications()
        assert 'flips' in ap['birational']['termination'].lower()

    def test_number_theory(self):
        ap = applications()
        assert 'fundamental' in ap['number_theory']['langlands'].lower()


class TestComplete:
    def test_links(self):
        cc = complete_chain()
        assert len(cc['links']) == 6

    def test_miracle(self):
        cc = complete_chain()
        assert 'MIRACLE' in cc['miracle']['statement']
        assert 'Grothendieck' in cc['miracle']['depth']
