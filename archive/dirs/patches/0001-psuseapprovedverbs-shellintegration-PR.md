Title: fix(terminal): use approved verb for helper function in shellIntegration.ps1 (PSUseApprovedVerbs)

Summary:
PSScriptAnalyzer flags `PSUseApprovedVerbs` for the helper function `__VSCode-Escape-Value` in the built-in `shellIntegration.ps1` script. This change renames the function to `ConvertTo-VSCodeEscapedValue` and updates all call sites accordingly. The change is non-functional and only intended to satisfy the linter and use an approved verb.

Details:
- Rename `Global:__VSCode-Escape-Value` → `Global:ConvertTo-VSCodeEscapedValue`
- Update all call sites in `shellIntegration.ps1` to use the new name

Rationale:
Using an approved verb fixes the `PSUseApprovedVerbs` diagnostic and prevents editor warnings for users running the PowerShell linter. This is a purely internal rename (no behavior changes).

Alternative:
If the maintainers prefer not to rename the helper, we can instead add a small `PSScriptAnalyzerSettings` file-level header to disable `PSUseApprovedVerbs` for this script. I'm happy to change the PR accordingly.

How to apply:
- Patch file included: `patches/0001-psuseapprovedverbs-shellintegration-rename.patch` (relative to repo root).
- Suggested branch: `fix/psuseapprovedverbs-shellintegration`

Would you like me to open the PR on your behalf or prepare the patch for you to submit? (I prepared the patch and this PR template.)
