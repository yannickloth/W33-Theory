#!/usr/bin/env python3
"""
Fetch and parse the Monster conjugacy class table from the ATLAS (QMUL).

This is a *build tool* used to generate a small, tracked JSON snapshot that
tests can consume offline. It is intentionally dependency-free (urllib + regex).

Source page:
  https://brauer.maths.qmul.ac.uk/Atlas/v3/spor/M/

Output (default):
  data/monster_atlas_ccls.json
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

ATLAS_MONSTER_URL = "https://brauer.maths.qmul.ac.uk/Atlas/v3/spor/M/"

# Power-up entries are rendered as e.g. "23B<SUP>5</SUP>" or "10A<SUP></SUP>".
_POWER_ENTRY_RE = re.compile(r"([0-9]+[0-9A-Za-z']*)\s*<SUP>([^<]*)</SUP>")


def class_order_from_label(class_name: str) -> int:
    """Parse the element order from an ATLAS class label, e.g. '10A' -> 10."""
    s = str(class_name).strip()
    digits = ""
    for ch in s:
        if ch.isdigit():
            digits += ch
        else:
            break
    return int(digits) if digits else 0


def extract_ccls_table_html(html: str) -> str:
    start = html.find('NAME="ccls"')
    if start < 0:
        raise RuntimeError('ATLAS HTML: could not find NAME="ccls" anchor')
    end = html.find("</TABLE>", start)
    if end < 0:
        raise RuntimeError("ATLAS HTML: could not find closing </TABLE> for ccls")
    return html[start:end]


def parse_monster_ccls_table(table_html: str) -> dict[str, dict[str, Any]]:
    """Parse the ATLAS 'Conjugacy classes of M' table.

    Returns a mapping:
      {class_name: {"order": int, "centralizer_order": str, "powers": {exp: [classes...]}}}

    Notes:
    - The ATLAS "Power up" column lists *some* power-relations. For some classes,
      the same exponent can plausibly reach multiple conjugacy classes of the
      same order (e.g. by composing a fixed divisor exponent with a unit power
      on the lower-order element). The table does not always disambiguate this,
      so we conservatively store a list of possible targets per exponent.
    - Tests should use this snapshot offline and only assert on unambiguous maps
      (lists of length 1).
    """
    # Split on <TR> boundaries. The table uses implicit </TD> closings, so we
    # split cells on every <TD ...> occurrence.
    rows = re.split(r"<TR>", table_html)
    data_rows = [r for r in rows if "<TD" in r.upper()]

    classes: dict[str, dict[str, Any]] = {}
    powers_by_from: dict[str, dict[int, set[str]]] = {}

    for row in data_rows:
        cells = re.split(r"<TD[^>]*>", row)
        if len(cells) < 4:
            continue

        to_class = re.sub(r"<.*", "", cells[1]).strip()
        if not to_class:
            continue

        centralizer_raw = re.sub(r"<.*", "", cells[2])
        centralizer_order = re.sub(r"\s+", "", centralizer_raw).strip()

        classes[to_class] = {
            "order": class_order_from_label(to_class),
            "centralizer_order": centralizer_order,
        }

        power_cell = cells[3]
        for from_class, sup_text in _POWER_ENTRY_RE.findall(power_cell):
            from_class = from_class.strip()
            sup_text = sup_text.strip()
            if not from_class:
                continue

            o_from = class_order_from_label(from_class)
            o_to = class_order_from_label(to_class)

            if sup_text:
                exp = int(sup_text)
            else:
                # For different orders the exponent is implied by order ratio.
                if o_from and o_to and o_from != o_to and (o_from % o_to == 0):
                    exp = o_from // o_to
                else:
                    exp = 1

            m = powers_by_from.setdefault(from_class, {})
            m.setdefault(exp, set()).add(to_class)

    # Ensure every from_class encountered is present in the class table map.
    for from_class in sorted(powers_by_from.keys()):
        if from_class not in classes:
            classes[from_class] = {
                "order": class_order_from_label(from_class),
                "centralizer_order": "",
            }

    # Attach powers per class and add the trivial order -> 1A mapping.
    for cname, info in classes.items():
        order = int(info.get("order", 0) or 0)
        pm = {k: set(v) for k, v in powers_by_from.get(cname, {}).items()}
        if cname.upper() == "1A":
            pm.setdefault(1, set()).add("1A")
        elif order > 0:
            pm.setdefault(order, set()).add("1A")
        info["powers"] = {str(k): sorted(pm[k]) for k in sorted(pm.keys())}

    return classes


def fetch_html(url: str = ATLAS_MONSTER_URL) -> str:
    with urllib.request.urlopen(url) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def build_payload(url: str = ATLAS_MONSTER_URL) -> dict[str, object]:
    html = fetch_html(url)
    table_html = extract_ccls_table_html(html)
    classes = parse_monster_ccls_table(table_html)
    return {
        "source_url": url,
        "n_classes": len(classes),
        "classes": classes,
    }


def main(argv: list[str]) -> int:
    out_path = (
        Path(argv[1])
        if len(argv) >= 2
        else (Path(__file__).resolve().parents[1] / "data" / "monster_atlas_ccls.json")
    )
    payload = build_payload()
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Wrote {out_path} ({payload['n_classes']} classes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
