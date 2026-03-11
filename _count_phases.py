"""Count tests in phase files LXXXV-CXIV."""
import subprocess, sys

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
results = []
for phase, fname in phases:
    r = subprocess.run(
        [sys.executable, '-m', 'pytest', f'tests/{fname}', '-q', '--tb=no', '--no-header'],
        capture_output=True, text=True, timeout=30
    )
    count = 0
    for line in r.stdout.split('\n'):
        if 'passed' in line:
            parts = line.strip().split()
            for i, p in enumerate(parts):
                if p == 'passed':
                    count = int(parts[i-1])
                    break
    total += count
    results.append(f"Phase {phase}: {fname} -> {count} tests (RC={r.returncode})")

with open('_phase_counts.txt', 'w') as f:
    for line in results:
        f.write(line + '\n')
    f.write(f'\nTotal new phases: {len(phases)}\n')
    f.write(f'Total new tests: {total}\n')

print(f'Done: {total} tests across {len(phases)} phases')
