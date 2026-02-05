"""
COMPLETE_BRACKET.py - The Full Bracket on All 728 Elements

We've proven:
  - Product=2 pairs → weight-6 bracket (closure, antisymmetry ✓)
  - Product=1 pairs → weight-9 result (need to define bracket!)

Now let's complete the structure by defining brackets for ALL cases.

The goal: A bracket on 728 elements that satisfies Jacobi.
"""

import random
from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("THE COMPLETE BRACKET: Extending to All 728 Elements")
print("=" * 80)

# Setup
G = np.array(
    [
        [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 1, 2, 1, 0, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 0, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 0],
    ],
    dtype=int,
)


def generate_codewords():
    codewords = []
    for coeffs in product(range(3), repeat=6):
        c = np.array(coeffs) @ G % 3
        codewords.append(tuple(c))
    return codewords


codewords = generate_codewords()
codeword_set = set(codewords)
nonzero = [c for c in codewords if any(x != 0 for x in c)]
zero = tuple([0] * 12)


def weight(c):
    return sum(1 for x in c if x != 0)


def support(c):
    return frozenset(i for i, x in enumerate(c) if x != 0)


def neg(c):
    return tuple((3 - x) % 3 if x != 0 else 0 for x in c)


def add(c1, c2):
    return tuple((c1[i] + c2[i]) % 3 for i in range(12))


def scale(k, c):
    """Multiply codeword by scalar k in GF(3)"""
    return tuple((k * c[i]) % 3 for i in range(12))


weight_6 = [c for c in nonzero if weight(c) == 6]
weight_9 = [c for c in nonzero if weight(c) == 9]
weight_12 = [c for c in nonzero if weight(c) == 12]

hexads = set(support(c) for c in weight_6)
hexad_to_cw = defaultdict(list)
for c in weight_6:
    hexad_to_cw[support(c)].append(c)

support_9 = set(support(c) for c in weight_9)
support_to_cw9 = defaultdict(list)
for c in weight_9:
    support_to_cw9[support(c)].append(c)

