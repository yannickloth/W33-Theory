#!/usr/bin/env python3
"""
ICOSIAN_BIJECTION_ATTACK.py
============================

GOAL: Construct explicit bijection W33 edges (240) ↔ E8 roots (240)
using the icosian decomposition E8 = 2 × 600-cell.

KEY INSIGHT from Marcelis:
- 240 E8 roots = 2 × 120 icosians = ±{120 icosians}
- Icosians are quaternions with golden ratio coordinates
- Binary icosahedral group 2I has 120 elements

STRATEGY:
1. Build the 120 icosians explicitly
2. Build W33 correctly (40 vertices, 240 edges)
3. Find the map: W33 edge → E8 root
"""

import math
from collections import defaultdict
from itertools import combinations, permutations

import numpy as np

# Golden ratio
PHI = (1 + math.sqrt(5)) / 2  # φ ≈ 1.618
PSI = (1 - math.sqrt(5)) / 2  # ψ = 1 - φ = -1/φ ≈ -0.618

print("=" * 80)
print("ICOSIAN BIJECTION ATTACK: W33 ↔ E8")
print("=" * 80)

# =============================================================================
# PART 1: BUILD THE 120 ICOSIANS
# =============================================================================

print("\n" + "=" * 80)
print("PART 1: THE 120 ICOSIANS (Binary Icosahedral Group 2I)")
print("=" * 80)


def build_icosians():
    """
    Build the 120 icosians as quaternions (a, b, c, d).

    The icosians form the binary icosahedral group 2I ≅ SL(2,5).
    They are the vertices of the 600-cell.

    Three types:
    1. 8 quaternion units: ±1, ±i, ±j, ±k
    2. 16 half-integer quaternions: ½(±1 ± i ± j ± k)
    3. 96 "golden" quaternions involving φ and 1/φ
    """
    icosians = []

    # Type 1: 8 quaternion units
    # (±1, 0, 0, 0) and permutations
    for sign in [1, -1]:
        for i in range(4):
            q = [0, 0, 0, 0]
            q[i] = sign
            icosians.append(tuple(q))

    # Type 2: 16 half-integer quaternions
    # ½(±1 ± i ± j ± k)
    for s0 in [1, -1]:
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                for s3 in [1, -1]:
                    q = (0.5 * s0, 0.5 * s1, 0.5 * s2, 0.5 * s3)
                    icosians.append(q)

    # Type 3: 96 golden quaternions
    # These have the form ½(0, ±1, ±φ, ±1/φ) and even permutations
    # where φ = golden ratio, 1/φ = φ - 1

    phi = PHI
    psi = 1 / PHI  # = φ - 1 = 1/φ

    # The 96 golden icosians come from:
    # ½(0, ±1, ±φ, ±ψ) where ψ = 1/φ
    # with all even permutations of the last 3 coordinates

    base_values = [0, 1, phi, psi]

    # Generate all even permutations of (1, φ, 1/φ) with signs
    def even_permutations(lst):
        """Return even permutations of a list."""
        if len(lst) == 3:
            a, b, c = lst
            return [(a, b, c), (b, c, a), (c, a, b)]
        return []

    for s1 in [1, -1]:
        for s2 in [1, -1]:
            for s3 in [1, -1]:
                # Base: (0, ±1, ±φ, ±1/φ)
                vals = [s1 * 1, s2 * phi, s3 * psi]
                for perm in even_permutations(vals):
                    # First coordinate is 0
                    q = (0, 0.5 * perm[0], 0.5 * perm[1], 0.5 * perm[2])
                    icosians.append(q)
                    # First coordinate is also permuted (full even permutations of 4 elements)

    # Actually, let me use the standard construction more carefully
    # The 600-cell vertices in standard form

    icosians = []  # Reset

    # Group 1: 8 vertices of form (±1, 0, 0, 0) and permutations
    for i in range(4):
        for s in [1, -1]:
            v = [0, 0, 0, 0]
            v[i] = s
            icosians.append(tuple(v))

    # Group 2: 16 vertices of form ½(±1, ±1, ±1, ±1)
    for s0 in [1, -1]:
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                for s3 in [1, -1]:
                    icosians.append((0.5 * s0, 0.5 * s1, 0.5 * s2, 0.5 * s3))

    # Group 3: 96 vertices involving golden ratio
    # Form: ½(0, ±1, ±φ, ±1/φ) with all EVEN permutations
    phi = PHI
    tau = 1 / PHI  # τ = 1/φ = φ - 1

    # Even permutations of 4 elements (indices)
    even_perms_4 = [
        (0, 1, 2, 3),
        (0, 2, 3, 1),
        (0, 3, 1, 2),
        (1, 0, 3, 2),
        (1, 2, 0, 3),
        (1, 3, 2, 0),
        (2, 0, 1, 3),
        (2, 1, 3, 0),
        (2, 3, 0, 1),
        (3, 0, 2, 1),
        (3, 1, 0, 2),
        (3, 2, 1, 0),
    ]

    # Base values: (0, 1, φ, τ) with signs on last 3
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            for s3 in [1, -1]:
                base = [0, s1 * 1, s2 * phi, s3 * tau]
                for perm in even_perms_4:
                    v = tuple(0.5 * base[perm[i]] for i in range(4))
                    icosians.append(v)

    # Remove duplicates (due to possible symmetry overlap)
    unique_icosians = []
    seen = set()
    for ico in icosians:
        # Round for comparison
        key = tuple(round(x, 8) for x in ico)
        if key not in seen:
            seen.add(key)
            unique_icosians.append(ico)

    return unique_icosians


