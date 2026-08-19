@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================================
echo   Drive On  ^>^>  GitHub  (ko500pl/car-rental-site)
echo ==========================================================
echo.
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\HEAD.lock" del /f /q ".git\HEAD.lock"
if exist ".git\refs\heads\main.lock" del /f /q ".git\refs\heads\main.lock"
if exist ".git\refs\heads\harden-static-rental-funnel.lock" del /f /q ".git\refs\heads\harden-static-rental-funnel.lock"
echo [1/4] dist is no longer tracked - removing it from git...
git rm -r -q --cached dist 2>nul
echo [2/4] staging...
git add -A
echo [3/4] commit...
git commit -m "Drive On: site update"
echo [4/4] push...
git branch -f main HEAD
git push -u origin HEAD:main
echo.
if %ERRORLEVEL%==0 (
  echo   ==========================================================
  echo   OK - uploaded.
  echo   GitHub Pages will publish in 2-3 min.
  echo   ==========================================================
) else (
  echo   Something went wrong - screenshot this window.
)
echo.
pause
