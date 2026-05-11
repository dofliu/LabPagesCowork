# push_today_blog.ps1
# Today: 2026-05-10 windMindOM M4 Backend 全收 - 庫存原子派工與成本台帳設計

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoDir

Write-Host ">>> Removing stale git lock files..." -ForegroundColor Cyan
$lockFiles = @(
    ".git\index.lock", ".git\HEAD.lock", ".git\packed-refs.lock",
    ".git\index-tmp.lock", ".git\index-new.lock", ".git\index-new2.lock",
    ".git\index-work.lock", ".git\index2.lock",
    ".git\index-1778112687.lock"
)
foreach ($f in $lockFiles) {
    $fullPath = Join-Path $repoDir $f
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Removed: $f" -ForegroundColor Green
    }
}

Write-Host ">>> Current branch: $(git branch --show-current)" -ForegroundColor Yellow
Write-Host ">>> New article: posts/2026-05-10-windmindom-m4-backend-inventory-atomic-dispatch-cost-ledger.html" -ForegroundColor Yellow

Write-Host ">>> Pushing branch claude/blog-2026-05-09- to origin..." -ForegroundColor Cyan
git push origin "claude/blog-2026-05-09-"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Push successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host ">>> Next step: Create PR at:" -ForegroundColor Yellow
    Write-Host "    https://github.com/dofliu/LabPagesCowork/compare/main...claude/blog-2026-05-09-" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "PR Title: blog: 2026-05-10 windMindOM M4 Backend 全收 - 庫存原子派工與成本台帳設計"
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Please check your GitHub credentials and try again." -ForegroundColor Red
    Write-Host "   You may need to run: git config --global credential.helper manager" -ForegroundColor Yellow
}