icosians = build_icosians()
print(f"Number of icosians built: {len(icosians)}")

# Verify norms (all should be 1 for unit quaternions)
norms = [sum(x**2 for x in q) ** 0.5 for q in icosians]
print(f"All norms = 1? {all(abs(n - 1) < 1e-10 for n in norms)}")

# =============================================================================
# PART 2: BUILD E8 ROOTS FROM ICOSIANS
# =============================================================================

print("\n" + "=" * 80)
print("PART 2: E8 ROOTS = 2 × ICOSIANS")
print("=" * 80)


def build_e8_roots_standard():
    """Build the 240 E8 roots using the standard construction."""
    roots = []

    # Type 1: 112 integer-type roots
    # All permutations of (±1, ±1, 0, 0, 0, 0, 0, 0)
    for i in range(8):
        for j in range(i + 1, 8):
            for si in [1, -1]:
                for sj in [1, -1]:
                    root = [0] * 8
                    root[i] = si
                    root[j] = sj
                    roots.append(tuple(root))

    # Type 2: 128 half-integer roots
    # (±½, ±½, ±½, ±½, ±½, ±½, ±½, ±½) with even number of minus signs
    for mask in range(256):
        signs = [(mask >> i) & 1 for i in range(8)]
        if sum(signs) % 2 == 0:  # even number of minus signs
            root = tuple(0.5 if s == 0 else -0.5 for s in signs)
            roots.append(root)

    return roots


e8_roots = build_e8_roots_standard()
print(f"Number of E8 roots: {len(e8_roots)}")

# Verify they all have norm² = 2
norms_sq = [sum(x**2 for x in r) for r in e8_roots]
print(f"All norms² = 2? {all(abs(n - 2) < 1e-10 for n in norms_sq)}")

# =============================================================================
# PART 3: BUILD W33 CORRECTLY
# =============================================================================

print("\n" + "=" * 80)
print("PART 3: W33 = SRG(40, 12, 2, 4) via ORTHOGONAL adjacency")
print("=" * 80)


def build_w33():
    """
    Build W33: the symplectic polar graph Sp(4, GF(3)).

    Vertices: 40 isotropic lines in GF(3)^4
    Edges: pairs of ORTHOGONAL isotropic lines (ω(v,w) = 0)

    This gives exactly 240 edges.
    """
    from itertools import product

    # Symplectic form ω on GF(3)^4: ω(v, w) = v₀w₁ - v₁w₀ + v₂w₃ - v₃w₂
    def symplectic_form(v, w):
        return (v[0] * w[1] - v[1] * w[0] + v[2] * w[3] - v[3] * w[2]) % 3

    # Find all nonzero vectors
    vectors = [v for v in product(range(3), repeat=4) if v != (0, 0, 0, 0)]

    # Find isotropic vectors: ω(v, v) = 0 (automatically true for symplectic)
    # Actually need: vectors on isotropic lines
    # An isotropic line is span of v where ω(v,v) = 0
    # For symplectic form, ω(v,v) = 0 always, so all lines are isotropic

    # Find representative for each projective line
    def normalize_line(v):
        """Return canonical representative of the projective line [v]."""
        for i in range(4):
            if v[i] != 0:
                inv = pow(v[i], -1, 3) if v[i] != 0 else 0
                # Actually in GF(3): 1^(-1)=1, 2^(-1)=2
                inv_map = {1: 1, 2: 2}
                inv = inv_map.get(v[i], 0)
                return tuple((v[j] * inv) % 3 for j in range(4))
        return v

    # Get all projective lines
    lines = set()
    for v in vectors:
        lines.add(normalize_line(v))

    lines = list(lines)
    print(f"Number of projective lines (vertices): {len(lines)}")

    # Build adjacency: two lines are adjacent if they are ORTHOGONAL
    # Lines L1 = [v] and L2 = [w] are orthogonal if ω(v, w) = 0
    edges = []
    adjacency = defaultdict(set)

    for i, L1 in enumerate(lines):
        for j, L2 in enumerate(lines):
            if i < j:
                # Check orthogonality
                if symplectic_form(L1, L2) == 0:
                    edges.append((i, j))
                    adjacency[i].add(j)
                    adjacency[j].add(i)

    print(f"Number of edges: {len(edges)}")

    # Verify SRG parameters
    degrees = [len(adjacency[i]) for i in range(len(lines))]
    print(f"Degree of each vertex: {set(degrees)}")

    return lines, edges, adjacency


