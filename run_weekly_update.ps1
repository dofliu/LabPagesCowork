$LAB_DIR = "D:\Dropbox\Project_CodingSimulation\MCP\LabPagesCowork"
$ROOT_DIR = "D:\Dropbox\Project_CodingSimulation"

Write-Host "=== Step 0: Clean stale git locks ===" -ForegroundColor Yellow
Set-Location $LAB_DIR
Get-ChildItem ".git" -Filter "*.lock" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "Removed: $($_.Name)" -ForegroundColor Green
}

Write-Host "=== Step 1: Scan STATUS.yaml ===" -ForegroundColor Yellow
Set-Location $ROOT_DIR
python update_research_os.py

Write-Host "=== Step 2: Full update + push ===" -ForegroundColor Yellow
Set-Location $LAB_DIR
python scripts\update_all.py --all --push

if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed, trying new branch..." -ForegroundColor Red
    $branch = "auto/weekly-" + (Get-Date -Format "yyyy-MM-dd")
    git checkout -b $branch
    git push -u origin $branch
}

Write-Host "=== Done ===" -ForegroundColor Cyan
