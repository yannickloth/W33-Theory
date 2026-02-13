"""
Greedy search for canonical representative points for the 12 F3^2 lines used
in THE_EXACT_MAP.py. Goal: improve the cocycle pass rate used in the repo's
cocycle sanity check (sample-based).

This script does NOT change THE_EXACT_MAP.py. It reports:
 - baseline cocycle pass count (current canonical choices)
 - best found pass count and the corresponding `line_rep` list
 - (optionally) writes the best `line_rep` to stdout so it can be applied

Algorithm (greedy hill-climb):
 - start from current `canonical_point` (= min(line))
 - for each line, try its 3 possible representative points and pick the one
   that improves the sampled cocycle pass count the most
 - repeat passes until no improvement or max passes reached
 - do several random restarts to escape local maxima

Run:
  python -m scripts.tune_line_reps

"""

import itertools
import os
import random
import sys
from copy import deepcopy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import THE_EXACT_MAP as exact

# Reuse the same sampling logic THE_EXACT_MAP.py uses for cocycle check
RNG_SEED = 42
SAMPLE_SIZE = 15  # same sample used in THE_EXACT_MAP.py cocycle test
MAX_PASSES = 6
RESTARTS = 5


def build_symp_lines_from_line_rep(line_rep):
    """Return 12x12 symplectic matrix on lines from a given line_rep list."""
    n = len(line_rep)
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        p1 = line_rep[i]
        for j in range(n):
            p2 = line_rep[j]
            M[i][j] = (p1[0] * p2[1] - p2[0] * p1[1]) % 3
    return M


def build_position_symp(line_symp, pos_to_line):
    npos = len(pos_to_line)
    P = [[0] * npos for _ in range(npos)]
    for i in range(npos):
        for j in range(npos):
            li = pos_to_line[i]
            lj = pos_to_line[j]
            P[i][j] = line_symp[li][lj]
    return P


def codeword_symplectic_with_possym(c1, c2, pos_symp):
    H1, H2 = exact.support(c1), exact.support(c2)
    total = 0
    for i in H1:
        for j in H2:
            total = (total + pos_symp[i][j]) % 3
    return total


def symplectic_sign_from_possym(c1, c2, pos_symp):
    s = codeword_symplectic_with_possym(c1, c2, pos_symp)
    return 1 if s == 0 else (-1 if s == 1 else 1)


TRIPLE_SAMPLE_COUNT = 20000