lines, edges, adjacency = build_w33()

# Verify SRG(40, 12, 2, 4) parameters
n = len(lines)
k = len(adjacency[0])
print(f"\nVerifying SRG parameters:")
print(f"n = {n} (should be 40)")
print(f"k = {k} (should be 12)")

# Check λ (common neighbors for adjacent pairs)
lambdas = []
for i, j in edges[:20]:  # Sample
    common = len(adjacency[i] & adjacency[j])
    lambdas.append(common)
print(f"λ = {set(lambdas)} (should be {2})")

# Check μ (common neighbors for non-adjacent pairs)
mus = []
for i in range(min(10, n)):
    for j in range(i + 1, min(20, n)):
        if j not in adjacency[i]:
            common = len(adjacency[i] & adjacency[j])
            mus.append(common)
print(f"μ = {set(mus)} (should be {4})")

# =============================================================================
# PART 4: THE CRITICAL INSIGHT - LOOK FOR STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("PART 4: SEEKING THE BIJECTION STRUCTURE")
print("=" * 80)

print(
    """
KEY OBSERVATION:
- W33 has 40 vertices, 240 edges
- E8 has 240 roots
- E8 = 2 × 600-cell = 2 × 120 icosians

QUESTION: What structure in W33 corresponds to the "2 ×" in E8?

HYPOTHESIS 1: The 40 W33 vertices might split as 40 = 20 + 20
             corresponding to the two 600-cells.

HYPOTHESIS 2: Each W33 edge (an orthogonal pair of lines) might
             naturally map to an E8 root via some algebraic operation.

HYPOTHESIS 3: The symplectic form on GF(3)^4 might "lift" to
             a quadratic form on R^8 giving E8 structure.
"""
)

# Let's investigate the vertex structure
print("\n--- Investigating W33 Vertex Structure ---")

# The 40 vertices are lines in GF(3)^4
# Let's look at their coordinates
print(f"\nFirst 10 W33 vertices (isotropic lines):")
for i, L in enumerate(lines[:10]):
    print(f"  v_{i}: {L}")

# =============================================================================
# PART 5: ATTEMPT A COORDINATE-BASED MAP
# =============================================================================

print("\n" + "=" * 80)
print("PART 5: COORDINATE-BASED BIJECTION ATTEMPT")
print("=" * 80)

print(
    """
IDEA: Map GF(3) → {-1, 0, 1} and extend to R^8

For a W33 edge (L1, L2) where L1, L2 are orthogonal lines:
- L1 = (a, b, c, d) in GF(3)^4
- L2 = (e, f, g, h) in GF(3)^4

Map to R^8 as: (a-1, b-1, c-1, d-1, e-1, f-1, g-1, h-1)
             or some normalized version.

Actually, let's try: concatenate and normalize!
"""
)


def gf3_to_real(x):
    """Map GF(3) element to {-1, 0, 1}."""
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:  # x == 2
        return -1


def line_to_r4(L):
    """Map a GF(3)^4 line representative to R^4."""
    return tuple(gf3_to_real(x) for x in L)


# Try mapping edges to R^8 by concatenation
print("\nAttempt: Edge → R^8 by concatenation")
print("-" * 50)

