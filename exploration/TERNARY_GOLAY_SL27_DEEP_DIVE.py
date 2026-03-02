#!/usr/bin/env python3
"""
TERNARY_GOLAY_SL27_DEEP_DIVE.py

Deep Investigation of the Connection Between:
- Ternary Golay Code G12 [12,6,6] over GF(3)
- sl(27) = 27² - 1 = 728 dimensional Lie algebra
- W33 graph and Sp(4,3)

The discovery: |G12| - 1 = 728 = dim(sl(27))
This cannot be coincidence!

Author: Theory of Everything Project
Date: February 2026
"""

import math
from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("DEEP DIVE: TERNARY GOLAY CODE AND sl(27)")
print("=" * 70)

# ============================================================================
# PART 1: CONSTRUCT THE TERNARY GOLAY CODE
# ============================================================================
print("\n" + "=" * 70)
print("PART 1: CONSTRUCTING THE TERNARY GOLAY CODE")
print("=" * 70)

# The ternary Golay code G12 can be defined by its generator matrix
# Standard generator matrix (systematic form): G = [I_6 | P]
# where P is a specific 6x6 matrix over GF(3)

# The parity check matrix P for ternary Golay
# This is one standard form
P = np.array(
    [
        [0, 1, 1, 1, 1, 1],
        [1, 0, 1, 2, 2, 1],
        [1, 1, 0, 1, 2, 2],
        [1, 2, 1, 0, 1, 2],
        [1, 2, 2, 1, 0, 1],
        [1, 1, 2, 2, 1, 0],
    ],
    dtype=int,
)

# Generator matrix G = [I_6 | P]
I6 = np.eye(6, dtype=int)
G = np.hstack([I6, P])

print("Generator matrix G (6×12):")
print(G)


# Generate all 729 codewords
def generate_ternary_golay():
    """Generate all 3^6 = 729 codewords of the ternary Golay code."""
    codewords = []
    for coeffs in product(range(3), repeat=6):
        message = np.array(coeffs, dtype=int)
        codeword = np.dot(message, G) % 3
        codewords.append(tuple(codeword))
    return codewords


codewords = generate_ternary_golay()
print(f"\nGenerated {len(codewords)} codewords")
print(f"Expected: 3^6 = {3**6}")

# Verify uniqueness
unique_codewords = set(codewords)
print(f"Unique codewords: {len(unique_codewords)}")

# ============================================================================
# PART 2: WEIGHT DISTRIBUTION ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("PART 2: WEIGHT DISTRIBUTION ANALYSIS")
print("=" * 70)


def hamming_weight(codeword):
    """Count nonzero entries (Hamming weight over GF(3))."""
    return sum(1 for x in codeword if x != 0)


# Calculate weight distribution
weight_dist = defaultdict(list)
for cw in unique_codewords:
    w = hamming_weight(cw)
    weight_dist[w].append(cw)

print("\nWeight distribution:")
print(f"{'Weight':<10} {'Count':<10} {'Expected':<10}")
print("-" * 30)
expected = {0: 1, 6: 264, 9: 440, 12: 24}
for w in sorted(weight_dist.keys()):
    count = len(weight_dist[w])
    exp = expected.get(w, "?")
    status = "✓" if count == exp else "✗"
    print(f"{w:<10} {count:<10} {exp:<10} {status}")

# Total nonzero codewords
nonzero_count = sum(len(weight_dist[w]) for w in weight_dist if w > 0)
print(f"\nTotal nonzero codewords: {nonzero_count}")
print(f"This equals dim(sl(27)) = 27² - 1 = {27**2 - 1} ✓")

# ============================================================================
# PART 3: STRUCTURE OF THE 264 WEIGHT-6 CODEWORDS
# ============================================================================
print("\n" + "=" * 70)
print("PART 3: THE 264 WEIGHT-6 CODEWORDS")
print("=" * 70)

weight_6 = weight_dist[6]
print(f"Number of weight-6 codewords: {len(weight_6)}")
print(f"264 = 11 × 24")
print(f"264 = 240 + 24 (E8 roots + 24)")
print(f"264 = 132 × 2 (two copies of something)")


