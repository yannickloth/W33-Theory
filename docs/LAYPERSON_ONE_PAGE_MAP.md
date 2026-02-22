# W33 One-Page Map For New Readers

Ultra-fast orientation for people with no physics background.

## What This Repo Is

- A research repo that tests whether patterns from a finite geometry (`W(3,3)` / `W33`) line up with structures from exceptional Lie algebra frameworks (`E6`, `E7`, `E8`).
- Built around reproducibility: claims should map to scripts, tests, and machine outputs.

## What To Read First

1. `README.md`
2. `STANDARDIZATION.md`
3. `docs/LAYPERSON_TEXTBOOK_GUIDE.md`

## Core Rule

For any major claim, find:

`claim -> script -> artifact -> test`

If one link is missing, confidence should drop.

## First 20 Minutes (Hands-on)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python scripts/w33_e8_correspondence_theorem.py
python -m pytest tests/test_e8_embedding.py -q
```

## How To Interpret "Verified"

In this repo, "verified" means:

- computationally verified in this code model

It does not automatically mean:

- experimentally validated in nature

## Fast Vocabulary

- `W33`: graph derived from `W(3,3)`
- `Automorphism`: symmetry that preserves structure
- `Homology`: algebraic count of structural holes
- `Artifact`: generated output file from a script
- `Smoke test`: quick sanity-check test

## Where To Go Next

- Beginner deep dive: `docs/LAYPERSON_TEXTBOOK_GUIDE.md`
- Practice modules: `docs/LAYPERSON_WORKBOOK.md`
- Claim scoring template: `docs/LAYPERSON_EVIDENCE_AUDIT_TEMPLATE.md`
- Concept navigation map: `docs/LAYPERSON_CONCEPT_MAP.md`
- Documentation map: `docs/INDEX.md`
- Contribution workflow: `CONTRIBUTING.md`
