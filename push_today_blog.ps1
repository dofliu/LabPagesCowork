# push_today_blog.ps1 — 由自動化排程更新（2026-04-29）
# 今日文章：時間序列基礎模型革命：MOIRAI 2.0 與 Chronos 如何改寫風能預測格局
# 執行方式：在 PowerShell 中 cd 到 LabPagesCowork 目錄後執行 .\push_today_blog.ps1

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoDir

Write-Host ">>> 清除殘留 git lock 檔..." -ForegroundColor Cyan
$lockFiles = @(
    ".git\index.lock",
    ".git\HEAD.lock",
    ".git\packed-refs.lock"
)
foreach ($f in $lockFiles) {
    $fullPath = Join-Path $repoDir $f
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Removed: $f" -ForegroundColor Green
    }
}

Write-Host ">>> 切換到今日新分支（已含今日文章 commit）..." -ForegroundColor Cyan
git checkout claude/blog-2026-04-29

Write-Host ">>> git push 到 GitHub..." -ForegroundColor Cyan
git push origin claude/blog-2026-04-29

Write-Host ""
Write-Host "✅ 推送完成！請至 GitHub 建立 PR 合併到 main：" -ForegroundColor Green
Write-Host "   https://github.com/dofliu/LabPagesCowork/compare/claude/blog-2026-04-29" -ForegroundColor Cyan
