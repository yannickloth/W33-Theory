#!/usr/bin/env python3
"""Build a dual positive/negative rigidity profile for global full-sign cells.

This composes:
- `tools/minimal_global_full_sign_cores.py` (negative UNSAT witnesses)
- `tools/minimal_global_identity_certificates.py` (positive SAT identity witnesses)

and reports a compact theorem-facing profile.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.minimal_global_full_sign_cores as neg
import tools.minimal_global_identity_certificates as pos


def _nontrivial_unsat_uniform_size(
    payload: Dict[str, Any], mode: str, variant: str
) -> int:
    vals = set()
    for a, b in neg.Z_MAPS:
        if (a, b) == (1, 0):
            continue
        cell = payload["matrix"][mode][f"({a},{b})"]
        if cell["status"] != "unsat":
            raise RuntimeError(f"Expected UNSAT cell for mode={mode}, z=({a},{b})")
        if variant == "unconstrained":
            vals.add(int(cell["minimal_core_size"]))
        else:
            vals.add(int(cell["variant_profiles"][variant]["minimal_core_size"]))
    if len(vals) != 1:
        raise RuntimeError(
            f"Expected uniform nontrivial core size for mode={mode}, variant={variant}, got {sorted(vals)}"
        )
    return int(next(iter(vals)))


def build_report(max_examples: int = 5, top_k: int = 8) -> Dict[str, Any]:
    neg_payload = neg.build_report()
    pos_payload = pos.build_report(max_examples=max_examples, top_k=top_k)

    profile = {
        "negative": {
            "all_agl": {
                "nontrivial_unconstrained_core_size": _nontrivial_unsat_uniform_size(
                    neg_payload, mode="all_agl", variant="unconstrained"
                ),
                "nontrivial_striation_complete_core_size": _nontrivial_unsat_uniform_size(
                    neg_payload, mode="all_agl", variant="striation_complete"
                ),
            },
            "hessian216": {
                "nontrivial_unconstrained_core_size": _nontrivial_unsat_uniform_size(
                    neg_payload, mode="hessian216", variant="unconstrained"
                ),
                "nontrivial_striation_complete_core_size": _nontrivial_unsat_uniform_size(
                    neg_payload, mode="hessian216", variant="striation_complete"
                ),
            },
            "involution_det2": {
                "z10_unconstrained_core_size": int(
                    neg_payload["matrix"]["involution_det2"]["(1,0)"][
                        "minimal_core_size"
                    ]
                ),
                "z10_striation_complete_core_size": int(
                    neg_payload["matrix"]["involution_det2"]["(1,0)"][
                        "variant_profiles"
                    ]["striation_complete"]["minimal_core_size"]
                ),
            },
        },
        "positive": {
            "all_agl": {
                "z10_unconstrained_cert_size": int(
                    pos_payload["mode_results"]["all_agl"]["minimal_certificate_size"]
                ),
                "z10_striation_complete_cert_size": int(
                    pos_payload["mode_results"]["all_agl"]["variant_profiles"][
                        "striation_complete"
                    ]["minimal_certificate_size"]
                ),
            },
            "hessian216": {
                "z10_unconstrained_cert_size": int(
                    pos_payload["mode_results"]["hessian216"][
                        "minimal_certificate_size"
                    ]
                ),
                "z10_striation_complete_cert_size": int(
                    pos_payload["mode_results"]["hessian216"]["variant_profiles"][
                        "striation_complete"
                    ]["minimal_certificate_size"]
                ),
            },
        },
    }

    derived = {
        "all_agl_positive_minus_negative_unconstrained": int(
            profile["positive"]["all_agl"]["z10_unconstrained_cert_size"]
            - profile["negative"]["all_agl"]["nontrivial_unconstrained_core_size"]
        ),
        "all_agl_positive_minus_negative_striation_complete": int(
            profile["positive"]["all_agl"]["z10_striation_complete_cert_size"]
            - profile["negative"]["all_agl"]["nontrivial_striation_complete_core_size"]
        ),
        "hessian_positive_minus_negative_unconstrained": int(
            profile["positive"]["hessian216"]["z10_unconstrained_cert_size"]
            - profile["negative"]["hessian216"]["nontrivial_unconstrained_core_size"]
        ),
        "hessian_positive_minus_negative_striation_complete": int(
            profile["positive"]["hessian216"]["z10_striation_complete_cert_size"]
            - profile["negative"]["hessian216"][
                "nontrivial_striation_complete_core_size"
            ]
        ),
    }

    theorem_flags = {
        "nontrivial_unsat_baseline_3_in_agl_hessian": (
            profile["negative"]["all_agl"]["nontrivial_unconstrained_core_size"] == 3
            and profile["negative"]["hessian216"]["nontrivial_unconstrained_core_size"]
            == 3
        ),
        "nontrivial_unsat_striation_4_in_agl_hessian": (
            profile["negative"]["all_agl"]["nontrivial_striation_complete_core_size"]
            == 4
            and profile["negative"]["hessian216"][
                "nontrivial_striation_complete_core_size"
            ]
            == 4
        ),
        "identity_positive_6_vs_5": (
            profile["positive"]["all_agl"]["z10_unconstrained_cert_size"] == 6
            and profile["positive"]["hessian216"]["z10_unconstrained_cert_size"] == 5
        ),
        "identity_positive_gap_robust_under_striation": (
            profile["positive"]["all_agl"]["z10_striation_complete_cert_size"] == 6
            and profile["positive"]["hessian216"]["z10_striation_complete_cert_size"]
            == 5
        ),
        "dual_gap_shrinks_by_one_under_striation": (
            derived["all_agl_positive_minus_negative_unconstrained"]
            - derived["all_agl_positive_minus_negative_striation_complete"]
            == 1
            and derived["hessian_positive_minus_negative_unconstrained"]
            - derived["hessian_positive_minus_negative_striation_complete"]
            == 1
        ),
    }

    return {
        "status": "ok",
        "profile": profile,
        "derived": derived,
        "theorem_flags": theorem_flags,
        "sources": {
            "negative_cores": "tools/minimal_global_full_sign_cores.py",
            "positive_certificates": "tools/minimal_global_identity_certificates.py",
        },
        "notes": (
            "Dual profile compares minimal contradiction witnesses (UNSAT) and "
            "minimal uniqueness witnesses (SAT identity cell)."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    p = payload["profile"]
    d = payload["derived"]
    lines = ["# Global Sign Rigidity Dual Profile", ""]
    lines.append(
        "- Dual view: negative contradiction cores vs positive identity certificates."
    )
    lines.append("")
    lines.append(
        "Mode | Negative core (unconstrained) | Negative core (striation) | Positive cert (unconstrained) | Positive cert (striation)"
    )
    lines.append("--- | --- | --- | --- | ---")
    lines.append(
        "all_agl | {} | {} | {} | {}".format(
            p["negative"]["all_agl"]["nontrivial_unconstrained_core_size"],
            p["negative"]["all_agl"]["nontrivial_striation_complete_core_size"],
            p["positive"]["all_agl"]["z10_unconstrained_cert_size"],
            p["positive"]["all_agl"]["z10_striation_complete_cert_size"],
        )
    )
    lines.append(
        "hessian216 | {} | {} | {} | {}".format(
            p["negative"]["hessian216"]["nontrivial_unconstrained_core_size"],
            p["negative"]["hessian216"]["nontrivial_striation_complete_core_size"],
            p["positive"]["hessian216"]["z10_unconstrained_cert_size"],
            p["positive"]["hessian216"]["z10_striation_complete_cert_size"],
        )
    )
    lines.append("")
    lines.append("Derived gaps")
    lines.append("")
    lines.append(
        "- all_agl: unconstrained `{}` -> striation `{}`".format(
            d["all_agl_positive_minus_negative_unconstrained"],
            d["all_agl_positive_minus_negative_striation_complete"],
        )
    )
    lines.append(
        "- hessian216: unconstrained `{}` -> striation `{}`".format(
            d["hessian_positive_minus_negative_unconstrained"],
            d["hessian_positive_minus_negative_striation_complete"],
        )
    )
    lines.append("")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/global_sign_rigidity_dual_profile_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/GLOBAL_SIGN_RIGIDITY_DUAL_PROFILE_2026_02_11.md"),
    )
    parser.add_argument("--max-examples", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()

    payload = build_report(max_examples=args.max_examples, top_k=args.top_k)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
