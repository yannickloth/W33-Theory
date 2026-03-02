\
"""
Compute the '480' count by discrete orbit-stabilizer.

Group: signed permutations on 7 imaginary units, order 2^7 * 7! = 645120.
Action: change-of-basis on the octonion imaginary basis; stabilizer elements preserve the multiplication table.

Output:
  - stabilizer size inside signed perms
  - orbit size (=645120/stabilizer), should be 480
"""

from __future__ import annotations
from itertools import permutations, product
import json, os
from typing import List, Tuple
from src.octonion import build_code_table, encode, decode

TAB = build_code_table()

def mul_code(code_i: int, code_j: int) -> int:
    si, ii = decode(code_i)
    sj, ij = decode(code_j)
    return si*sj*TAB[ii][ij]

def apply_code(code: int, perm_arr: List[int], sign_arr: List[int]) -> int:
    s, idx = decode(code)
    if idx==0:
        return code
    return s * sign_arr[idx] * encode(1, perm_arr[idx])

def is_automorphism(perm_arr: List[int], sign_arr: List[int]) -> bool:
    basis_codes = [encode(1,i) for i in range(8)]
    for i in range(8):
        for j in range(8):
            lhs = apply_code(TAB[i][j], perm_arr, sign_arr)
            rhs = mul_code(apply_code(basis_codes[i], perm_arr, sign_arr),
                           apply_code(basis_codes[j], perm_arr, sign_arr))
            if lhs != rhs:
                return False
    return True

def compute_stabilizer_and_orbit() -> Tuple[int,int]:
    perms = list(permutations(range(1,8)))
    sign_patterns = list(product([1,-1], repeat=7))
    stab = 0
    for perm in perms:
        perm_arr = [0]*8
        for i,img in enumerate(perm, start=1):
            perm_arr[i]=img
        for sp in sign_patterns:
            sign_arr = [1]*8
            for i,sg in enumerate(sp, start=1):
                sign_arr[i]=sg
            if is_automorphism(perm_arr, sign_arr):
                stab += 1
    group_order = (2**7) * 5040
    orbit = group_order // stab
    return stab, orbit

if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)

    stab, orbit = compute_stabilizer_and_orbit()
    print(f"Signed-permutation group order: {2**7 * 5040}")
    print(f"Stabilizer size: {stab}")
    print(f"Orbit size (# distinct tables): {orbit}")
    with open("out/orbit_480_result.json","w") as f:
        json.dump({"group_order": 2**7*5040, "stabilizer": stab, "orbit": orbit}, f, indent=2)

