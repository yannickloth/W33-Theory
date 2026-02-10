import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze
from tools.enumerate_minimal_certificates import build_reject_masks

lines, sign_field = analyze._load_sign_field(Path("artifacts/e6_f3_trilinear_map.json"))
gl = analyze._gl2_3()
sl = [m for m in gl if m[4] == 1]

for name, mats in [("hessian", sl), ("agl", gl)]:
    witnesses, reject_masks_by_witness, full_cover_mask = build_reject_masks(
        lines, sign_field, mats
    )
    # compute counts
    pts = [(x, y) for x in range(3) for y in range(3)]
    z_maps = [(az, bz) for az in (1, 2) for bz in range(3)]
    candidates = []
    for A in mats:
        for shift in pts:
            line_map = {line: analyze._map_line(A, shift, line) for line in lines}
            if set(line_map.values()) != set(lines):
                continue
            for z_map in z_maps:
                for eps in (1, -1):
                    candidates.append(((A, shift), z_map, int(eps), line_map))
    mismatch_masks_by_candidate = []
    stabilizer_indices = []
    witnesses_pairs = [(line, z) for line in lines for z in (0, 1, 2)]
    for idx, (u_map, z_map, eps, line_map) in enumerate(candidates):
        mask = 0
        for wi, (line, z) in enumerate(witnesses_pairs):
            lhs = sign_field[(line_map[line], analyze._map_z(z_map, z))]
            rhs = eps * sign_field[(line, z)]
            if lhs != rhs:
                mask |= 1 << wi
        mismatch_masks_by_candidate.append(mask)
        if mask == 0:
            stabilizer_indices.append(idx)
    non_stabilizer_indices = [
        idx for idx in range(len(candidates)) if idx not in set(stabilizer_indices)
    ]
    print(
        name,
        "candidates:",
        len(candidates),
        "stabilizers:",
        len(stabilizer_indices),
        "non-stabilizers:",
        len(non_stabilizer_indices),
        "witnesses:",
        len(witnesses),
    )
