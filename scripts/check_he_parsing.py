import os
import sys
from pathlib import Path

# ensure repo root is on sys.path when run as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.w33_permrep_association import parse_gap_permrep

p1 = Path("data/HeG1-p2058B0.g1")
p2 = Path("data/HeG1-p2058B0.g2")
perms1 = parse_gap_permrep(p1)
perms2 = parse_gap_permrep(p2)
print("parsed from g1:", len(perms1), "perm length:", len(perms1[0]))
print("parsed from g2:", len(perms2), "perm length:", len(perms2[0]))
print("g1 sample (first 16):", perms1[0][:16])
print("g2 sample (first 16):", perms2[0][:16])
print("g1 max index:", max(perms1[0]))
print("g2 max index:", max(perms2[0]))

# inspect point-BFS coset reps and H-orbits (using internal helpers)
from scripts.w33_permrep_association import (
    _point_bfs_coset_reps,
    compute_suborbits_from_generators,
    orbit_of_group_on_points,
)


n = len(perms1[0])
coset1 = _point_bfs_coset_reps(perms1, n, base=0)
coset12 = _point_bfs_coset_reps(perms1 + perms2, n, base=0)
print("coset size with g1 only:", len(coset1))
print("coset size with g1+g2:", len(coset12))
sub1 = compute_suborbits_from_generators(perms1, base=0)
sub12 = compute_suborbits_from_generators(perms1 + perms2, base=0)
print("suborbits with g1 only:", len(sub1), [len(s) for s in sub1[:10]])
print("suborbits with g1+g2:", len(sub12), [len(s) for s in sub12])

# group orbit under generators (should be transitive for a full permrep)
from scripts.w33_permrep_association import orbit_of_group_on_points

orbit = orbit_of_group_on_points(perms1 + perms2, 0)
print("group orbit size starting at 0:", len(orbit))
