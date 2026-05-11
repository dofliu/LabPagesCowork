# fix_conflict_and_push.ps1
# Resolve PR #109 merge conflict and re-push

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoDir

Write-Host "=== windMindOM Blog Conflict Resolver ===" -ForegroundColor Cyan
Write-Host "Repo: $repoDir" -ForegroundColor Gray

# Step 1: Remove lock files
Write-Host "`n[1/6] Removing git lock files..." -ForegroundColor Yellow
$lockFiles = @(
    ".git\index.lock",
    ".git\HEAD.lock",
    ".git\packed-refs.lock",
    ".git\MERGE_HEAD",
    ".git\CHERRY_PICK_HEAD",
    ".git\REBASE_HEAD"
)
foreach ($f in $lockFiles) {
    $fullPath = Join-Path $repoDir $f
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Removed: $f" -ForegroundColor Green
    }
}

# Step 2: Show current branch
$currentBranch = git branch --show-current
Write-Host "`n[2/6] Current branch: $currentBranch" -ForegroundColor Yellow

# Step 3: Fetch latest origin/main
Write-Host "`n[3/6] Fetch origin/main..." -ForegroundColor Yellow
git fetch origin
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Fetch failed. Check network connection." -ForegroundColor Red
    exit 1
}

# Step 4: Create clean branch from origin/main
Write-Host "`n[4/6] Creating claude/blog-2026-05-09-fix from origin/main..." -ForegroundColor Yellow
git branch -D claude/blog-2026-05-09-fix 2>$null
git checkout -b claude/blog-2026-05-09-fix origin/main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Checkout failed." -ForegroundColor Red
    exit 1
}
Write-Host "  Switched to claude/blog-2026-05-09-fix" -ForegroundColor Green

# Step 5: Cherry-pick the two article commits
# ad62dba = 2026-05-08 Calm Operator UI article
# 1dc3add = 2026-05-09 Work Order frontend article
Write-Host "`n[5/6] Cherry-picking 2026-05-08 article (ad62dba)..." -ForegroundColor Yellow

git cherry-pick ad62dba
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Conflict detected - auto-resolving..." -ForegroundColor DarkYellow
    git checkout --ours blog.html 2>$null
    git add blog.html posts/
    git -c "user.name=Juihung Liu" -c "user.email=moredof@gmail.com" cherry-pick --continue --no-edit
}
Write-Host "  2026-05-08 commit OK" -ForegroundColor Green

Write-Host "`n  Cherry-picking 2026-05-09 article (1dc3add)..." -ForegroundColor Yellow
git cherry-pick 1dc3add
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Conflict detected - auto-resolving..." -ForegroundColor DarkYellow
    git checkout --ours blog.html 2>$null
    git add blog.html posts/
    git -c "user.name=Juihung Liu" -c "user.email=moredof@gmail.com" cherry-pick --continue --no-edit
}
Write-Host "  2026-05-09 commit OK" -ForegroundColor Green

# Rebuild blog.html post list
Write-Host "`n  Rebuilding blog.html post list..." -ForegroundColor Gray
python scripts/update_all.py --blog
git -c "user.name=Juihung Liu" -c "user.email=moredof@gmail.com" commit -am "blog: rebuild post list including 2026-05-08 and 2026-05-09" --allow-empty

# Step 6: Force push new branch
Write-Host "`n[6/6] Pushing claude/blog-2026-05-09-fix..." -ForegroundColor Yellow
git push -f origin claude/blog-2026-05-09-fix
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  Push succeeded!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Close old PR #109" -ForegroundColor White
    Write-Host "  2. Open new PR at:" -ForegroundColor White
    Write-Host "     https://github.com/dofliu/LabPagesCowork/compare/main...claude/blog-2026-05-09-fix" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  PR title: blog: 2026-05-08 Calm Operator UI + 2026-05-09 Work Order Frontend" -ForegroundColor White
} else {
    Write-Host "`n  Push failed. Check GitHub credentials." -ForegroundColor Red
}