print(
    f"Weight-6: {len(weight_6)}, Weight-9: {len(weight_9)}, Weight-12: {len(weight_12)}"
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 1: The Universal Bracket Definition")
print("=" * 80)

print(
    """
DEFINITION: For any two codewords c1, c2:

  [c1, c2] = sign(c1, c2) * (c1 + c2)

Where sign(c1, c2) is determined by a TOTAL ORDERING that:
  1. Gives antisymmetry: [c1, c2] = -[c2, c1]
  2. Is consistent with the code structure

The key: The sign must be chosen to make Jacobi work!
"""
)


def intersection_product(c1, c2):
    """Product of values at intersection of supports."""
    H1, H2 = support(c1), support(c2)
    inter = H1 & H2
    if not inter:
        return 0
    prod = 1
    for i in inter:
        if c1[i] != 0 and c2[i] != 0:
            prod = (prod * c1[i] * c2[i]) % 3
    return prod


# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Bracket Table by Weight Pairs")
print("=" * 80)

# What weight does [c1, c2] have for each weight combination?
print("\nAnalyzing [weight_a, weight_b] → weight_result:")

weight_pairs = defaultdict(Counter)

for c1 in nonzero[:200]:
    for c2 in nonzero[:200]:
        if c1 < c2:
            w1, w2 = weight(c1), weight(c2)
            s = add(c1, c2)
            ws = weight(s) if s != zero else 0
            weight_pairs[(w1, w2)][ws] += 1

for w1, w2 in sorted(weight_pairs.keys()):
    print(f"\n  [{w1}, {w2}]:")
    for ws, count in sorted(weight_pairs[(w1, w2)].items()):
        print(f"    → weight {ws}: {count}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 3: The Sign Function")
print("=" * 80)

print(
    """
For Jacobi to hold: [a,[b,c]] + [b,[c,a]] + [c,[a,b]] = 0

With [x,y] = sign(x,y) * (x+y), we need:

  sign(a, b+c)*(a+b+c) + sign(b, c+a)*(a+b+c) + sign(c, a+b)*(a+b+c) = 0

This means: sign(a, b+c) + sign(b, c+a) + sign(c, a+b) ≡ 0 (mod 3)

If signs are ±1, we need them to sum to 0 mod 3.
Three values from {-1, +1} sum to ±1 or ±3.
±3 ≡ 0 (mod 3)!

So we need: all three signs equal (all +1 or all -1).

This is a COCYCLE CONDITION on the sign function!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Testing Lexicographic Sign")
print("=" * 80)


def bracket_lex(c1, c2):
    """Bracket with lexicographic sign."""
    if c1 == c2:
        return zero
    s = add(c1, c2)
    if c1 < c2:
        return s
    else:
        return neg(s)


# Test Jacobi with lex sign
print("\nTesting Jacobi with lexicographic sign:")
jacobi_pass = 0
jacobi_fail = 0
fail_examples = []

random.seed(42)
sample = random.sample(nonzero, min(80, len(nonzero)))

for a in sample[:25]:
    for b in sample[:25]:
        for c in sample[:25]:
            if a != b and b != c and a != c:
                bc = bracket_lex(b, c)
                ca = bracket_lex(c, a)
                ab = bracket_lex(a, b)

                a_bc = bracket_lex(a, bc) if bc != zero else zero
                b_ca = bracket_lex(b, ca) if ca != zero else zero
                c_ab = bracket_lex(c, ab) if ab != zero else zero

                jacobi_sum = add(add(a_bc, b_ca), c_ab)

                if jacobi_sum == zero:
                    jacobi_pass += 1
                else:
                    jacobi_fail += 1
                    if len(fail_examples) < 3:
                        fail_examples.append((a, b, c, jacobi_sum))

print(f"  Jacobi pass: {jacobi_pass}")
print(f"  Jacobi fail: {jacobi_fail}")
if jacobi_fail > 0:
    print(f"  Pass rate: {jacobi_pass / (jacobi_pass + jacobi_fail):.2%}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 5: The Support-Based Sign")
print("=" * 80)

print(
    """
Try a sign based on SUPPORTS rather than full codewords.

Idea: sign(c1, c2) depends only on supp(c1) and supp(c2).

For weight-6 pairs with |∩|=3, we used:
  sign = +1 if min(H1-H2) < min(H2-H1), else -1

Let's generalize this.
"""
)


def support_sign(c1, c2):
    """Sign based on support comparison."""
    H1, H2 = support(c1), support(c2)

    # Compare by symmetric difference parts
    only_H1 = H1 - H2
    only_H2 = H2 - H1

    if not only_H1 and not only_H2:
        # Same support - use values
        return 1 if c1 < c2 else -1

    if not only_H1:
        return 1  # H1 ⊂ H2
    if not only_H2:
        return -1  # H2 ⊂ H1

    # Compare min elements
    if min(only_H1) < min(only_H2):
        return 1
    else:
        return -1


def bracket_supp(c1, c2):
    """Bracket with support-based sign."""
    if c1 == c2:
        return zero
    s = add(c1, c2)
    sign = support_sign(c1, c2)
    if sign == 1:
        return s
    else:
        return neg(s)


print("\nTesting Jacobi with support-based sign:")
jacobi_pass = 0
jacobi_fail = 0

for a in sample[:25]:
    for b in sample[:25]:
        for c in sample[:25]:
            if a != b and b != c and a != c:
                bc = bracket_supp(b, c)
                ca = bracket_supp(c, a)
                ab = bracket_supp(a, b)

                a_bc = bracket_supp(a, bc) if bc != zero else zero
                b_ca = bracket_supp(b, ca) if ca != zero else zero
                c_ab = bracket_supp(c, ab) if ab != zero else zero

                jacobi_sum = add(add(a_bc, b_ca), c_ab)

                if jacobi_sum == zero:
                    jacobi_pass += 1
                else:
                    jacobi_fail += 1

print(f"  Jacobi pass: {jacobi_pass}")
print(f"  Jacobi fail: {jacobi_fail}")
if jacobi_fail > 0:
    print(f"  Pass rate: {jacobi_pass / (jacobi_pass + jacobi_fail):.2%}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 6: Analyzing Jacobi Failures")
print("=" * 80)

print(
    """
Let's understand WHY Jacobi fails.

For [a,[b,c]] + [b,[c,a]] + [c,[a,b]] = 0:

With addition-based bracket, the UNSIGNED sum is:
  (a + (b+c)) + (b + (c+a)) + (c + (a+b))
  = a + b + c + b + c + a + c + a + b
  = 3(a + b + c)
  = 0 in GF(3) ✓

So the unsigned part ALWAYS satisfies Jacobi!
The failure comes from SIGN inconsistency.
"""
)

# Check the sign pattern in failures
print("\nAnalyzing sign patterns in Jacobi failures:")

sign_patterns = Counter()

for a in sample[:20]:
    for b in sample[:20]:
        for c in sample[:20]:
            if a != b and b != c and a != c:
                # Get intermediate codewords
                bc = add(b, c)
                ca = add(c, a)
                ab = add(a, b)

                if bc == zero or ca == zero or ab == zero:
                    continue

                # Get signs
                s_bc = support_sign(b, c)
                s_ca = support_sign(c, a)
                s_ab = support_sign(a, b)

                s_a_bc = support_sign(a, bc)
                s_b_ca = support_sign(b, ca)
                s_c_ab = support_sign(c, ab)

                # Total signs for each term
                sign_a_bc = s_a_bc * s_bc  # sign([a, [b,c]])
                sign_b_ca = s_b_ca * s_ca
                sign_c_ab = s_c_ab * s_ab

                pattern = (sign_a_bc, sign_b_ca, sign_c_ab)
                sign_patterns[pattern] += 1

print("\nSign patterns (s1, s2, s3):")
for pattern, count in sorted(sign_patterns.items(), key=lambda x: -x[1]):
    total = sum(pattern)
    jacobi_ok = "✓ Jacobi" if total % 3 == 0 else "✗ Fails"
    print(f"  {pattern}: {count} occurrences, sum={total} {jacobi_ok}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 7: The Cocycle Condition")
print("=" * 80)

print(
    """
For Jacobi: sign(a,bc)*sign(b,c) + sign(b,ca)*sign(c,a) + sign(c,ab)*sign(a,b) ≡ 0 (mod 3)

With signs in {+1, -1}, the only way to get sum ≡ 0 is:
  - All three products equal +1: sum = 3 ≡ 0 ✓
  - All three products equal -1: sum = -3 ≡ 0 ✓

So we need: sign(a,bc)*sign(b,c) = sign(b,ca)*sign(c,a) = sign(c,ab)*sign(a,b)

This is a 2-COCYCLE condition!

The sign function must be a 2-cocycle with values in {±1}.
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 8: Searching for a Good Sign Function")
print("=" * 80)

print(
    """
Let's try a sign based on a QUADRATIC FORM.

Define: sign(c1, c2) = (-1)^{q(c1, c2)}

where q is some bilinear form on codewords.

A natural candidate: q(c1, c2) = sum over positions of c1[i]*c2[i]
"""
)


def quadratic_sign(c1, c2):
    """Sign based on inner product."""
    inner = sum(c1[i] * c2[i] for i in range(12)) % 3
    if inner == 0:
        # Orthogonal - use lex tiebreaker
        return 1 if c1 < c2 else -1
    elif inner == 1:
        return 1
    else:  # inner == 2
        return -1


def bracket_quad(c1, c2):
    """Bracket with quadratic sign."""
    if c1 == c2:
        return zero
    s = add(c1, c2)
    sign = quadratic_sign(c1, c2)
    if sign == 1:
        return s
    else:
        return neg(s)


print("\nTesting Jacobi with quadratic sign:")
jacobi_pass = 0
jacobi_fail = 0

for a in sample[:25]:
    for b in sample[:25]:
        for c in sample[:25]:
            if a != b and b != c and a != c:
                bc = bracket_quad(b, c)
                ca = bracket_quad(c, a)
                ab = bracket_quad(a, b)

                a_bc = bracket_quad(a, bc) if bc != zero else zero
                b_ca = bracket_quad(b, ca) if ca != zero else zero
                c_ab = bracket_quad(c, ab) if ab != zero else zero

                jacobi_sum = add(add(a_bc, b_ca), c_ab)

                if jacobi_sum == zero:
                    jacobi_pass += 1
                else:
                    jacobi_fail += 1

print(f"  Jacobi pass: {jacobi_pass}")
print(f"  Jacobi fail: {jacobi_fail}")
if jacobi_fail > 0:
    print(f"  Pass rate: {jacobi_pass / (jacobi_pass + jacobi_fail):.2%}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 9: The Trivial Sign (All +1)")
print("=" * 80)

print(
    """
What if sign(c1, c2) = +1 for all pairs?

Then [c1, c2] = c1 + c2 (just addition).
This is NOT antisymmetric: [c1, c2] = [c2, c1] ≠ -[c2, c1] in general.

BUT: If we quotient by the equivalence c ~ -c (projective code),
then antisymmetry becomes: [c1, c2] ~ -[c2, c1] = [c2, c1]
which is just symmetry!

So on the PROJECTIVE ternary Golay code (364 elements = 728/2),
the bracket [c1, c2] = c1 + c2 might give a JORDAN algebra!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 10: Testing the Jordan Identity")
print("=" * 80)

print(
    """
Jordan algebras satisfy: (x·y)·x² = x·(y·x²)

For our bracket x·y = x + y:
  (x·y)·x² = (x+y) + 2x = 3x + y = y (in GF(3))
  x·(y·x²) = x + (y + 2x) = 3x + y = y (in GF(3))

These are EQUAL! So addition trivially satisfies Jordan identity.

But we can define a more interesting product:
  x * y = x + y if x ≠ ±y
  x * x = 2x = -x
  x * (-x) = 0

Let's test this.
"""
)


def jordan_product(c1, c2):
    """Jordan-like product."""
    if c1 == c2:
        return neg(c1)  # x * x = -x
    if c1 == neg(c2):
        return zero  # x * (-x) = 0
    return add(c1, c2)


# Test Jordan identity: (a*b)*a² = a*(b*a²)
print("\nTesting Jordan identity (a*b)*a² = a*(b*a²):")
jordan_pass = 0
jordan_fail = 0

for a in sample[:30]:
    for b in sample[:30]:
        if a != b and a != neg(b):
            # a² = a * a = -a
            a_sq = jordan_product(a, a)

            # (a*b)*a²
            ab = jordan_product(a, b)
            lhs = jordan_product(ab, a_sq)

            # a*(b*a²)
            b_asq = jordan_product(b, a_sq)
            rhs = jordan_product(a, b_asq)

            if lhs == rhs:
                jordan_pass += 1
            else:
                jordan_fail += 1

print(f"  Jordan pass: {jordan_pass}")
print(f"  Jordan fail: {jordan_fail}")
if jordan_pass + jordan_fail > 0:
    print(f"  Pass rate: {jordan_pass / (jordan_pass + jordan_fail):.2%}")

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS")
print("=" * 80)

print(
    """
FINDINGS:

1. Simple addition-based brackets fail Jacobi due to sign issues.

2. The unsigned sum ALWAYS satisfies Jacobi (= 0 in GF(3)).

3. The sign function must satisfy a 2-COCYCLE condition.

4. Finding the right sign function is the key remaining problem.

5. On the projective code (mod ±1), addition gives a Jordan algebra.

INSIGHT: The 728-element structure might be:
  - A PROJECTIVE representation of sl(27)
  - Or a CENTRAL EXTENSION with Z/3Z kernel
  - The sign encodes the extension class

The 264 weight-6 codewords with our hexad bracket form
a PARTIAL Lie algebra. Completing to 728 requires understanding
the cohomological structure.
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)

print(
    """
To crack the full structure:

1. Compute H²(V, Z/3Z) where V is the code as abelian group
   - This classifies central extensions
   - The Golay code has special cohomology

2. Find the sign function satisfying the 2-cocycle condition
   - May relate to the Steiner system geometry
   - Or to the Mathieu group action

3. Alternatively, work with PROJECTIVE bracket:
   - Identify c with -c (364 elements)
   - Bracket becomes symmetric (Jordan-like)
   - May relate to exceptional Jordan algebra J₃(O)

The connection to sl(27) is through the 27-dimensional
representation of E6, and the exceptional Jordan algebra.

27 = dim of exceptional Jordan algebra J₃(O)!
"""
)