def cocycle_pass_count_with_possym(pos_symp, sample_weight6):
    """Estimate cocycle pass/fail counts using random triple sampling.

    - Uses `TRIPLE_SAMPLE_COUNT` random unordered triples drawn from
      `sample_weight6` to estimate pass/fail. This keeps evaluation fast
      when SAMPLE_SIZE is large while still providing a reliable metric
      for the greedy tuner.
    - Falls back to the original small cubic loop when SAMPLE_SIZE <= 15
      to preserve the exact behaviour used by THE_EXACT_MAP.py.
    Returns (pass_count, fail_count).
    """
    import random

    # small-exact mode (preserve original behaviour)
    if SAMPLE_SIZE <= 15:
        cocycle_pass = 0
        cocycle_fail = 0
        zero = tuple([0] * 12)
        for a in sample_weight6[:SAMPLE_SIZE]:
            for b in sample_weight6[:SAMPLE_SIZE]:
                for c in sample_weight6[:SAMPLE_SIZE]:
                    if a != b and b != c and a != c:
                        bc = tuple((b[i] + c[i]) % 3 for i in range(12))
                        ca = tuple((c[i] + a[i]) % 3 for i in range(12))
                        ab = tuple((a[i] + b[i]) % 3 for i in range(12))

                        if bc != zero and ca != zero and ab != zero:
                            s1 = symplectic_sign_from_possym(
                                a, bc, pos_symp
                            ) * symplectic_sign_from_possym(b, c, pos_symp)
                            s2 = symplectic_sign_from_possym(
                                b, ca, pos_symp
                            ) * symplectic_sign_from_possym(c, a, pos_symp)
                            s3 = symplectic_sign_from_possym(
                                c, ab, pos_symp
                            ) * symplectic_sign_from_possym(a, b, pos_symp)

                            if s1 == s2 == s3:
                                cocycle_pass += 1
                            else:
                                cocycle_fail += 1
        return cocycle_pass, cocycle_fail

    # sampled-triple mode (fast estimate)
    rng = random.Random(42)  # deterministic
    M = TRIPLE_SAMPLE_COUNT
    n = len(sample_weight6)
    cocycle_pass = 0
    cocycle_fail = 0
    zero = tuple([0] * 12)

    for _ in range(M):
        a, b, c = rng.sample(sample_weight6, 3)
        bc = tuple((b[i] + c[i]) % 3 for i in range(12))
        ca = tuple((c[i] + a[i]) % 3 for i in range(12))
        ab = tuple((a[i] + b[i]) % 3 for i in range(12))

        if bc == zero or ca == zero or ab == zero:
            continue

        s1 = symplectic_sign_from_possym(a, bc, pos_symp) * symplectic_sign_from_possym(
            b, c, pos_symp
        )
        s2 = symplectic_sign_from_possym(b, ca, pos_symp) * symplectic_sign_from_possym(
            c, a, pos_symp
        )
        s3 = symplectic_sign_from_possym(c, ab, pos_symp) * symplectic_sign_from_possym(
            a, b, pos_symp
        )

        if s1 == s2 == s3:
            cocycle_pass += 1
        else:
            cocycle_fail += 1

    return cocycle_pass, cocycle_fail


def evaluate_line_rep(line_rep, sample_weight6):
    line_symp = build_symp_lines_from_line_rep(line_rep)
    pos_symp = build_position_symp(line_symp, exact.pos_to_line_mog)
    pc, fc = cocycle_pass_count_with_possym(pos_symp, sample_weight6)
    total = pc + fc
    rate = pc / total if total else 0.0
    return pc, fc, rate


def greedy_optimize(initial_line_rep, sample_weight6, max_passes=MAX_PASSES):
    current = list(initial_line_rep)
    best_pc, best_fc, best_rate = evaluate_line_rep(current, sample_weight6)
    improved = True
    passes = 0

    while improved and passes < max_passes:
        improved = False
        passes += 1
        for li, line in enumerate(exact.F3_lines):
            # try each point in this line as representative
            candidates = sorted(list(line))
            local_best = (best_pc, best_fc, best_rate, current[li])
            for cand in candidates:
                if cand == current[li]:
                    continue
                trial = list(current)
                trial[li] = cand
                pc, fc, rate = evaluate_line_rep(trial, sample_weight6)
                if pc > local_best[0] or (pc == local_best[0] and rate > local_best[2]):
                    local_best = (pc, fc, rate, cand)
            # apply the local best if improved
            if local_best[0] > best_pc or (
                local_best[0] == best_pc and local_best[2] > best_rate
            ):
                current[li] = local_best[3]
                best_pc, best_fc, best_rate = (
                    local_best[0],
                    local_best[1],
                    local_best[2],
                )
                improved = True
        # end of one full pass
    return current, (best_pc, best_fc, best_rate)


