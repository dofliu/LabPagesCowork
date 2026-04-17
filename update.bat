@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Git Auto-Update Script
echo ========================================

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not in PATH.
    pause
    exit /b
)

:: Get current branch
for /f "tokens=*" %%a in ('git branch --show-current') do set current_branch=%%a

if "%current_branch%"=="" (
    echo Error: Could not determine current branch. Are you in a Git repository?
    pause
    exit /b
)

echo [1/3] Staging all changes...
git add .

echo [2/3] Committing changes...
:: Generate timestamp for commit message
set commit_message=Update %date% %time%
git commit -m "%commit_message%"
if %errorlevel% neq 0 (
    echo No changes to commit or commit failed.
)

echo [3/3] Pushing to origin/%current_branch%...
git push origin %current_branch%

if %errorlevel% eq 0 (
    echo.
    echo SUCCESS: Project updated and pushed to %current_branch%.
) else (
    echo.
    echo ERROR: Push failed. Please check your network or credentials.
)

echo ========================================
pause