edge_vectors = []
for i, (v1_idx, v2_idx) in enumerate(edges[:20]):
    L1 = lines[v1_idx]
    L2 = lines[v2_idx]

    r1 = line_to_r4(L1)
    r2 = line_to_r4(L2)

    # Concatenate to R^8
    r8 = r1 + r2
    norm_sq = sum(x**2 for x in r8)

    edge_vectors.append(r8)

    if i < 5:
        print(f"Edge {i}: {L1} ⊥ {L2}")
        print(f"  → R^8: {r8}, ||v||² = {norm_sq}")

# Check what norms we get
all_norms_sq = []
for v1_idx, v2_idx in edges:
    L1 = lines[v1_idx]
    L2 = lines[v2_idx]
    r1 = line_to_r4(L1)
    r2 = line_to_r4(L2)
    r8 = r1 + r2
    norm_sq = sum(x**2 for x in r8)
    all_norms_sq.append(norm_sq)

print(f"\nNorm² distribution of edge vectors:")
from collections import Counter

norm_dist = Counter(all_norms_sq)
for norm_sq, count in sorted(norm_dist.items()):
    print(f"  ||v||² = {norm_sq}: {count} edges")

# =============================================================================
# PART 6: DEEPER STRUCTURE - THE D4 TRIALITY CONNECTION
# =============================================================================

print("\n" + "=" * 80)
print("PART 6: THE D4 TRIALITY INSIGHT")
print("=" * 80)

print(
    """
CRUCIAL INSIGHT: D4 has TRIALITY!

D4 root system has:
- 24 roots
- Triality: three 8-dimensional representations

E8 contains D4 × D4:
- 240 = 24 + 24 + 192 (decomposition under D4 × D4)
- But also: 240 = 112 + 128 (integer + half-integer)

W33 might encode the TRIALITY structure:
- 40 vertices could relate to 40 = 24 + 16 = D4 roots + something
- Or 40 = 8 × 5 (related to 5-cell in Marcelis's discussion)

Let's check: 40 = |D5 roots| / 2?
D5 has 40 roots! But we showed D5 graph ≠ W33.

HOWEVER: The 40 W33 vertices might STILL be D5 roots
         just with a DIFFERENT adjacency!
"""
)


# Build D5 roots for comparison
def build_d5_roots():
    """Build the 40 roots of D5."""
    roots = []
    for i in range(5):
        for j in range(i + 1, 5):
            for si in [1, -1]:
                for sj in [1, -1]:
                    root = [0] * 5
                    root[i] = si
                    root[j] = sj
                    roots.append(tuple(root))
    return roots


d5_roots = build_d5_roots()
print(f"\nD5 has {len(d5_roots)} roots")

# =============================================================================
# PART 7: THE SYMPLECTIC → QUADRATIC FORM LIFT
# =============================================================================

print("\n" + "=" * 80)
print("PART 7: SYMPLECTIC → QUADRATIC FORM LIFT")
print("=" * 80)

print(
    """
THE KEY THEORETICAL INSIGHT:

A symplectic form ω on GF(3)^4 can be "lifted" to a quadratic form Q on R^8.

The E8 lattice is defined by a quadratic form!

CONSTRUCTION:
1. GF(3)^4 with symplectic form ω
2. "Complexify": Consider GF(3)^4 as GF(9)^2 (since GF(9) = GF(3)[i])
3. Lift to C^2 → R^4
4. Double: R^4 → R^8 (real + imaginary parts)

This should give E8!

The map: GF(3)^4 → R^8 should be:
- Preserve the symplectic/orthogonality structure
- Map isotropic lines to E8 root-like objects
"""
)

# Let's try a more sophisticated map using roots of unity
print("\nAttempt: Use cube roots of unity for GF(3) → C")

omega = np.exp(2j * np.pi / 3)  # ω = primitive cube root of unity
omega_bar = np.exp(-2j * np.pi / 3)  # ω̄ = conjugate


def gf3_to_complex(x):
    """Map GF(3) → complex plane using cube root of unity."""
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:  # x == 2
        return omega  # or could use omega_bar


# Map W33 vertex to C^4 then R^8
def line_to_c4(L):
    """Map GF(3)^4 line to C^4."""
    return tuple(gf3_to_complex(x) for x in L)


def c4_to_r8(c4):
    """Unpack C^4 to R^8 as (Re, Im) pairs."""
    r8 = []
    for z in c4:
        r8.append(z.real)
        r8.append(z.imag)
    return tuple(r8)


