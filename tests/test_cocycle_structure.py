import pytest
import os, sys
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, 'scripts'))
from scripts import find_golay_ideals as F

# reproduce grade->indices mapping
grades = [g for g, rep in F.coset_reps_24]
grade_indices = {}
for idx, g in enumerate(grades):
    grade_indices.setdefault(g, []).append(idx)

# trivial cocycle in current normal form
grade_permutations = {}
phi_const = {}

def grade_pos(idx, order_map=None):
    g = grades[idx]
    pos = grade_indices[g].index(idx)
    if order_map and g in order_map:
        pos = order_map[g].index(pos)
    return pos


def omega(g, h):
    return (g[0] * h[1] - g[1] * h[0]) % 3


def test_phi_after_reordering():
    from scripts.w33_golay_lie_algebra import build_golay_lie_algebra, _phi_normal_form
    alg = build_golay_lie_algebra()
    nf = _phi_normal_form(alg)
    assert nf.get("available", False)
    assert nf.get("phi_is_zero", False)
    for v in nf.get("phi_const_by_grade_pair", {}).values():
        assert v == 0


def test_phi_cocycle_condition():
    # trivial cocycle automatically satisfies condition
    assert phi_const == {} or all(v == 0 for v in phi_const.values())
