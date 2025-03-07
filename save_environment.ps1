# Export Conda environment without build hashes and exclude prefix
conda env export --no-builds | Select-String -Pattern 'prefix:' -NotMatch | Out-File -Encoding utf8 environment.yml

Write-Host "Universal environment file created."