print("\nMapping W33 vertices via cube root of unity:")
for i, L in enumerate(lines[:5]):
    c4 = line_to_c4(L)
    r8 = c4_to_r8(c4)
    norm_sq = sum(x**2 for x in r8)
    print(f"  v_{i}: GF(3)^4 {L} → R^8 norm² = {norm_sq:.4f}")

# =============================================================================
# PART 8: THE ULTIMATE STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("PART 8: THE ULTIMATE STRUCTURE - EDGE PAIRING INSIGHT")
print("=" * 80)

print(
    """
FUNDAMENTAL REALIZATION:

W33 edge = pair of orthogonal isotropic lines (L1, L2)
E8 root = single vector in R^8

The bijection must encode BOTH lines into ONE root.

NATURAL CANDIDATES:
1. L1 ⊕ L2 (direct sum) - but this gives R^8 naturally!
2. L1 ⊗ L2 (tensor) - gives 16-dim, too big
3. L1 ∧ L2 (wedge) - gives 6-dim (Plücker embedding)
4. Some algebraic combination using symplectic structure

THE PLÜCKER INSIGHT:
Two lines in P^3 can be encoded as a point in P^5 (Plücker coordinates).
For orthogonal lines under symplectic form, this is special!

THE 6 ⊂ 8 EMBEDDING:
P^5 has 6 homogeneous coordinates.
If we extend to 8 coordinates appropriately, we get E8 territory!
"""
)


# Compute Plücker coordinates for pairs of orthogonal lines
def plucker_coordinates(L1, L2):
    """
    Compute Plücker coordinates for the pair of lines L1, L2.

    Plücker coords for a line through points p, q in P^3 are:
    (p0*q1 - p1*q0, p0*q2 - p2*q0, p0*q3 - p3*q0,
     p1*q2 - p2*q1, p1*q3 - p3*q1, p2*q3 - p3*q2)

    Here L1, L2 are projective points (lines through origin).
    Let's use them as vectors and compute their "meet" somehow.
    """
    # For two points in P^3, Plücker gives the line through them
    # But we have two LINES (points in P^3), not a line

    # Alternative: exterior product
    # L1 ∧ L2 in ∧²(GF(3)^4) has dimension C(4,2) = 6

    p01 = (L1[0] * L2[1] - L1[1] * L2[0]) % 3
    p02 = (L1[0] * L2[2] - L1[2] * L2[0]) % 3
    p03 = (L1[0] * L2[3] - L1[3] * L2[0]) % 3
    p12 = (L1[1] * L2[2] - L1[2] * L2[1]) % 3
    p13 = (L1[1] * L2[3] - L1[3] * L2[1]) % 3
    p23 = (L1[2] * L2[3] - L1[3] * L2[2]) % 3

    return (p01, p02, p03, p12, p13, p23)


print("\nPlücker coordinates (∧² structure) for first 10 edges:")
plucker_vectors = []
for i, (v1_idx, v2_idx) in enumerate(edges[:10]):
    L1 = lines[v1_idx]
    L2 = lines[v2_idx]
    plucker = plucker_coordinates(L1, L2)
    plucker_vectors.append(plucker)
    print(f"  Edge {i}: {L1} ∧ {L2} = {plucker}")

# Count distinct Plücker coordinates
all_plucker = []
for v1_idx, v2_idx in edges:
    L1 = lines[v1_idx]
    L2 = lines[v2_idx]
    plucker = plucker_coordinates(L1, L2)
    all_plucker.append(plucker)

unique_plucker = set(all_plucker)
print(f"\nNumber of distinct Plücker vectors: {len(unique_plucker)}")
print(f"(out of 240 edges)")

# =============================================================================
# PART 9: THE BREAKTHROUGH ATTEMPT
# =============================================================================

print("\n" + "=" * 80)
print("PART 9: BREAKTHROUGH - COMBINING BOTH LINES")
print("=" * 80)

print(
    """
NEW APPROACH:

For edge (L1, L2) where L1 ⊥ L2:
- Embed L1 in first 4 coords of R^8
- Embed L2 in last 4 coords of R^8
- Apply suitable transformation to land on E8 roots

The transformation should use the ORTHOGONALITY constraint!

Since L1 ⊥ L2 (symplectic orthogonal), we have:
ω(L1, L2) = L1[0]*L2[1] - L1[1]*L2[0] + L1[2]*L2[3] - L1[3]*L2[2] = 0

This constraint should map to the E8 root constraint!
"""
)