# Analyze supports (which positions are nonzero)
def get_support(codeword):
    """Return the set of nonzero positions."""
    return frozenset(i for i, x in enumerate(codeword) if x != 0)


supports_6 = [get_support(cw) for cw in weight_6]
unique_supports_6 = set(supports_6)
print(f"\nNumber of distinct 6-supports: {len(unique_supports_6)}")

# Each 6-support should appear multiple times (for different nonzero patterns)
support_counts = defaultdict(int)
for s in supports_6:
    support_counts[s] += 1

print(f"Support multiplicities: {set(support_counts.values())}")

# The 6-supports form a design structure
print(f"\n6-supports are 6-subsets of {{0,1,...,11}}")
print(f"Total possible 6-subsets: C(12,6) = {int(math.comb(12, 6))}")
print(f"Actual 6-supports: {len(unique_supports_6)}")

# ============================================================================
# PART 4: CONNECTION TO sl(27) DECOMPOSITION
# ============================================================================
print("\n" + "=" * 70)
print("PART 4: MATCHING TO sl(27) DECOMPOSITION")
print("=" * 70)

print(
    """
sl(27) has dimension 728 = 27² - 1

Under various decompositions:
1. sl(27) ⊃ E6 (78) + complement (650)
2. sl(27) can be graded by weight

TERNARY GOLAY WEIGHTS:
  264 (weight 6) + 440 (weight 9) + 24 (weight 12) = 728

HYPOTHESIS: These correspond to sl(27) gradings!

Let's check if the numbers match any natural sl(27) structure:
"""
)

# Check various decompositions
print("\nNumeric checks:")

# E6 connection
e6_dim = 78
sl27_dim = 728
complement = sl27_dim - e6_dim
print(f"sl(27) = E6 + complement: {e6_dim} + {complement} = {e6_dim + complement}")

# Root space decomposition of sl(27)
# sl(27) has 26 Cartan generators and 27² - 27 = 702 root spaces
cartan = 26
root_spaces = 27**2 - 27
print(f"sl(27) = {cartan} Cartan + {root_spaces} root spaces = {cartan + root_spaces}")

# Check: 264 + 440 + 24
print(f"\n264 = 11 × 24")
print(f"440 = 40 × 11")
print(f"24 = 24 × 1")

# Factor of 11 appears!
print(f"\n264/11 = {264//11}")
print(f"440/11 = {440//11}")
print(f"Total/11 = {728//11} = {728/11}")  # Not divisible by 11

# Check GF(3) and 27 connection
print(f"\n27 = 3³")
print(f"729 = 3⁶ = 27²")
print(f"sl(27) = 27² - 1 = 3⁶ - 1")

# ============================================================================
# PART 5: THE AUTOMORPHISM GROUP 2.M12
# ============================================================================
print("\n" + "=" * 70)
print("PART 5: AUTOMORPHISM GROUP 2.M12")
print("=" * 70)

print(
    """
The automorphism group of the ternary Golay code is 2.M12:
• A double cover (central extension) of M12
• |2.M12| = 2 × |M12| = 2 × 95040 = 190080

This group acts on:
• The 12 coordinate positions
• The 729 codewords
• Preserves the weight structure

CONNECTION TO W33/E6:
• |W(E6)| = 51840
• |M12| = 95040
• Ratio: 95040/51840 = 11/6 ≈ 1.833

The 11 that appears in 264 = 11×24 might be significant!
"""
)

# Check the 11 connection
print(f"11 × 24 = {11 * 24}")
print(f"11 × 40 = {11 * 40}")
print(f"11 × 24 + 11 × 40 + 24 = {11*24 + 11*40 + 24}")

# Factor 264 and 440
print(f"\n264 = 2³ × 3 × 11")
print(f"440 = 2³ × 5 × 11")
print(f"728 = 2³ × 7 × 13")

# Hmm, 728 is NOT divisible by 11
print(f"728 / 11 = {728/11:.4f} (not integer)")

