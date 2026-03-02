"""
Tests for Pillar 144 — Information Geometry & Quantum Information
"""
import pytest
from THEORY_PART_CCXLIV_INFORMATION_GEOMETRY import (
    fisher_information_metric,
    statistical_manifolds,
    quantum_fisher_information,
    von_neumann_entropy,
    ryu_takayanagi,
    entanglement_builds_spacetime,
    quantum_no_go_theorems,
    quantum_channels,
    holographic_qec,
    quantum_info_quantities,
    area_laws,
    complete_chain_w33_to_information,
    run_all_checks,
)


class TestFisherMetric:
    def test_discoverer(self):
        r = fisher_information_metric()
        assert r['discoverer'] == 'C. R. Rao'
    
    def test_year(self):
        r = fisher_information_metric()
        assert r['year_rao'] == 1945
    
    def test_properties_count(self):
        r = fisher_information_metric()
        assert len(r['properties']) == 5
    
    def test_normal_curvature(self):
        r = fisher_information_metric()
        assert r['normal_distribution']['curvature'] == -0.5
    
    def test_chentsov(self):
        r = fisher_information_metric()
        assert 'unique' in r['chentsov_theorem'].lower()
    
    def test_cramer_rao_year(self):
        r = fisher_information_metric()
        assert r['cramer_rao']['year'] == 1945
    
    def test_connections(self):
        r = fisher_information_metric()
        assert len(r['connections']) >= 4


class TestStatisticalManifolds:
    def test_examples_count(self):
        r = statistical_manifolds()
        assert len(r['examples']) == 4
    
    def test_normal_geometry(self):
        r = statistical_manifolds()
        assert 'Poincaré' in r['examples'][0]['geometry'] or 'half-plane' in r['examples'][0]['geometry']
    
    def test_f3_example(self):
        r = statistical_manifolds()
        assert r['examples'][3]['dimension'] == 2
    
    def test_natural_gradient(self):
        r = statistical_manifolds()
        assert 'Neural networks' in r['natural_gradient']['applications']
    
    def test_w33_connection(self):
        r = statistical_manifolds()
        assert 'F₃' in r['w33_connection'] or 'F_3' in r['w33_connection']


class TestQuantumFisherInfo:
    def test_fubini_study(self):
        r = quantum_fisher_information()
        assert 'δψ' in r['fubini_study']['formula']
    
    def test_bures_metric(self):
        r = quantum_fisher_information()
        assert 'SLD' in r['bures_metric']['sld'] or 'symmetric' in r['bures_metric']['sld'].lower()
    
    def test_quantum_cramer_rao(self):
        r = quantum_fisher_information()
        assert 'LIGO' in str(r['quantum_cramer_rao']['applications'])
    
    def test_classical_to_quantum(self):
        r = quantum_fisher_information()
        assert 'density_matrix' in r['classical_to_quantum']['probability_distribution'] or \
               'density' in r['classical_to_quantum']['probability_distribution']


class TestVonNeumannEntropy:
    def test_year(self):
        r = von_neumann_entropy()
        assert r['year'] == 1932
    
    def test_properties_count(self):
        r = von_neumann_entropy()
        assert len(r['properties']) == 7
    
    def test_pure_state_zero(self):
        r = von_neumann_entropy()
        assert r['qubit_entropy']['pure_state'] == 0.0
    
    def test_bell_pair(self):
        r = von_neumann_entropy()
        assert r['qubit_entropy']['bell_pair_each_half'] == 1.0
    
    def test_conditional_can_be_negative(self):
        r = von_neumann_entropy()
        assert 'NEGATIVE' in r['entropic_quantities']['conditional']


