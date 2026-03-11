"""Quick count of test methods in phase files."""
import re, os

phases = [
    ("LXXXV", "test_spectral_action_functionals.py"),
    ("LXXXVI", "test_ko_dimension_real_spectral.py"),
    ("LXXXVII", "test_precision_electroweak_g2.py"),
    ("LXXXVIII", "test_brst_cohomology_ghost.py"),
    ("LXXXIX", "test_holography_ads_cft.py"),
    ("XC", "test_topological_defects_solitons.py"),
    ("XCI", "test_automorphic_langlands.py"),
    ("XCII", "test_m_theory_exceptional.py"),
    ("XCIII", "test_w33_uor_landauer_monster_bridge.py"),
    ("XCIV", "test_qec_stabilizer_codes.py"),
    ("XCV", "test_loop_quantum_gravity.py"),
    ("XCVI", "test_asymptotic_bms.py"),
    ("XCVII", "test_susy_breaking_soft.py"),
    ("XCVIII", "test_ncg_spectral_model.py"),
    ("XCIX", "test_page_curve_unitarity.py"),
    ("C", "test_grand_unified_closure.py"),
    ("CI", "test_categorical_foundations.py"),
    ("CII", "test_amplituhedron_scattering.py"),
    ("CIII", "test_swampland_landscape.py"),
    ("CIV", "test_topological_qc.py"),
    ("CV", "test_emergent_spacetime.py"),
    ("CVI", "test_precision_observables.py"),
    ("CVII", "test_ultimate_closure.py"),
    ("CVIII", "test_qg_phenomenology.py"),
    ("CIX", "test_celestial_holography.py"),
    ("CX", "test_quantum_chaos.py"),
    ("CXI", "test_generalized_symmetries.py"),
    ("CXII", "test_quantum_cosmology.py"),
    ("CXIII", "test_experimental_signatures.py"),
    ("CXIV", "test_absolute_final_synthesis.py"),
]

total = 0
for phase, fname in phases:
    path = os.path.join('tests', fname)
    if not os.path.exists(path):
        print(f"{phase}: {fname} -> FILE NOT FOUND")
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    count = len(re.findall(r'def test_', content))
    total += count
    print(f"{phase}: {count} tests")

print(f"\nTotal: {total} tests across {len(phases)} phases")
