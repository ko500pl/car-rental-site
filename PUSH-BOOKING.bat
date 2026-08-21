@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   Firestore booking change  ^>^>  GitHub (main)
echo ============================================================
echo.

rem The Linux side cannot delete lock files, so clear them here first.
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\HEAD.lock" del /f /q ".git\HEAD.lock"
if exist ".git\refs\heads\main.lock" del /f /q ".git\refs\heads\main.lock"
if exist ".git\refs\heads\harden-static-rental-funnel.lock" del /f /q ".git\refs\heads\harden-static-rental-funnel.lock"

echo Commits waiting to go up:
echo.
git --no-pager log --oneline origin/main..HEAD
echo.
echo NOTE: this script does NOT run "git add -A".
echo Your other edited files (AUDIT.md, RESEARCH.md, content\attractions\*.yml ...)
echo stay local and are NOT uploaded. Only the commits listed above go up.
echo.
echo Press any key to push, or close this window to cancel.
pause >nul

git branch -f main HEAD
git push -u origin HEAD:main

echo.
if %ERRORLEVEL%==0 (
  echo   ==========================================================
  echo   OK - uploaded. GitHub Pages publishes in 2-3 min.
  echo   ==========================================================
) else (
  echo   Something went wrong - screenshot this window.
)
echo.
pause
