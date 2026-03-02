import importlib.util
import random

spec = importlib.util.spec_from_file_location("the_exact_map", "exploration/THE_EXACT_MAP.py")
exact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exact)


def test_line_rep_is_tuned_and_sample_cocycle_matches_expected():
    """Pin the canonical `line_rep` and verify the sampled cocycle pass/fail counts.

    This test is intentionally lightweight (uses the same 50→15 sampling THE_EXACT_MAP.py uses)
    and prevents accidental regressions to the tuned representatives.
    """
    expected = [
        (0, 0),
        (1, 0),
        (0, 0),
        (1, 2),
        (2, 2),
        (1, 1),
        (2, 0),
        (2, 1),
        (1, 1),
        (2, 2),
        (1, 2),
        (2, 1),
    ]

    assert exact.line_rep == expected

    random.seed(42)
    sample = random.sample(exact.weight_6, 50)

    cocycle_pass = 0
    cocycle_fail = 0
    zero = tuple([0] * 12)

    for a in sample[:15]:
        for b in sample[:15]:
            for c in sample[:15]:
                if a != b and b != c and a != c:
                    bc = tuple((b[i] + c[i]) % 3 for i in range(12))
                    ca = tuple((c[i] + a[i]) % 3 for i in range(12))
                    ab = tuple((a[i] + b[i]) % 3 for i in range(12))

                    if bc != zero and ca != zero and ab != zero:
                        s1 = exact.symplectic_sign(a, bc) * exact.symplectic_sign(b, c)
                        s2 = exact.symplectic_sign(b, ca) * exact.symplectic_sign(c, a)
                        s3 = exact.symplectic_sign(c, ab) * exact.symplectic_sign(a, b)

                        if s1 == s2 == s3:
                            cocycle_pass += 1
                        else:
                            cocycle_fail += 1

    # Preserve determinism: ensure the total tested triples remains the same
    assert cocycle_pass + cocycle_fail == 2652
    # Require sampled-cocycle does not regress: compare against the canonical baseline
    import scripts.tune_line_reps as tune

    canon = [tune.exact.canonical_point(l) for l in tune.exact.F3_lines]
    base_pc, base_fc, base_rate = tune.evaluate_line_rep(canon, sample)
    assert cocycle_pass >= base_pc
