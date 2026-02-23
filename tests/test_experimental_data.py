import numpy as np
import pytest

from scripts.experimental_data import (
    fetch_ckm_from_wikipedia,
    fetch_pmns_from_wikipedia,
    fetch_neutrino_mass_limits,
    fetch_fermion_masses_from_wikipedia,
)


def test_ckm_fetch_shape_or_none():
    val = fetch_ckm_from_wikipedia()
    if val is not None:
        assert isinstance(val, np.ndarray)
        assert val.shape == (3, 3)
        assert (val >= 0).all() and (val <= 1).all()


def test_pmns_fetch_shape_or_none():
    val = fetch_pmns_from_wikipedia()
    if val is not None:
        assert isinstance(val, np.ndarray)
        assert val.shape == (3, 3)
        assert (val >= 0).all() and (val <= 1).all()


def test_neutrino_limits_structure():
    val = fetch_neutrino_mass_limits()
    if val is not None:
        assert "masser" in val or "sum" in val
        for k, v in val.items():
            assert isinstance(v, float)
            assert v >= 0


# mark network-dependent tests as xfail if offline
@pytest.fixture(autouse=True)
def check_network(request):
    # simple check: try to resolve wikipedia
    import socket
    try:
        socket.gethostbyname("en.wikipedia.org")
    except Exception:
        pytest.xfail("no network")


def test_fermion_mass_fetch():
    masses = fetch_fermion_masses_from_wikipedia()
    if masses is not None:
        assert 'e' in masses and 'μ' in masses and 'τ' in masses
        for v in masses.values():
            assert isinstance(v, float) and v > 0

