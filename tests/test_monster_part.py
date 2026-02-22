import runpy
import numpy as np

def test_monster_script_runs_and_outputs():
    # run the CLXIII script and capture globals
    globs = runpy.run_path("THEORY_PART_CLXIII_MONSTER_DM.py")
    # verify key variables exist
    assert "m_monster" in globs
    assert globs["m_monster"] == 196884.0
    assert "flux" in globs
    flux = globs["flux"]
    assert isinstance(flux, np.ndarray)
    # heavy mass leads to tiny flux; should be well below 1e-5 in our toy model
    assert flux.max() < 1e-5


def test_monster_flux_ratio():
    # ensure the heavy DM mass is roughly three orders of magnitude above the
    # lighter W33 candidate (approx. 150 GeV)
    m = runpy.run_path("THEORY_PART_CLXIII_MONSTER_DM.py")["m_monster"]
    assert m / 150 > 1e3  # at least thousand-fold heavier