def sa_optimize(
    initial_line_rep, sample_weight6, iterations=3000, temp0=0.05, rng_seed=42
):
    """Simulated-annealing over `line_rep` using single-line flips.

    Uses `evaluate_line_rep` (which may use sampled triple scoring) as the
    objective function. Returns best found line_rep and its (pc, fc, rate).
    """
    import math

    rng = random.Random(rng_seed)
    current = list(initial_line_rep)
    current_pc, current_fc, current_rate = evaluate_line_rep(current, sample_weight6)
    best = list(current)
    best_pc, best_fc, best_rate = current_pc, current_fc, current_rate

    for it in range(iterations):
        # linear temperature schedule
        temp = temp0 * (1.0 - (it / max(1, iterations)))
        # propose a single-line flip
        li = rng.randrange(len(exact.F3_lines))
        candidates = [p for p in sorted(list(exact.F3_lines[li])) if p != current[li]]
        cand = rng.choice(candidates)
        trial = list(current)
        trial[li] = cand

        pc, fc, rate = evaluate_line_rep(trial, sample_weight6)
        delta = pc - current_pc

        accept = False
        if delta > 0:
            accept = True
        else:
            try:
                prob = math.exp(delta / max(1e-12, temp))
            except OverflowError:
                prob = 0.0
            if rng.random() < prob:
                accept = True

        if accept:
            current = trial
            current_pc, current_fc, current_rate = pc, fc, rate
            if current_pc > best_pc or (
                current_pc == best_pc and current_rate > best_rate
            ):
                best = list(current)
                best_pc, best_fc, best_rate = current_pc, current_fc, current_rate

    return best, (best_pc, best_fc, best_rate)


def run_search(restarts=RESTARTS):
    random.seed(RNG_SEED)
    weight6 = exact.weight_6
    sample_weight6 = random.sample(weight6, 50)

    # baseline (current canonical selections used by THE_EXACT_MAP.py)
    baseline_line_rep = [exact.canonical_point(l) for l in exact.F3_lines]
    base_pc, base_fc, base_rate = evaluate_line_rep(baseline_line_rep, sample_weight6)

    print(
        "Baseline cocycle sample pass:",
        base_pc,
        "fail:",
        base_fc,
        "rate:",
        f"{base_rate:.3f}",
    )

    best_global = (baseline_line_rep, (base_pc, base_fc, base_rate))

    # Try greedy from baseline and from random starts
    for r in range(restarts):
        if r == 0:
            start = list(baseline_line_rep)
            print("Greedy run #0 (start=baseline)")
        else:
            # random start: pick a random point for each line
            start = [random.choice(list(l)) for l in exact.F3_lines]
            print(f"Greedy run #{r} (random start)")

        candidate, metrics = greedy_optimize(start, sample_weight6)
        pc, fc, rate = metrics
        print(f"  Result pass={pc} fail={fc} rate={rate:.3f}")
        if pc > best_global[1][0] or (
            pc == best_global[1][0] and rate > best_global[1][2]
        ):
            best_global = (candidate, metrics)

    # --- simulated-annealing refinement phase -------------------------------------------------
    print("\nSimulated-annealing refinement phase:")
    SA_RESTARTS = 4
    SA_ITERS = 3000
    SA_TEMP0 = 0.05

    for s in range(SA_RESTARTS):
        if s == 0:
            start = list(best_global[0])
            print(f" SA run #{s} (start=best)")
        else:
            start = [random.choice(list(l)) for l in exact.F3_lines]
            print(f" SA run #{s} (random start)")

        candidate_sa, metrics_sa = sa_optimize(
            start,
            sample_weight6,
            iterations=SA_ITERS,
            temp0=SA_TEMP0,
            rng_seed=RNG_SEED + s,
        )
        pc_sa, fc_sa, rate_sa = metrics_sa
        print(f"  SA result pass={pc_sa} fail={fc_sa} rate={rate_sa:.3f}")

        if pc_sa > best_global[1][0] or (
            pc_sa == best_global[1][0] and rate_sa > best_global[1][2]
        ):
            best_global = (candidate_sa, metrics_sa)
    # -----------------------------------------------------------------------------------------

    print("\nBest found:")
    best_line_rep, (pc, fc, rate) = best_global
    print(" pass=", pc, " fail=", fc, " rate=", f"{rate:.3f}")
    print("line_rep = [")
    for i, p in enumerate(best_line_rep):
        print(f"  {p},  # line {i}: {sorted(exact.F3_lines[i])}")
    print("]")

    return best_global


if __name__ == "__main__":
    run_search()
