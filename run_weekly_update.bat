@echo off
chcp 65001 >nul
echo ============================================
echo  LabPagesCowork — Weekly Update
echo  %date% %time%
echo ============================================

echo.
echo [Step 0] 清理 git stale lock 檔案...
cd /d "D:\Dropbox\Project_CodingSimulation\MCP\LabPagesCowork"
if exist ".git\index.lock" del /f ".git\index.lock" && echo   已刪除 index.lock
if exist ".git\index.lock.bak" del /f ".git\index.lock.bak"
if exist ".git\HEAD.lock" del /f ".git\HEAD.lock" && echo   已刪除 HEAD.lock
if exist ".git\HEAD.lock.bak" del /f ".git\HEAD.lock.bak"
if exist ".git\HEAD.lock.bak2" del /f ".git\HEAD.lock.bak2"
if exist ".git\index-tmp.lock" del /f ".git\index-tmp.lock"
if exist ".git\index-tmp.lock.bak" del /f ".git\index-tmp.lock.bak"
if exist ".git\index2.lock" del /f ".git\index2.lock"
if exist ".git\index-0417-1776384452346253782.lock" del /f ".git\index-0417-1776384452346253782.lock"
if exist ".git\index-new-2026-04-17.lock" del /f ".git\index-new-2026-04-17.lock"
if exist ".git\index-tmp-0418.lock" del /f ".git\index-tmp-0418.lock"
if exist ".git\index-tmp-valid.lock" del /f ".git\index-tmp-valid.lock"
if exist ".git\idx_1776557201.lock" del /f ".git\idx_1776557201.lock"
echo   Lock 清理完成

echo.
echo [Step 1] 掃描所有專案 STATUS.yaml...
cd /d "D:\Dropbox\Project_CodingSimulation"
python update_research_os.py
if errorlevel 1 (
    echo   [警告] update_research_os.py 回傳錯誤，繼續執行...
)

echo.
echo [Step 2] 執行完整更新 + 推送...
cd /d "D:\Dropbox\Project_CodingSimulation\MCP\LabPagesCowork"
python scripts\update_all.py --all --push
if errorlevel 1 (
    echo.
    echo   [push 失敗] 嘗試建立新分支...
    for /f "tokens=1-3 delims=/" %%a in ("%date%") do set YDATE=%%c-%%a-%%b
    git checkout -b auto/weekly-%YDATE%
    git push -u origin auto/weekly-%YDATE%
)

echo.
echo ============================================
echo  完成！請確認上方輸出是否有錯誤。
echo ============================================
pause
