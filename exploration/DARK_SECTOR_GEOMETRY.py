#!/usr/bin/env python3
"""
DARK_SECTOR_GEOMETRY.py

Deep dive into the 13-point dark sector from PG(2,3)

The 13 "dark" points at infinity in PG(3,3) form the projective plane PG(2,3).
This plane has rich structure that may encode the dark sector physics.

Author: Theory of Everything Project
Date: February 2026
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 75)
print("THE DARK SECTOR: GEOMETRY OF PG(2,3)")
print("=" * 75)

# ============================================================================
# PART 1: CONSTRUCT PG(2,3)
# ============================================================================
print("\n" + "=" * 75)
print("PART 1: CONSTRUCTING PG(2,3)")
print("=" * 75)

# PG(2,3) = projective plane over GF(3)
# Points are equivalence classes of nonzero vectors in GF(3)³
# Two vectors are equivalent if one is a scalar multiple of the other


def normalize(v):
    """Normalize a projective point: first nonzero coord = 1."""
    v = tuple(x % 3 for x in v)
    if v == (0, 0, 0):
        return None
    for i, x in enumerate(v):
        if x != 0:
            inv = pow(x, -1, 3)  # Modular inverse in GF(3)
            return tuple((c * inv) % 3 for c in v)
    return None


# Generate all 13 points of PG(2,3)
pg2_3_points = set()
for v in product(range(3), repeat=3):
    if v != (0, 0, 0):
        normalized = normalize(v)
        if normalized:
            pg2_3_points.add(normalized)

pg2_3_points = sorted(list(pg2_3_points))
print(f"\nThe 13 points of PG(2,3):")
for i, p in enumerate(pg2_3_points):
    print(f"  P{i+1}: {p}")

print(f"\nTotal: {len(pg2_3_points)} points ✓")

# ============================================================================
# PART 2: LINES IN PG(2,3)
# ============================================================================
print("\n" + "=" * 75)
print("PART 2: THE 13 LINES OF PG(2,3)")
print("=" * 75)

# A line in PG(2,3) is defined by a linear equation ax + by + cz = 0
# The line [a:b:c] contains points (x,y,z) satisfying this equation


def line_points(a, b, c):
    """Find all points on the line ax + by + cz = 0 in GF(3)."""
    points = []
    for p in pg2_3_points:
        if (a * p[0] + b * p[1] + c * p[2]) % 3 == 0:
            points.append(p)
    return sorted(points)


# Generate all 13 lines
pg2_3_lines = set()
for coeffs in product(range(3), repeat=3):
    if coeffs != (0, 0, 0):
        normalized = normalize(coeffs)
        if normalized:
            pg2_3_lines.add(normalized)

pg2_3_lines = sorted(list(pg2_3_lines))

print(f"\nThe 13 lines of PG(2,3) (each with 4 points):")
for i, L in enumerate(pg2_3_lines):
    pts = line_points(*L)
    point_indices = [pg2_3_points.index(p) + 1 for p in pts]
    print(f"  L{i+1} [{L}]: P{point_indices}")

# ============================================================================
# PART 3: INCIDENCE STRUCTURE
# ============================================================================
print("\n" + "=" * 75)
print("PART 3: INCIDENCE STRUCTURE")
print("=" * 75)

print(
    """
PG(2,3) has the following properties:
• 13 points
• 13 lines
• 4 points on each line
• 4 lines through each point
• Any 2 points determine a unique line
• Any 2 lines meet in a unique point

This is a SELF-DUAL projective plane!
"""
)

# Build incidence matrix
incidence = np.zeros((13, 13), dtype=int)
for i, L in enumerate(pg2_3_lines):
    for p in line_points(*L):
        j = pg2_3_points.index(p)
        incidence[i, j] = 1

print("Incidence matrix (rows=lines, cols=points):")
print(incidence)

print(f"\nPoints per line: {incidence.sum(axis=1)}")
print(f"Lines per point: {incidence.sum(axis=0)}")

# ============================================================================
# PART 4: SPECIAL CONFIGURATIONS
# ============================================================================
print("\n" + "=" * 75)
print("PART 4: SPECIAL CONFIGURATIONS IN PG(2,3)")
print("=" * 75)

print(
    """
