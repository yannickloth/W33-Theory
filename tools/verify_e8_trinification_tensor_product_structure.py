#!/usr/bin/env python3
"""
Verify the *tensor-product factorization* in the standard E8→E6×A2 (trinification) grading.

We already have, for each E8 root α, metadata fields:
  - grade ∈ {g0_e6, g0_a2, g1, g2} with counts 72,6,81,81
  - i27 ∈ {0..26} for g1/g2 (which 27-weight index)
  - i3  ∈ {0,1,2} for g1/g2 (which SU(3) color/weight index)

In the canonical decomposition:
  e8 ≅ (e6 ⊕ sl3) ⊕ (27⊗3) ⊕ (27*⊗3*)

we expect:
  - sl3 roots act on g1/g2 by changing i3 but preserving i27
  - e6 roots act on g1/g2 by changing i27 but preserving i3
  - (e6) and (sl3) commute inside grade-0 (no root sums between them)
  - g1+g2→g0: outputs split cleanly into (e6) vs (sl3) channels with predictable
    “which index stays fixed” behavior:
      • output in sl3: i27 matches, i3 changes
      • output in e6:  i3 matches, i27 changes

This script checks those constraints purely from root addition on the 240 roots.

Inputs:
  - artifacts/e8_root_metadata_table.json

Outputs:
  - artifacts/e8_trinification_tensor_product_structure.json
  - artifacts/e8_trinification_tensor_product_structure.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
OUT_JSON = ROOT / "artifacts" / "e8_trinification_tensor_product_structure.json"
OUT_MD = ROOT / "artifacts" / "e8_trinification_tensor_product_structure.md"


Root = Tuple[int, ...]  # 8-tuple in E8 simple-root coeff basis


def _write_json(path: Path, obj: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _add(a: Root, b: Root) -> Root:
    return tuple(a[i] + b[i] for i in range(8))


def main() -> None:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta["rows"]

    root_to_row: Dict[Root, dict] = {}
    for r in rows:
        root = tuple(int(x) for x in r["root_orbit"])
        root_to_row[root] = r
    if len(root_to_row) != 240:
        raise RuntimeError("Expected 240 distinct roots")

    def grade_of(root: Root) -> str:
        return str(root_to_row[root]["grade"])

    def i27_of(root: Root) -> int | None:
        v = root_to_row[root]["i27"]
        return None if v is None else int(v)

    def i3_of(root: Root) -> int | None:
        v = root_to_row[root]["i3"]
        return None if v is None else int(v)

    roots_e6 = [rt for rt in root_to_row if grade_of(rt) == "g0_e6"]
    roots_a2 = [rt for rt in root_to_row if grade_of(rt) == "g0_a2"]
    roots_g1 = [rt for rt in root_to_row if grade_of(rt) == "g1"]
    roots_g2 = [rt for rt in root_to_row if grade_of(rt) == "g2"]

    # 1) Check [e6, a2] = 0 at the root level: no sums are roots.
    commute_sum_count = 0
    commute_examples: List[Dict[str, object]] = []
    root_set = set(root_to_row.keys())
    for a in roots_e6:
        for b in roots_a2:
            if _add(a, b) in root_set:
                commute_sum_count += 1
                if len(commute_examples) < 5:
                    commute_examples.append(
                        {"e6": list(a), "a2": list(b), "sum": list(_add(a, b))}
                    )

    # 2) sl3 action on g1/g2 preserves i27 and moves i3.
    su3_action: Dict[str, Dict[str, object]] = {}
    su3_violations: List[Dict[str, object]] = []

    for s in roots_a2:
        m_g1: Counter[Tuple[int, int]] = Counter()
        m_g2: Counter[Tuple[int, int]] = Counter()
        i27_ok = True
        g1_total = 0
        g2_total = 0

        for x in roots_g1:
            y = _add(s, x)
            if y not in root_set:
                continue
            g1_total += 1
            if grade_of(y) != "g1":
                su3_violations.append(
                    {
                        "where": "g1",
                        "su3_root": list(s),
                        "x": list(x),
                        "y": list(y),
                        "want_grade": "g1",
                        "got_grade": grade_of(y),
                    }
                )
                continue
            if i27_of(x) != i27_of(y):
                i27_ok = False
                if len(su3_violations) < 10:
                    su3_violations.append(
                        {
                            "where": "g1",
                            "su3_root": list(s),
                            "x": list(x),
                            "y": list(y),
                            "reason": "i27_changed",
                        }
                    )
            sx = i3_of(x)
            sy = i3_of(y)
            if sx is None or sy is None:
                su3_violations.append(
                    {
                        "where": "g1",
                        "su3_root": list(s),
                        "x": list(x),
                        "y": list(y),
                        "reason": "missing_i3",
                    }
                )
            else:
                m_g1[(sx, sy)] += 1

        for x in roots_g2:
            y = _add(s, x)
            if y not in root_set:
                continue
            g2_total += 1
            if grade_of(y) != "g2":
                su3_violations.append(
                    {
                        "where": "g2",
                        "su3_root": list(s),
                        "x": list(x),
                        "y": list(y),
                        "want_grade": "g2",
                        "got_grade": grade_of(y),
                    }
                )
                continue
            if i27_of(x) != i27_of(y):
                i27_ok = False
                if len(su3_violations) < 10:
                    su3_violations.append(
                        {
                            "where": "g2",
                            "su3_root": list(s),
                            "x": list(x),
                            "y": list(y),
                            "reason": "i27_changed",
                        }
                    )
            sx = i3_of(x)
            sy = i3_of(y)
            if sx is None or sy is None:
                su3_violations.append(
                    {
                        "where": "g2",
                        "su3_root": list(s),
                        "x": list(x),
                        "y": list(y),
                        "reason": "missing_i3",
                    }
                )
            else:
                m_g2[(sx, sy)] += 1

        su3_action[str(list(s))] = {
            "g1_total_transitions": g1_total,
            "g2_total_transitions": g2_total,
            "g1_i3_map_counts": {
                f"{a}->{b}": int(c) for (a, b), c in sorted(m_g1.items())
            },
            "g2_i3_map_counts": {
                f"{a}->{b}": int(c) for (a, b), c in sorted(m_g2.items())
            },
            "i27_preserved": bool(i27_ok),
        }

    # 3) e6 action on g1/g2 preserves i3 and moves i27.
    e6_violations: List[Dict[str, object]] = []
    e6_i3_preserved_ok = True
    e6_transitions_total = 0
    for e in roots_e6:
        for x in roots_g1:
            y = _add(e, x)
            if y not in root_set:
                continue
            e6_transitions_total += 1
            if grade_of(y) != "g1":
                e6_i3_preserved_ok = False
                if len(e6_violations) < 10:
                    e6_violations.append(
                        {
                            "where": "g1",
                            "e6_root": list(e),
                            "x": list(x),
                            "y": list(y),
                            "want_grade": "g1",
                            "got_grade": grade_of(y),
                        }
                    )
                continue
            if i3_of(x) != i3_of(y):
                e6_i3_preserved_ok = False
                if len(e6_violations) < 10:
                    e6_violations.append(
                        {
                            "where": "g1",
                            "e6_root": list(e),
                            "x": list(x),
                            "y": list(y),
                            "reason": "i3_changed",
                        }
                    )
        for x in roots_g2:
            y = _add(e, x)
            if y not in root_set:
                continue
            e6_transitions_total += 1
            if grade_of(y) != "g2":
                e6_i3_preserved_ok = False
                if len(e6_violations) < 10:
                    e6_violations.append(
                        {
                            "where": "g2",
                            "e6_root": list(e),
                            "x": list(x),
                            "y": list(y),
                            "want_grade": "g2",
                            "got_grade": grade_of(y),
                        }
                    )
                continue
            if i3_of(x) != i3_of(y):
                e6_i3_preserved_ok = False
                if len(e6_violations) < 10:
                    e6_violations.append(
                        {
                            "where": "g2",
                            "e6_root": list(e),
                            "x": list(x),
                            "y": list(y),
                            "reason": "i3_changed",
                        }
                    )

    # 4) Mixed bracket target splits (g1+g2→g0_e6 or g0_a2) and the right index stays fixed.
    mixed_counts = Counter()
    mixed_rule_ok = True
    mixed_violations: List[Dict[str, object]] = []
    for x in roots_g1:
        for y in roots_g2:
            z = _add(x, y)
            if z not in root_set:
                continue
            gz = grade_of(z)
            mixed_counts[gz] += 1
            if gz == "g0_a2":
                # su3 output: expect same i27
                if i27_of(x) != i27_of(y):
                    mixed_rule_ok = False
                    if len(mixed_violations) < 10:
                        mixed_violations.append(
                            {
                                "kind": "g0_a2",
                                "x": list(x),
                                "y": list(y),
                                "z": list(z),
                                "reason": "i27_mismatch",
                            }
                        )
            elif gz == "g0_e6":
                # e6 output: expect same i3
                if i3_of(x) != i3_of(y):
                    mixed_rule_ok = False
                    if len(mixed_violations) < 10:
                        mixed_violations.append(
                            {
                                "kind": "g0_e6",
                                "x": list(x),
                                "y": list(y),
                                "z": list(z),
                                "reason": "i3_mismatch",
                            }
                        )
            else:
                mixed_rule_ok = False
                if len(mixed_violations) < 10:
                    mixed_violations.append(
                        {
                            "kind": "unexpected_output_grade",
                            "x": list(x),
                            "y": list(y),
                            "z": list(z),
                            "grade": gz,
                        }
                    )

    out: Dict[str, object] = {
        "status": (
            "ok"
            if (
                commute_sum_count == 0
                and not su3_violations
                and e6_i3_preserved_ok
                and mixed_rule_ok
            )
            else "fail"
        ),
        "counts": {
            "roots": 240,
            "g0_e6": len(roots_e6),
            "g0_a2": len(roots_a2),
            "g1": len(roots_g1),
            "g2": len(roots_g2),
        },
        "checks": {
            "no_root_sums_between_g0_e6_and_g0_a2": commute_sum_count == 0,
            "su3_action_preserves_i27": all(
                v["i27_preserved"] for v in su3_action.values()
            ),
            "e6_action_preserves_i3": bool(e6_i3_preserved_ok),
            "g1_plus_g2_output_rule": bool(mixed_rule_ok),
        },
        "g0_commutation": {
            "sum_root_count": commute_sum_count,
            "examples": commute_examples,
        },
        "su3_root_action": su3_action,
        "su3_violations": su3_violations[:10],
        "e6_action": {
            "total_transitions_checked": e6_transitions_total,
            "violations": e6_violations[:10],
        },
        "g1_plus_g2_to_g0": {
            "output_grade_counts": {k: int(v) for k, v in mixed_counts.items()},
            "rule_ok": bool(mixed_rule_ok),
            "violations": mixed_violations[:10],
        },
    }

    _write_json(OUT_JSON, out)

    md: List[str] = []
    md.append("# Verify: E8 trinification tensor-product structure\n")
    md.append(f"- status: `{out['status']}`\n")
    md.append("## Counts\n")
    md.append(f"- g0_e6 roots: `{len(roots_e6)}`")
    md.append(f"- g0_a2 roots: `{len(roots_a2)}`")
    md.append(f"- g1 roots: `{len(roots_g1)}`")
    md.append(f"- g2 roots: `{len(roots_g2)}`\n")
    md.append("## Checks\n")
    for k, v in out["checks"].items():
        md.append(f"- {k}: `{v}`")
    md.append("\n## SU(3) root action (i3 transitions)\n")
    md.append(
        "- For each su3 root, the map counts should show one nonzero arrow with count 27 per grade.\n"
    )
    sample_keys = list(su3_action.keys())[:3]
    for sk in sample_keys:
        ent = su3_action[sk]
        md.append(
            f"- su3_root={sk}: g1 {ent['g1_i3_map_counts']}, g2 {ent['g2_i3_map_counts']}"
        )
    md.append(f"\n- JSON: `{OUT_JSON}`")
    _write_md(OUT_MD, md)

    print(f"status={out['status']} wrote={OUT_JSON}")
    if out["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
