from pathlib import Path

from scripts.w33_permrep_association import (
    _point_bfs_coset_reps,
    compute_suborbits_from_generators,
    parse_gap_permrep,
    schreier_stabilizer_from_coset_reps,
)

p1 = Path("data/HeG1-p2058B0.g1")
p2 = Path("data/HeG1-p2058B0.g2")
perms1 = parse_gap_permrep(p1)
perms2 = parse_gap_permrep(p2)
print("parsed perms from g1:", len(perms1))
print("parsed perms from g2:", len(perms2))
perms_both = perms1 + perms2
print("degree (len perms[0]):", len(perms_both[0]))
# BFS coset reps using only perms1
coset1 = _point_bfs_coset_reps(perms1, len(perms1[0]), base=0)
coset12 = _point_bfs_coset_reps(perms_both, len(perms_both[0]), base=0)
print("coset size with g1 only:", len(coset1))
print("coset size with g1+g2:", len(coset12))
# compute suborbits
sub1 = compute_suborbits_from_generators(perms1, base=0)
sub12 = compute_suborbits_from_generators(perms_both, base=0)
print("suborbits with g1 only:", len(sub1), [len(s) for s in sub1[:10]])
print("suborbits with g1+g2:", len(sub12), [len(s) for s in sub12])
# Schreier stabilizer sizes
h1 = schreier_stabilizer_from_coset_reps(perms1, coset1, base=0)
h12 = schreier_stabilizer_from_coset_reps(perms_both, coset12, base=0)
print("schreier Hgens sizes:", len(h1), len(h12))