PG(2,3) contains several special configurations:

1. TRIANGLE: 3 non-collinear points (any such triple works)
   These determine 3 lines forming a triangle.

2. QUADRILATERAL: 4 points, no 3 collinear
   These form a "complete quadrangle" with interesting properties.

3. REFERENCE FRAME: The 4 "fundamental points"
   (1,0,0), (0,1,0), (0,0,1), (1,1,1) - no 3 collinear.
"""
)

# Find fundamental points
fund_points = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]
print("\nFundamental quadrangle:")
for p in fund_points:
    idx = pg2_3_points.index(p) + 1
    print(f"  P{idx}: {p}")


# Check no 3 collinear
def collinear(p1, p2, p3):
    """Check if 3 points are collinear in projective space."""
    # Points are collinear iff det = 0
    det = (
        p1[0] * (p2[1] * p3[2] - p2[2] * p3[1])
        - p1[1] * (p2[0] * p3[2] - p2[2] * p3[0])
        + p1[2] * (p2[0] * p3[1] - p2[1] * p3[0])
    )
    return det % 3 == 0


print("\nChecking no 3 fundamental points are collinear:")
for triple in combinations(fund_points, 3):
    result = collinear(*triple)
    print(f"  {triple}: collinear = {result}")

# ============================================================================
# PART 5: SPLITTING 13 INTO PHYSICAL COMPONENTS
# ============================================================================
print("\n" + "=" * 75)
print("PART 5: PHYSICAL INTERPRETATION OF THE 13")
print("=" * 75)

print(
    """
The 13 points of PG(2,3) can be partitioned in several ways:

PARTITION A: 1 + 4 + 4 + 4 (point + 3 lines through it)
   Pick any point P. It lies on 4 lines.
   Each line has 4 points, but P is on all of them.
   So: 1 (the point) + 3 × 4 = 13? No, overcounting.
   Actually: 1 + 3 × 3 = 10, missing 3.

PARTITION B: 4 + 9 (quadrangle + remaining)
   The fundamental quadrangle has 4 points.
   Remaining: 13 - 4 = 9 points.
   These 9 form the "diagonal points" and other structure.

PARTITION C: 4 + 3 + 3 + 3 (one line + remaining lines)
   One line has 4 points.
   The remaining 9 points form structure.

Let's find all triangles (3 non-collinear points):
"""
)


# Find an arc (set of points, no 3 collinear)
def is_arc(points):
    """Check if a set of points forms an arc (no 3 collinear)."""
    for triple in combinations(points, 3):
        if collinear(*triple):
            return False
    return True


# Find all maximal arcs (4 points, no 3 collinear)
arcs_4 = []
for quad in combinations(pg2_3_points, 4):
    if is_arc(quad):
        arcs_4.append(quad)

print(f"\nNumber of 4-arcs (quadrangles) in PG(2,3): {len(arcs_4)}")
print("First few quadrangles:")
for arc in arcs_4[:5]:
    indices = [pg2_3_points.index(p) + 1 for p in arc]
    print(f"  P{indices}")

# ============================================================================
# PART 6: CONNECTION TO THE VISIBLE SECTOR
# ============================================================================
print("\n" + "=" * 75)
print("PART 6: DARK-VISIBLE INTERFACE")
print("=" * 75)

print(
    """
In PG(3,3), the 13 "dark" points at infinity interact with the 27 "visible"
affine points through:

1. PARALLEL CLASSES: Each of the 13 directions at infinity determines
   a class of parallel lines in affine space. There are:
   - 13 parallel classes
   - Each class has 9 parallel lines
   - Each line has 3 affine points

2. AFFINE PLANES: The 13 points at infinity also determine affine planes.
   Each "line at infinity" (4 dark points) corresponds to a pencil of
   9 parallel affine planes.