class TestRyuTakayanagi:
    def test_year(self):
        r = ryu_takayanagi()
        assert r['year'] == 2006
    
    def test_authors(self):
        r = ryu_takayanagi()
        assert 'Shinsei Ryu' in r['authors']
    
    def test_conditions(self):
        r = ryu_takayanagi()
        assert len(r['rt_surface_conditions']) == 3
    
    def test_breakthrough_prize(self):
        r = ryu_takayanagi()
        assert 'Breakthrough' in r['awards'][0]
    
    def test_formula(self):
        r = ryu_takayanagi()
        assert 'Area' in r['formula'] and '4 G' in r['formula']
    
    def test_generalizations(self):
        r = ryu_takayanagi()
        assert 'HRT' in r['generalizations']


class TestEntanglementSpacetime:
    def test_key_insights_count(self):
        r = entanglement_builds_spacetime()
        assert len(r['key_insights']) == 4
    
    def test_er_epr(self):
        r = entanglement_builds_spacetime()
        assert 'ER = EPR' in r['key_insights'][1]['name']
    
    def test_tensor_networks(self):
        r = entanglement_builds_spacetime()
        assert 'MERA' in r['key_insights'][2]['insight']
    
    def test_einstein_from_entanglement(self):
        r = entanglement_builds_spacetime()
        assert 'Einstein' in r['einstein_from_entanglement']['result']


class TestNoGoTheorems:
    def test_count(self):
        r = quantum_no_go_theorems()
        assert r['num_theorems'] == 5
    
    def test_no_cloning(self):
        r = quantum_no_go_theorems()
        assert r['theorems'][0]['name'] == 'No-cloning theorem'
        assert r['theorems'][0]['year'] == 1982
    
    def test_unitarity(self):
        r = quantum_no_go_theorems()
        assert 'unitarity' in r['unifying_principle'].lower()


class TestQuantumChannels:
    def test_channel_types(self):
        r = quantum_channels()
        assert len(r['channel_types']) == 4
    
    def test_holevo_year(self):
        r = quantum_channels()
        assert r['capacities']['classical']['holevo_year'] == 1973
    
    def test_protocols(self):
        r = quantum_channels()
        assert len(r['protocols']) >= 4


class TestHolographicQEC:
    def test_key_paper(self):
        r = holographic_qec()
        assert 'Almheiri' in r['key_paper']
    
    def test_tensor_networks(self):
        r = holographic_qec()
        assert len(r['tensor_networks']) >= 3
    
    def test_e8_connection(self):
        r = holographic_qec()
        assert 'E₈' in r['e8_qec_connection'] or 'E_8' in r['e8_qec_connection']


class TestInfoQuantities:
    def test_count(self):
        r = quantum_info_quantities()
        assert r['num_quantities'] == 5
    
    def test_conditional_surprise(self):
        r = quantum_info_quantities()
        assert 'NEGATIVE' in r['quantities'][3]['surprise']
    
    def test_geometry_connections(self):
        r = quantum_info_quantities()
        assert 'fisher' in r['geometry_connections']['fisher_metric'].lower() or \
               'Hessian' in r['geometry_connections']['fisher_metric']


class TestAreaLaws:
    def test_hastings(self):
        r = area_laws()
        assert 'Hastings' in r['by_dimension'][0]['status']
    
    def test_tee(self):
        r = area_laws()
        assert r['tee']['year'] == 2006
    
    def test_toric_code_tee(self):
        r = area_laws()
        assert r['tee']['examples']['toric_code'] == 'γ = log 2'


class TestChain:
    def test_num_links(self):
        chain = complete_chain_w33_to_information()
        assert chain['num_links'] == 7
    
    def test_miracle(self):
        chain = complete_chain_w33_to_information()
        assert 'INFORMATION GEOMETRY IS SPACETIME GEOMETRY' in chain['miracle']
    
    def test_links(self):
        chain = complete_chain_w33_to_information()
        assert len(chain['links']) == 7
        assert chain['links'][0]['from'] == 'W(3,3) combinatorial design'


class TestRunChecks:
    def test_all_pass(self):
        checks = run_all_checks()
        for name, ok in checks:
            assert ok, f"Check failed: {name}"
    
    def test_count(self):
        checks = run_all_checks()
        assert len(checks) == 15
