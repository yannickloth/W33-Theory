from scripts.w33_monster_structure_bridge_report import _MONOMIAL_FACTORIES
from scripts.monomial_utils import find_sign_lifts_for_group, monomial_group_order
from tools.s12_universal_algebra import (
    enumerate_linear_code_f3,
    ternary_golay_generator_matrix,
)
from scripts.ce2_global_cocycle import predict_ce2_uv


def test_ce2_nontrivial_when_monolift_exists():
    # build Golay code data for sign-lift search
    gen = ternary_golay_generator_matrix()
    generator_rows = [tuple(int(x) % 3 for x in row) for row in gen]
    code_set = set(enumerate_linear_code_f3(gen))

    # search among factories
    for cls, factory in _MONOMIAL_FACTORIES.items():
        perms = factory()
        lifts = find_sign_lifts_for_group(perms, generator_rows, code_set)
        if lifts is None:
            continue
        order = monomial_group_order(list(zip(perms, lifts)))
        # if lifted group has order > 1, expect some CE2 anomaly exists
        if order > 1:
            found = False
            for a in [(i, j) for i in range(3) for j in range(3)]:
                for b in [(i, j) for i in range(3) for j in range(3)]:
                    for c in [(i, j) for i in range(3) for j in range(3)]:
                        uv = predict_ce2_uv(a, b, c)
                        if uv is not None and (uv.U or uv.V):
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            assert found, f"no CE2 anomaly found for class {cls} despite monolift"