# Build direct concatenation map with proper scaling
def edge_to_r8_direct(L1, L2):
    """Map edge (L1, L2) to R^8 by direct embedding with scaling."""
    r1 = [gf3_to_real(x) for x in L1]
    r2 = [gf3_to_real(x) for x in L2]

    # Concatenate and scale to have norm² = 2 (E8 root norm)
    r8 = r1 + r2
    current_norm_sq = sum(x**2 for x in r8)

    if current_norm_sq > 0:
        scale = (2 / current_norm_sq) ** 0.5
        r8_scaled = tuple(x * scale for x in r8)
        return r8_scaled
    return tuple(r8)


# Compute all scaled edge vectors
print("\nScaled edge vectors (targeting ||v||² = 2):")
scaled_edge_vectors = []
for i, (v1_idx, v2_idx) in enumerate(edges):
    L1 = lines[v1_idx]
    L2 = lines[v2_idx]
    r8 = edge_to_r8_direct(L1, L2)
    scaled_edge_vectors.append(r8)

    if i < 5:
        norm_sq = sum(x**2 for x in r8)
        print(f"  Edge {i}: {L1}, {L2}")
        print(f"    → R^8 (scaled): norm² = {norm_sq:.6f}")
        print(f"    → Vector: {tuple(round(x, 4) for x in r8)}")


# Check if these match E8 roots
def find_closest_e8_root(v):
    """Find the E8 root closest to vector v."""
    min_dist = float("inf")
    closest = None
    for root in e8_roots:
        dist = sum((v[i] - root[i]) ** 2 for i in range(8)) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = root
    return closest, min_dist


print("\nChecking if scaled edge vectors are close to E8 roots:")
close_count = 0
exact_count = 0
for i, v in enumerate(scaled_edge_vectors[:20]):
    closest, dist = find_closest_e8_root(v)
    if dist < 0.01:
        exact_count += 1
    if dist < 0.5:
        close_count += 1
    if i < 5:
        print(f"  Edge {i}: distance to nearest E8 root = {dist:.6f}")

print(f"\nOut of first 20 edges: {exact_count} exact, {close_count} close")

# =============================================================================
# PART 10: FINAL ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("PART 10: ANALYSIS AND NEXT STEPS")
print("=" * 80)

# Analyze the structure of the edge vectors we created
print("\nAnalyzing the 240 edge vectors we constructed:")
print("-" * 50)

# What are the possible coordinate values?
all_coords = []
for v in scaled_edge_vectors:
    all_coords.extend(v)

unique_coords = sorted(set(round(x, 6) for x in all_coords))
print(f"Unique coordinate values: {len(unique_coords)}")
print(f"Sample values: {unique_coords[:10]}...")

# Check inner products
print("\nInner product structure:")
inner_products = []
for i in range(min(50, len(scaled_edge_vectors))):
    for j in range(i + 1, min(50, len(scaled_edge_vectors))):
        v1 = scaled_edge_vectors[i]
        v2 = scaled_edge_vectors[j]
        ip = sum(v1[k] * v2[k] for k in range(8))
        inner_products.append(round(ip, 4))

ip_dist = Counter(inner_products)
print(f"Inner product distribution (sample):")
for ip, count in sorted(ip_dist.items())[:10]:
    print(f"  <v, w> = {ip}: {count} pairs")

print(
    """

═══════════════════════════════════════════════════════════════════════════════
CONCLUSIONS AND INSIGHTS
═══════════════════════════════════════════════════════════════════════════════

1. DIRECT CONCATENATION does NOT give E8 roots directly.
   The coordinate values from GF(3) → {-1, 0, 1} don't match E8's structure.

2. The PLÜCKER EMBEDDING gives 6D vectors, not 8D.
   Need to extend appropriately.

3. KEY INSIGHT NEEDED: The "lift" from GF(3) to R must use
   ALGEBRAIC structure, not just numerical values.

4. MOST PROMISING DIRECTION: Use the ICOSIAN structure!
   - 40 W33 vertices should map to some subset of icosian structure
   - The 240 edges should arise from pairs combining to give 240 E8 roots

5. THE GOLDEN RATIO CONNECTION:
   - Icosians involve φ (golden ratio)
   - GF(3) involves ω (cube root of unity)
   - Perhaps: GF(3)^4 → H (quaternions) using ω → something involving φ?

NEXT ATTACK: Build explicit map using Sp(4,3) → E6 Weyl group!
"""
)

print("\n" + "=" * 80)
print("ICOSIAN BIJECTION ATTACK COMPLETE")
print("=" * 80)
