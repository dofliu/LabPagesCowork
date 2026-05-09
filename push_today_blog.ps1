# push_today_blog.ps1
# Today: 2026-05-09 windMindOM 工單前端完成 — 3-Step Wizard 與工單狀態機設計實錄

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoDir

Write-Host ">>> Removing stale git lock files..." -ForegroundColor Cyan
$lockFiles = @(".git\index.lock", ".git\HEAD.lock", ".git\packed-refs.lock", ".git\index-tmp.lock")
foreach ($f in $lockFiles) {
    $fullPath = Join-Path $repoDir $f
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Removed: $f" -ForegroundColor Green
    }
}

Write-Host ">>> Current branch: $(git branch --show-current)" -ForegroundColor Yellow

Write-Host ">>> Pushing branch claude/blog-2026-05-09 to origin..." -ForegroundColor Cyan
git push origin claude/blog-2026-05-09

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Push successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host ">>> Next step: Create PR at:" -ForegroundColor Yellow
    Write-Host "    https://github.com/dofliu/LabPagesCowork/compare/main...claude/blog-2026-05-09" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "PR Title: blog: 2026-05-09 windMindOM 工單前端完成 — 3-Step Wizard 與工單狀態機設計實錄"
} else {
    Write-Host "❌ Push failed. Please check GitHub credentials." -ForegroundColor Red
}
