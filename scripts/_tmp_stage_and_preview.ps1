$list = Get-Content checks\_tmp_stage_list.txt
$staged = @()
foreach ($f in $list) {
    try {
        git add "$f"
        $staged += $f
    } catch {
        Write-Output "failed to add $f: $_"
    }
}
# write staged list to file
$staged | Out-File -Encoding utf8 checks\_tmp_stage_preview.txt
Write-Output "Wrote checks/_tmp_stage_preview.txt with $($staged.Count) entries"
# show staged summary
git diff --staged --name-only | Select-String 'committed_artifacts|scripts' | Out-File -Encoding utf8 checks\_tmp_git_staged_summary.txt
Write-Output "Wrote checks/_tmp_git_staged_summary.txt"