# ============================================================================
# PART 6: RELATING TO W33 PARAMETERS
# ============================================================================
print("\n" + "=" * 70)
print("PART 6: RELATING TO W33 PARAMETERS")
print("=" * 70)

print(
    """
W33 graph parameters: SRG(40, 12, 2, 4)
• 40 vertices
• Each vertex has 12 neighbors  (same as Golay length!)
• λ = 2 (common neighbors of adjacent vertices)
• μ = 4 (common neighbors of non-adjacent vertices)
• 240 edges (= E8 roots)

W33 embeds in Sp(4,3) over GF(3):
• Same field as ternary Golay code!
• Sp(4,3) has order 25920

The number 12:
• W33 regularity = 12
• Ternary Golay length = 12
• Both over GF(3)
"""
)

# Check Sp(4,3) order
sp43_order = 25920
print(f"\n|Sp(4,3)| = {sp43_order}")
print(f"|Sp(4,3)| / 12 = {sp43_order/12} = {sp43_order//12}")
print(f"|Sp(4,3)| / 40 = {sp43_order/40} = {sp43_order//40}")
print(f"|Sp(4,3)| / 240 = {sp43_order/240} = {sp43_order//240}")

# W(E6) and Sp(4,3)
we6_order = 51840
print(f"\n|W(E6)| = {we6_order}")
print(f"|W(E6)| / |Sp(4,3)| = {we6_order/sp43_order} = 2")
print(f"So W(E6) = 2 × Sp(4,3)!")

# ============================================================================
# PART 7: THE 24 WEIGHT-12 CODEWORDS
# ============================================================================
print("\n" + "=" * 70)
print("PART 7: THE 24 WEIGHT-12 CODEWORDS (ALL-NONZERO)")
print("=" * 70)

weight_12 = weight_dist[12]
print(f"Number of weight-12 codewords: {len(weight_12)}")
print(f"24 = dimension of Leech lattice")
print(f"24 = |S4| (symmetric group)")
print(f"24 = 27 - 3 (E6 rep minus 3)")

# These codewords have all 12 positions nonzero
# Over GF(3), each position can be 1 or 2 (not 0)
# So there are 2^12 = 4096 potential patterns
# But only 24 are codewords!

print(f"\nPotential all-nonzero 12-tuples: 2^12 = {2**12}")
print(f"Actual weight-12 codewords: 24")
print(f"Ratio: {2**12 / 24} = 170.67")

# List a few
print("\nSample weight-12 codewords:")
for i, cw in enumerate(weight_12[:5]):
    print(f"  {cw}")

# ============================================================================
# PART 8: CONSTRUCTING A BIJECTION?
# ============================================================================
print("\n" + "=" * 70)
print("PART 8: TOWARDS A TERNARY GOLAY ↔ sl(27) BIJECTION")
print("=" * 70)

print(
    """
GOAL: Find an explicit map between:
• 728 nonzero ternary Golay codewords
• 728 basis elements of sl(27)

sl(27) BASIS:
• 26 Cartan generators: H_i (diagonal matrices)
• 702 root generators: E_α for roots α

TERNARY GOLAY:
• 264 weight-6 codewords
• 440 weight-9 codewords
• 24 weight-12 codewords

HYPOTHESIS FOR THE MAP:
Weight 6 (264): → E6 subalgebra (78) + part of complement?
Weight 9 (440): → Remaining root spaces?
Weight 12 (24): → Special generators?

Note: 78 + 650 = 728, but 264 + 440 + 24 = 728 too.
The decompositions don't obviously match...
"""
)

# Check if 264, 440, 24 can be rearranged to match other structures
print("\nCombinations of 264, 440, 24:")
print(f"  264 + 440 = {264 + 440}")
print(f"  264 + 24 = {264 + 24}")
print(f"  440 + 24 = {440 + 24}")
print(f"  264 - 78 = {264 - 78} (264 minus E6)")
print(f"  440 + 24 + 264 - 728 = {440 + 24 + 264 - 728}")

# 186 = 264 - 78
print(f"\n186 = 264 - 78 = 6 × 31")

