"""
Explore numeric decompositions of the 323 "correction" (196883 - 196560).
Search for small integer linear combinations of meaningful basis dimensions
that equal 323, and report compact decompositions that are likely meaningful
in the W33/Albert/Leech/Monster context.

Run: python scripts/explore_323_decompositions.py
"""

from itertools import product

TARGET = 323
# Candidate basis numbers drawn from repository context and previous notes
BASIS = [1, 3, 8, 10, 16, 27, 40, 80, 81, 242, 486, 728]
LABELS = [
    "1",
    "3",
    "Octonion(8)",
    "SO10(10)",
    "spinor16",
    "Albert27",
    "W33(40)",
    "80",
    "3^4=81",
    "center242",
    "quotient486",
    "s12=728",
]

solutions = []

# Search for combinations with small integer coefficients (-5..5)
RANGE = range(0, 6)  # allow only non-negative coefficients to keep results small

# Try combinations of up to 4 non-zero basis elements to keep search small
n = len(BASIS)
for r in range(1, 5):
    # choose r indices (combinatorially via product with most coefficients zero)
    # brute force over coefficient vectors with exactly r non-zero entries
    indices = list(range(n))

    def search_recursive(start, chosen, coeffs_left):
        if coeffs_left == 0:
            coef = [0] * n
            for idx, c in chosen:
                coef[idx] = c
            s = sum(coef[i] * BASIS[i] for i in range(n))
            if s == TARGET:
                terms = [f"{coef[i]}×{LABELS[i]}" for i in range(n) if coef[i] != 0]
                solutions.append((coef, terms))
            return
        for i in range(start, n):
            for c in RANGE:
                if c == 0:
                    continue
                search_recursive(i + 1, chosen + [(i, c)], coeffs_left - 1)

    search_recursive(0, [], r)

# Add some known algebraic decompositions explicitly
known = [
    ("242 + 81", [("center242", 1), ("3^4", 1)]),
    ("3×81 + 80", [("3^4", 3), ("80", 1)]),
    ("27×12 - 1", [("Albert27×12", 1), ("-1", -1)]),
    ("17×19", [("17", 1), ("19", 1)]),
]

print("Exploring decompositions of 323 (target) from candidate basis:\n")
print(", ".join(f"{LABELS[i]}={BASIS[i]}" for i in range(len(BASIS))))
print("\nFound exact decompositions (non-negative small-coefficient search):\n")
if solutions:
    for coef, terms in solutions:
        print(" + ".join(terms))
else:
    print("(none found with up to 4 terms and coefficients 1..5)")

print("\nKnown/interesting algebraic decompositions:")
for desc, parts in known:
    print(f" - {desc}: ", end="")
    s = 0
    for name, c in parts:
        if isinstance(name, str) and name.startswith("Albert"):
            val = 27 * 12
        elif name == "3^4":
            val = 81
        elif name == "center242":
            val = 242
        elif name == "80":
            val = 80
        elif name == "17":
            val = 17
        elif name == "19":
            val = 19
        elif name == "-1":
            val = -1
        else:
            val = 0
        s += c * val
        print(
            f"{c}×{name}",
            end=(" + " if parts.index((name, c)) < len(parts) - 1 else ""),
        )
    print(f" = {s}")

# Additional targeted checks (small integer relations)
print("\nTargeted relations to highlight: \n")
relations = [
    ("323 = 242 + 81", 242 + 81),
    ("323 = 3×81 + 80", 3 * 81 + 80),
    ("323 = 40×8 + 3", 40 * 8 + 3),
    ("323 = 27×12 - 1", 27 * 12 - 1),
    ("323 = 17×19", 17 * 19),
]
for desc, val in relations:
    print(f"{desc} -> {val}  (matches={val==TARGET})")

# Output short summary file
with open("outputs/323_decompositions.txt", "w") as f:
    f.write("Decomposition search for 323\n")
    f.write("\nFound (non-negative small coefficients, up to 4 terms):\n")
    if solutions:
        for coef, terms in solutions:
            f.write(" + ".join(terms) + "\n")
    else:
        f.write("(none)\n")
    f.write("\nKnown decompositions:\n")
    for desc, parts in known:
        f.write(desc + "\n")

print("\nWrote summary to outputs/323_decompositions.txt")
