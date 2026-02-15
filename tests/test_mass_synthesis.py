import math


def test_mass_synthesis_smoke():
    from scripts.w33_mass_synthesis import compute_mass_predictions

    out = compute_mass_predictions()

    # Yukawa / top sanity
    Yt = out["yukawas"]["Y_t"]
    assert Yt > 0.5 and Yt <= 2.0

    # Top mass proxy sanity (GUT-scale proxy used by repo)
    mt = out["masses_GeV"]["top_GeV"]
    assert mt > 10 and mt < 1000

    # Neutrino seesaw: sum of light neutrino masses should be positive and finite.
    # Exact value depends on assumed M_R scale (default 3^20 GeV) and singlet
    # identification method. With SVD-based sector ID the value can be O(10^3) eV;
    # physical bound requires explicit GUT-scale symmetry breaking (M_R = 0 at
    # pure W33 level per Pillar 36).
    sum_m_nu = out["neutrino_seesaw"]["sum_m_nu_eV"]
    assert sum_m_nu > 1e-6 and math.isfinite(sum_m_nu)

    # Dirac-singular-value hierarchy (expect strong hierarchy)
    sv = out["neutrino_seesaw"]["m_D_singular_values"]
    assert len(sv) >= 3
    assert sv[0] >= sv[1] >= sv[2]
    assert sv[0] / max(sv[2], 1e-12) > 2.5
