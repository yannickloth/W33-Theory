# Layperson Evidence Audit Template

Use this template to evaluate any claim in the repository.

The goal is not to "agree" or "disagree" with a claim.
The goal is to test whether the evidence chain is complete and reproducible.

---

## Quick Scoring

- `A` Strong: script + test + artifact all present and rerunnable
- `B` Medium: script present, but tests or artifacts incomplete
- `C` Weak: mostly narrative/interpretation, limited executable trace
- `D` Unsupported: cannot locate a concrete evidence path

---

## Audit Table

| Claim ID | Claim Text (short) | Source Doc | Script Path | Test Path | Artifact Path | Rerun Result | Score | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |

---

## One-Claim Deep Audit

Claim:

Source:

### Step 1: Locate executable path

- Script found? `yes/no`
- Path:

### Step 2: Locate test path

- Test found? `yes/no`
- Path:

### Step 3: Locate machine output

- Artifact/report found? `yes/no`
- Path:

### Step 4: Reproducibility run

Commands executed:

Observed result:

### Step 5: Confidence decision

Final score: `A/B/C/D`

Reason:

---

## Interpretation Guardrails

When writing conclusions, separate:

- what was directly computed
- what is an interpretation layer

Use wording like:

- "Computed result shows ..."
- "Interpretation suggests ..."

Avoid wording like:

- "This proves all of physics ..."
