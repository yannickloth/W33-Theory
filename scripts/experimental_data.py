#!/usr/bin/env python3
"""Utilities for fetching up-to-date experimental data from the web.

The functions here attempt to scrape relevant tables from Wikipedia (or
other accessible sources) so that our various analysis scripts can compare
finite-geometry predictions with the latest measurements without manual
updates.

All fetchers return ``None`` on error; callers should fall back to the
hard‑coded default values included elsewhere in the repository.
"""

from __future__ import annotations

import re
import urllib.request

import numpy as np


def fetch_ckm_from_wikipedia(timeout: float = 10) -> np.ndarray | None:
    """Return a 3x3 array of CKM magnitudes scraped from Wikipedia.

    The page contains a table of matrix elements with entries like
    ``|V_{ud}| = 0.97373``; the routine looks for the first nine such
    numbers and arranges them in row-major order.  If the page structure
    changes or the network request fails, ``None`` is returned.
    """
    url = (
        "https://en.wikipedia.org/wiki/Cabibbo%E2%80%93Kobayashi%E2%80%93Maskawa_matrix"
    )
    try:
        html = urllib.request.urlopen(url, timeout=timeout).read().decode("utf-8")
        nums = re.findall(r"V_[uc,t][dsb]?\|?\s*=\s*([0]\.[0-9]+)", html)
        if len(nums) >= 9:
            vals = list(map(float, nums[:9]))
            return np.array(vals).reshape((3, 3))
    except Exception:
        pass
    return None


def fetch_pmns_from_wikipedia(timeout: float = 10) -> np.ndarray | None:
    """Return a 3x3 array of PMNS magnitudes scraped from Wikipedia.

    The PMNS page lists approximate magnitudes in a table; we look for
    entries of the form ``|U_{e1}| = 0.822`` etc.  Nine numbers are
    returned in row-major order if found.
    """
    url = "https://en.wikipedia.org/wiki/Pontecorvo%E2%80%93Maki%E2%80%93Nakagawa%E2%80%93Sakata_matrix"
    try:
        html = urllib.request.urlopen(url, timeout=timeout).read().decode("utf-8")
        nums = re.findall(r"U_[e\u03bcm][123]\|?\s*=\s*([0]\.[0-9]+)", html)
        if len(nums) >= 9:
            vals = list(map(float, nums[:9]))
            return np.array(vals).reshape((3, 3))
    except Exception:
        pass
    return None


def fetch_neutrino_mass_limits(timeout: float = 10) -> dict[str, float] | None:
    """Scrape a few simple neutrino-mass bounds from Wikipedia.

    Currently returns a dict containing ``"masser"`` for electron-neutrino
    mass limit (from beta-decay) and ``"sum"`` for the cosmological
    upper bound on the sum of masses, if both can be found.  The method is
    fragile and may need updating.
    """
    url = "https://en.wikipedia.org/wiki/Neutrino"  # mass limits appear here
    try:
        html = urllib.request.urlopen(url, timeout=timeout).read().decode("utf-8")
        # look for phrases like “< 1.1 eV” near "electron neutrino"
        m = re.search(r"electron neutrino[\s\S]{0,60}?<[\s]*([0-9\.]+)\s*eV", html)
        sum_m = re.search(r"sum of the neutrino masses[\s\S]{0,60}?<[\s]*([0-9\.]+)\s*eV", html)
        out = {}
        if m:
            out["masser"] = float(m.group(1))
        if sum_m:
            out["sum"] = float(sum_m.group(1))
        if out:
            return out
    except Exception:
        pass
    return None


def fetch_fermion_masses_from_wikipedia(timeout: float = 10) -> dict[str, float] | None:
    """Scrape a handful of fermion masses (GeV) from Wikipedia.

    Returns a dict mapping PDG symbols 'u','d','s','c','b','t','e','μ','τ' to
    floating-point masses.  The algorithm is crude and may fail silently.
    """
    url = "https://en.wikipedia.org/wiki/Fermion"
    try:
        html = urllib.request.urlopen(url, timeout=timeout).read().decode("utf-8")
        masses = {}
        # look for mass entries like "u = 2.16×10⁻³ GeV" or "u 2.16×10-3 GeV"
        for sym in ["u", "d", "s", "c", "b", "t", "e", "μ", "τ"]:
            pattern = rf"{sym}[^0-9\-\.|eE]+([0-9\.]+)(?:×10\^(?:-|\u2212)([0-9]+))?\s*GeV"
            m = re.search(pattern, html)
            if m:
                val = float(m.group(1))
                if m.group(2):
                    val *= 10 ** (-int(m.group(2)))
                masses[sym] = val
        return masses if masses else None
    except Exception:
        return None
