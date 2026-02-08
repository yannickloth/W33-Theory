Write-Host "Scanning next batch: edges 124/125 -> 132/133 (5 pairs)."
for ($e1=124; $e1 -le 132; $e1+=2) {
  $e2 = $e1 + 1
  Write-Host "--- Processing edges $e1 $e2 ---"
  py -3 -X utf8 scripts/local_hotspot_feasibility.py --edges $e1 $e2 --offset 0 --limit 200 --k 40 --time-limit 5 --workers 1 --log-dir checks
  py -3 -X utf8 scripts/select_next_candidates.py --feasibility "checks/PART_CVII_local_hotspot_feasibility_${e1}_${e2}_offset*_limit200_*.json" --out "checks/_tmp_verify_next20_${e1}_${e2}.json" --n 20
  if (Test-Path "checks/_tmp_verify_next20_${e1}_${e2}.json") {
     Write-Host "Candidates file exists: checks/_tmp_verify_next20_${e1}_${e2}.json"
     py -3 -X utf8 scripts/verify_and_register_local_pairs.py --feasibility "checks/_tmp_verify_next20_${e1}_${e2}.json" --workers 1 --time-limit 30
     git add committed_artifacts/PART_CVII_pair_obstruction_*_*.json committed_artifacts/PART_CVII_forbids.json committed_artifacts/PART_CVII_dd_pair_obstruction_*.json committed_artifacts/PART_CVII_dd_shrink_result_*.json
     git commit -m "auto: register pair obstructions and dd artifacts for $e1,$e2" --no-verify
     if ($LASTEXITCODE -ne 0) { Write-Host "Nothing new to commit" }
     git push origin HEAD
  } else {
     Write-Host "No candidates selected for $e1 $e2; skipping"
  }
}