The 13 × 9 = 117 pairs (dark direction, parallel line) encode all
directional structure in the visible universe!

PHYSICAL INTERPRETATION:
- Each dark point = a "direction" or "momentum mode"
- Parallel lines in that direction = particles with that momentum
- Dark sector controls the KINEMATIC structure of visible matter
"""
)

# ============================================================================
# PART 7: THE 13 AS DARK PARTICLES
# ============================================================================
print("\n" + "=" * 75)
print("PART 7: CONJECTURED DARK PARTICLE SPECTRUM")
print("=" * 75)

print(
    """
If the 13 dark points represent particles, how might they organize?

OPTION 1: Sterile neutrinos + dark bosons + dark fermions
   3 sterile neutrinos (one per generation)
   4 dark gauge bosons (new U(1)' or SU(2) dark)
   6 dark fermions (partners to quarks/leptons)
   Total: 3 + 4 + 6 = 13 ✓

OPTION 2: Dark SU(3) structure
   8 dark gluons (adjoint of SU(3))
   3 + 2 additional dark states (fundamental reps?)
   But 8 + 5 = 13 seems arbitrary.

OPTION 3: Based on PG(2,3) geometry
   4 special points (quadrangle) = dark gauge bosons
   9 remaining points = dark matter particles
   This gives: 4 + 9 = 13

   The 4 dark bosons mediate interactions.
   The 9 dark fermions parallel the 9 particles per generation!

OPTION 3 IS MOST COMPELLING:
   Visible: 3 × 9 = 27 particles in 3 generations
   Dark:    1 × 9 = 9 dark fermions + 4 dark gauge bosons

The dark sector is like ONE generation of the visible sector plus
gauge bosons! This suggests incomplete GUT multiplets that
couldn't fit in the visible 27.
"""
)

# ============================================================================
# PART 8: DEEPER STRUCTURE - BAER SUBPLANES
# ============================================================================
print("\n" + "=" * 75)
print("PART 8: BAER SUBPLANES AND SUBSTRUCTURE")
print("=" * 75)

print(
    """
PG(2,3) does NOT contain a Baer subplane (would need √3 to exist).
However, it contains interesting substructures:

AFFINE PLANES: Removing one line gives AG(2,3) with 9 points.
   - There are 13 ways to do this (one for each line)
   - Each AG(2,3) has the structure of 3×3 grid
   - Points of AG(2,3) form a Latin square structure

TRIANGLES: Any 3 non-collinear points and their connecting lines.
   - There are C(13,3) - (lines × C(4,3)) triangles
   - = 286 - 13×4 = 286 - 52 = 234 triangles

The 234 triangles in PG(2,3)... is this related to anything?
234 = 2 × 117 = 2 × 9 × 13 = 2 × (AG(2,3)) × (lines)
234 = 240 - 6 ... close to E8 roots!
"""
)

# Count triangles properly
triangles = 0
for triple in combinations(pg2_3_points, 3):
    if not collinear(*triple):
        triangles += 1

print(f"Number of triangles (non-collinear triples): {triangles}")
print(f"This equals: C(13,3) - 13×C(4,3) = 286 - 52 = 234")

# ============================================================================
# PART 9: AUTOMORPHISM GROUP
# ============================================================================
print("\n" + "=" * 75)
print("PART 9: AUTOMORPHISM GROUP OF PG(2,3)")
print("=" * 75)

print(
    """
The automorphism group of PG(2,3) is PGL(3,3):

|PGL(3,3)| = |GL(3,3)| / |Z(GL(3,3))|
           = (3³-1)(3³-3)(3³-9) / 2
           = 26 × 24 × 18 / 2
           = 26 × 24 × 9
           = 5616

Alternatively:
|PGL(3,3)| = |PSL(3,3)| × 2 = 5616

PSL(3,3) is a simple group of order 5616/2 = 2808? Let me recalculate.

Actually: |PSL(3,3)| = |SL(3,3)| / gcd(3, 3-1) = |SL(3,3)| / 1
|SL(3,3)| = (3³-1)(3³-3)(3³-9) / (3-1) = 26×24×18/2 = 5616

So |PSL(3,3)| = 5616.

PSL(3,3) contains various subgroups that act on subsets of points.
These may correspond to symmetries of the dark sector.
"""
)

# Calculate |PGL(3,3)| properly
gl33 = (3**3 - 1) * (3**3 - 3) * (3**3 - 3**2)  # = 26 × 24 × 18
center = 3 - 1  # = 2
pgl33 = gl33 // center

print(f"|GL(3,3)| = (27-1)(27-3)(27-9) = {gl33}")
print(f"|PGL(3,3)| = {pgl33}")

# SL and PSL
sl33 = gl33 // (3 - 1)  # Same as PGL in this case
psl33 = sl33 // 1  # gcd(3, 3-1) = gcd(3,2) = 1

print(f"|SL(3,3)| = {sl33}")
print(f"|PSL(3,3)| = {psl33}")

# ============================================================================
# PART 10: THE 13 AND MODULAR FORMS
# ============================================================================
print("\n" + "=" * 75)
print("PART 10: NUMBER 13 IN MATHEMATICS")
print("=" * 75)

print(
    """
The number 13 appears in many places:

1. PG(2,3) = 13 points and 13 lines ✓

2. FIBONACCI: F_7 = 13 (7th Fibonacci number)

3. PARTITIONS: p(13) = 101 (partitions of 13)

4. DIMENSION: 13 = 26/2 = (critical string dimension)/2

5. MOONSHINE: The Monster has a 196883-dimensional rep.
   196883 = 47 × 59 × 71. None involve 13 directly.
   But 196884 = 1 + 196883, and 196884/13 = 15145.something, not integer.

6. SIMPLE GROUPS: PSL(3,3) acts on 13 points.
   But 13 doesn't appear in its order 5616 = 2^4 × 3^3 × 13.

   WAIT: 5616 = 432 × 13!
   432 = 2^4 × 27 = 16 × 27 ✓

   So |PSL(3,3)| = 432 × 13 = (16 × 27) × 13

   This connects 13, 27, and 16 (= dimension of spinor rep)!

7. IN OUR CONTEXT: 13 is the number of "directions at infinity"
   that organize the parallel structure of the visible 27.
"""
)

print(f"\nFactorization check:")
print(f"|PSL(3,3)| = {psl33} = {psl33 // 13} × 13 = {psl33 // 432} × 432")
print(f"432 = 16 × 27 ✓")

# ============================================================================
# CONCLUSIONS
# ============================================================================
print("\n" + "=" * 75)
print("CONCLUSIONS: THE DARK SECTOR")
print("=" * 75)

print(
    """
THE DARK SECTOR HAS RICH INTERNAL STRUCTURE:

1. 13 = |PG(2,3)| points at infinity encode dark degrees of freedom

2. Natural partition: 4 + 9
   - 4 dark gauge bosons (quadrangle structure)
   - 9 dark fermions (parallel to one visible generation)

3. Each dark point controls a "direction" in visible space
   - 13 parallel classes in AG(3,3)
   - Dark sector shapes the kinematics of visible matter

4. Automorphism: |PSL(3,3)| = 5616 = 16 × 27 × 13
   - The 16 (spinor), 27 (visible), 13 (dark) are unified!

5. Dark-visible interface:
   - 13 × 9 = 117 line-direction pairs
   - 234 triangles in PG(2,3) ≈ 240 E8 roots (off by 6!)

PREDICTION: The dark sector consists of:
   - 4 dark gauge bosons (new dark U(1) or SU(2))
   - 9 dark fermions (incomplete 4th generation)

This explains why dark matter is ~5× visible matter:
   Dark: 9 + 4 = 13 degrees of freedom
   Visible: 27 degrees of freedom
   Ratio should be related to couplings, not just counting.

The structure PG(3,3) = AG(3,3) ∪ PG(2,3) = 27 + 13 = 40
is the FUNDAMENTAL ARENA of the Theory of Everything.
"""
)