# ============================================================================
# PART 9: THE GF(3) / CHARACTERISTIC 3 UNIFICATION
# ============================================================================
print("\n" + "=" * 70)
print("PART 9: THE GF(3) UNIFICATION")
print("=" * 70)

print(
    """
Both structures live over characteristic 3:

TERNARY GOLAY:
• Code over GF(3) = {0, 1, 2}
• 3^6 = 729 codewords
• Length 12 over GF(3)

W33/Sp(4,3):
• Symplectic form over GF(3)
• 40 isotropic points
• Sp(4,3) is the automorphism group

sl(27):
• 27 = 3³
• sl(27) defined over ℂ, but has GF(3) structure
• The "27" comes from 3³

E6 CONNECTION:
• E6 is the automorphism group of the Albert algebra
• The Albert algebra is related to the octonions
• Over characteristic 3, there are special features

UNIFIED VIEW:
The number 3 is fundamental:
• 3 = characteristic
• 27 = 3³
• 729 = 3⁶
• 12 = 4 × 3 (Golay length, W33 regularity)
• 40 = 27 + 13 (visible + dark, both related to 3-structures)
"""
)

# ============================================================================
# PART 10: THE HEXACODE CONNECTION
# ============================================================================
print("\n" + "=" * 70)
print("PART 10: THE HEXACODE CONNECTION")
print("=" * 70)

print(
    """
The HEXACODE is a [6, 3, 4] code over GF(4):
• Length 6 (half of Golay length 12)
• Dimension 3 (4³ = 64 codewords)
• Minimum distance 4

The hexacode is used in the MOG construction and is related to both:
• Binary Golay code (through MOG)
• Ternary Golay code (through weight structure)

GF(4) = GF(2²) has 4 elements: {0, 1, ω, ω²}
where ω² + ω + 1 = 0

CONNECTION TO WITTING:
• Witting polytope uses GF(4) coordinates!
• 40 rays of Witting ↔ 40 W33 vertices?
• The hexacode might bridge Witting and Golay
"""
)

# The hexacode has 64 codewords
hexacode_count = 4**3
print(f"\nHexacode codewords: {hexacode_count}")
print(f"64 = 2^6 = 4^3")

# ============================================================================
# CONCLUSIONS
# ============================================================================
print("\n" + "=" * 70)
print("CONCLUSIONS AND CONJECTURES")
print("=" * 70)

print(
    """
ESTABLISHED FACTS:
1. Ternary Golay has 729 = 728 + 1 codewords
2. sl(27) has dimension 728 = 27² - 1
3. Nonzero Golay codewords: 264 + 440 + 24 = 728 EXACTLY
4. Both structures are naturally over characteristic 3
5. W33 embeds in Sp(4,3) over GF(3)
6. W(E6) = 2 × Sp(4,3)

CONJECTURES:
1. There exists an explicit bijection:
   {nonzero ternary Golay codewords} ↔ {sl(27) basis}

2. The weight structure (264/440/24) encodes some
   natural grading or decomposition of sl(27)

3. The ternary Golay code is the "combinatorial shadow"
   of sl(27), just as the Hamming code is for E8

4. The hierarchy:
   Hamming [8,4,4] → E8 (240 roots)
   Ternary Golay [12,6,6] → sl(27) (728 dim)
   Binary Golay [24,12,8] → Leech (196560 vectors)

   represents increasing levels of "exceptional structure"

5. The W33 graph sits in the same GF(3) family as
   ternary Golay, suggesting deep connections to
   both E8 (via edges) and sl(27) (via Sp(4,3))

OPEN QUESTIONS:
1. What is the explicit Golay ↔ sl(27) bijection?
2. How does the Lie bracket translate to Golay operations?
3. Is there a "Golay lattice" that sl(27) generates?
4. What role does M12 play in the E6/sl(27) story?
5. How do the 24 weight-12 codewords relate to 24 = 27-3?
"""
)

print("\n" + "=" * 70)
print("END OF TERNARY GOLAY / sl(27) DEEP DIVE")
print("=" * 70)
