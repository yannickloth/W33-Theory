#!/usr/bin/env python3
"""
Generate a consolidated "selection rules" report tying together:
  - canonical SU(3)+E6 cubic sign gauge,
  - signed W(E6) simple-generator action on the 27,
  - concrete swapped-pair channels in the Schläfli/meet graphs.

Mathematically, for each generator g acting on the 27 basis as a signed permutation:
  e_i  ->  s_i * e_{p(i)},
the cubic C = Σ_{triad t={i,j,k}} d_t x_i x_j x_k transforms as:
  d_{p(t)} = g_scale * (s_i s_j s_k) * d_t,
where g_scale is a single global ±1 factor (cubic is unique up to scale).

This script:
  - computes g_scale for each generator from the data (and verifies consistency on all 45 triads),
  - records per-triad parity factors s_i s_j s_k (useful as a "selection parity" under that generator),
  - merges in the channel dictionary classification (skew vs meet swapped pairs).

Writes:
  artifacts/selection_rules_report.json
  artifacts/selection_rules_report.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _triad_key(triad: List[int] | Tuple[int, int, int]) -> Tuple[int, int, int]:
    a, b, c = triad
    t = tuple(sorted((int(a), int(b), int(c))))
    return t  # type: ignore[return-value]


def main() -> None:
    # Ensure upstream artifacts exist (tools generate them deterministically).
    # We read the already-produced artifacts rather than recomputing here.
    canon_path = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    act_path = ROOT / "artifacts" / "we6_signed_action_on_27.json"
    chan_path = ROOT / "artifacts" / "we6_channel_dictionary.json"

    canon = _load_json(canon_path)
    act = _load_json(act_path)
    chan = _load_json(chan_path)

    if not isinstance(canon, dict) or not canon.get("counts", {}).get(
        "solvable", False
    ):
        raise RuntimeError("canonical_su3_gauge_and_cubic.json is missing or unsolved")
    if not isinstance(act, dict) or act.get("status") != "ok":
        raise RuntimeError("we6_signed_action_on_27.json missing or invalid")
    if not isinstance(chan, dict) or chan.get("status") != "ok":
        raise RuntimeError("we6_channel_dictionary.json missing or invalid")

    d_bits: Dict[Tuple[int, int, int], int] = {}
    for t in canon["solution"]["d_triples"]:
        triad = _triad_key(t["triple"])
        d_bits[triad] = 1 if int(t["sign"]) == -1 else 0
    if len(d_bits) != 45:
        raise RuntimeError(f"Expected 45 triads, got {len(d_bits)}")

    # Map channel info by generator name for quick merge.
    chan_by_name = {g["name"]: g for g in chan["generators"]}

    report_gens = []
    total_failures = 0

    for g in act["generators"]:
        name = g["name"]
        p: List[int] = [int(x) for x in g["permutation"]]
        s: List[int] = [int(x) for x in g["signs"]]  # ±1 per i: e_i -> s[i] e_{p(i)}

        if len(p) != 27 or len(s) != 27:
            raise RuntimeError("Bad generator data shape")

        # Compute triad orbits and selection parity factors.
        seen = set()
        triad_orbits: List[List[Tuple[int, int, int]]] = []
        for triad in d_bits:
            if triad in seen:
                continue
            orbit = []
            cur = triad
            while cur not in seen:
                seen.add(cur)
                orbit.append(cur)
                img = tuple(sorted((p[cur[0]], p[cur[1]], p[cur[2]])))
                cur = img  # type: ignore[assignment]
            triad_orbits.append(orbit)

        orbit_size_hist = Counter(len(o) for o in triad_orbits)

        # Infer global scale g_scale from the first triad and verify across all.
        g_scale: int | None = None
        failures = 0
        per_triad_parity = {}
        for triad, d_t in d_bits.items():
            img = tuple(sorted((p[triad[0]], p[triad[1]], p[triad[2]])))
            d_img = d_bits[img]  # must exist by invariance
            parity = s[triad[0]] * s[triad[1]] * s[triad[2]]
            per_triad_parity["%d,%d,%d" % triad] = int(parity)
            # In bits: d_img ⊕ d_t equals (parity==-1) ⊕ (g_scale==-1)
            lhs = d_img ^ d_t
            rhs = 1 if parity == -1 else 0
            if g_scale is None:
                g_scale = -1 if (lhs ^ rhs) == 1 else 1
            else:
                want = 1 if g_scale == -1 else 0
                if (lhs ^ rhs) != want:
                    failures += 1
        total_failures += failures

        parity_hist = Counter(per_triad_parity.values())

        chan_info = chan_by_name.get(name, {})
        report_gens.append(
            {
                "name": name,
                "global_scale": int(g_scale) if g_scale is not None else None,
                "check_failures": int(failures),
                "triad_orbit_size_hist": {
                    str(k): int(v) for k, v in sorted(orbit_size_hist.items())
                },
                "triad_parity_hist": {
                    str(k): int(v) for k, v in sorted(parity_hist.items())
                },
                "triad_parity": per_triad_parity,
                "channels": chan_info,
            }
        )

    out = {
        "status": "ok",
        "counts": {
            "generators": len(report_gens),
            "total_failures": int(total_failures),
        },
        "reference_orbit": act["reference_orbit"],
        "generators": report_gens,
    }

    out_json = ROOT / "artifacts" / "selection_rules_report.json"
    out_json.write_text(json.dumps(out, indent=2, default=int), encoding="utf-8")

    # Small markdown summary for quick reading.
    lines = []
    lines.append("# Selection Rules Report (canonical gauge)")
    lines.append("")
    lines.append(f"- reference orbit: {out['reference_orbit']}")
    lines.append(f"- generators: {out['counts']['generators']}")
    lines.append(f"- total invariance failures: {out['counts']['total_failures']}")
    lines.append("")
    for g in report_gens:
        ch = g["channels"]
        trans = ch.get("n_transpositions")
        tri_fixed = ch.get("triads_fixed_setwise")
        parity_hist = g["triad_parity_hist"]
        lines.append(f"## {g['name']}")
        lines.append(f"- global_scale: {g['global_scale']}")
        lines.append(f"- transpositions: {trans}, triads_fixed_setwise: {tri_fixed}")
        lines.append(f"- triad_orbit_size_hist: {g['triad_orbit_size_hist']}")
        lines.append(f"- triad_parity_hist: {parity_hist}  (values are ±1)")
        lines.append("")

    out_md = ROOT / "artifacts" / "selection_rules_report.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    if total_failures == 0:
        print("PASS selection rule consistency")
    else:
        print("FAIL selection rule consistency")


if __name__ == "__main__":
    main()
