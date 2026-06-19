# push_today_blog_0524.ps1
# 2026-05-24 自動產生的 blog push 腳本
# 文章：安全鎖測試哲學：AI 輔助迭代開發中，補上 Route-Level 覆蓋缺口的系統思維

$LABPAGES = "D:\Project_CodingSimulation\MCP\LabPagesCowork"
Set-Location $LABPAGES

Write-Host ">>> 移除殘留的 lock 檔..." -ForegroundColor Cyan
$lockFiles = @(
    ".git\index.lock", ".git\HEAD.lock", ".git\config.lock",
    ".git\packed-refs.lock", ".git\index-tmp.lock"
)
foreach ($lf in $lockFiles) {
    $fullPath = Join-Path $LABPAGES $lf
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Removed: $lf" -ForegroundColor Green
    }
}

Write-Host ">>> 切換或建立分支 claude/blog-2026-05-24..." -ForegroundColor Cyan
git checkout -b claude/blog-2026-05-24 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  分支已存在，切換到該分支..." -ForegroundColor Yellow
    git checkout claude/blog-2026-05-24
}

Write-Host ">>> 加入今日文章..." -ForegroundColor Cyan
git add posts/2026-05-24-autosolvervideo-iter119-crud-route-safety-lock-testing.html blog.html
git -c user.name="Juihung Liu" -c user.email="moredof@gmail.com" commit -m "blog: 2026-05-24 安全鎖測試哲學：autoSolverVideo iter119 CRUD route 覆蓋缺口"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  commit 失敗或已無新變更（可能已在 hotfix 分支 commit 過）" -ForegroundColor Yellow
    Write-Host "  嘗試 cherry-pick 已有 commit..." -ForegroundColor Cyan
    git cherry-pick claude/hotfix-blog-truncation 2>$null
}

Write-Host ""
Write-Host ">>> 目前分支: $(git branch --show-current)" -ForegroundColor Yellow
Write-Host ">>> 最新 commit:" -ForegroundColor Yellow
git log --oneline -3

Write-Host ""
Write-Host ">>> 嘗試 push 到 origin..." -ForegroundColor Cyan
git push origin claude/blog-2026-05-24
if ($LASTEXITCODE -ne 0) {
    Write-Host "  push 失敗，請手動執行或確認網路/認證設定" -ForegroundColor Red
    Write-Host ""
    Write-Host "  手動指令：" -ForegroundColor Yellow
    Write-Host "  cd D:\Project_CodingSimulation\MCP\LabPagesCowork" -ForegroundColor White
    Write-Host "  git push origin claude/hotfix-blog-truncation" -ForegroundColor White
    Write-Host "  （然後在 GitHub 建立 PR：claude/hotfix-blog-truncation -> main）" -ForegroundColor White
} else {
    Write-Host "  push 成功！請至 GitHub 建立 PR：" -ForegroundColor Green
    Write-Host "  claude/blog-2026-05-24 -> main" -ForegroundColor Green
    Write-Host "  PR 標題：blog: 2026-05-24 安全鎖測試哲學：autoSolverVideo iter119 CRUD route 覆蓋缺口" -ForegroundColor Green
}
