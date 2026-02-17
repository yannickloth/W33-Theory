"""
Analyze all 3-fiber choices (choose 3 of the 8 non-central grades) and
classify them by simple combinatorial/projective properties.

Goal: help pick canonical `center + 3 fibers` decompositions for the
Monster 323 correction (80 + 3×81 = 323).
"""

from itertools import combinations

# Non-zero grades in F3^2 (exclude (0,0))
grades = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

# Helper: add two grades mod 3
add = lambda a, b: ((a[0] + b[0]) % 3, (a[1] + b[1]) % 3)

# All affine lines (solutions to a*x + b*y = c over F3)
lines = []
F3 = [0, 1, 2]
for a in F3:
    for b in F3:
        if a == 0 and b == 0:
            continue
        for c in F3:
            pts = []
            for x in F3:
                for y in F3:
                    if (a * x + b * y) % 3 == c:
                        pts.append((x, y))
            # store only lines that contain exactly 3 points (affine lines)
            if len(pts) == 3:
                pts_sorted = sorted(pts)
                if pts_sorted not in lines:
                    lines.append(pts_sorted)

# Filter lines that consist entirely of non-zero points
affine_lines_nonzero = [L for L in lines if all(p != (0, 0) for p in L)]

# Classify triples
triples = list(combinations(grades, 3))
results = []
for tri in triples:
    tri_set = set(tri)
    # check if triple lies on any affine line (including lines not through origin)
    on_line = any(tri_set.issubset(set(L)) for L in affine_lines_nonzero)
    # check grade-sum
    s = (
        (tri[0][0] + tri[1][0] + tri[2][0]) % 3,
        (tri[0][1] + tri[1][1] + tri[2][1]) % 3,
    )
    sum_zero = s == (0, 0)
    # check if triple contains two points that are negatives (g, -g)
    contains_neg_pair = any(
        ((g[0], g[1]) in tri_set and ((-g[0]) % 3, (-g[1]) % 3) in tri_set) for g in tri
    )
    results.append((tri, on_line, sum_zero, contains_neg_pair))

# Summarize
print("Total 3-fiber triples:", len(triples))
print("Triples that lie on an affine line (nonzero pts):")
for tri, on_line, sum_zero, neg in results:
    if on_line:
        print(" ", tri)

print("\nTriples with grade-sum = 0 (mod 3):")
for tri, on_line, sum_zero, neg in results:
    if sum_zero:
        print(" ", tri)

print("\nTriples containing a negation pair g and -g:")
for tri, on_line, sum_zero, neg in results:
    if neg:
        print(" ", tri)

# Heuristic: prefer triples that are "balanced" (sum_zero) or lie on a line
candidates = [tri for tri, on_line, sum_zero, neg in results if sum_zero or on_line]
print("\nCandidate triples (sum_zero OR on_line):", len(candidates))
for tri in candidates:
    print(" ", tri)

# Save to outputs
with open("outputs/323_fiber_triples.txt", "w") as f:
    f.write("All 3-fiber triples and classifications\n")
    for tri, on_line, sum_zero, neg in results:
        f.write(
            f"{tri} | on_line={on_line} | sum_zero={sum_zero} | contains_neg_pair={neg}\n"
        )

print("\nWrote outputs/323_fiber_triples.txt")
