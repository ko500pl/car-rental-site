@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================================
echo   Fleet House  ^>^>  GitHub  (ko500pl/car-rental-site)
echo ==========================================================
echo.
if exist ".git\index.lock" del /f /q ".git\index.lock"
echo [1/4] dist is no longer tracked - removing it from git...
git rm -r -q --cached dist 2>nul
echo [2/4] staging...
git add -A
echo [3/4] commit...
git commit -m "Fleet House: interactive map homepage, 247 attractions, from-to route planner"
echo [4/4] push...
git push -u origin main
echo.
if %ERRORLEVEL%==0 (
  echo   ==========================================================
  echo   OK - uploaded.
  echo   Netlify will build the site itself and publish in 2-3 min.
  echo   ==========================================================
) else (
  echo   Something went wrong - screenshot this window.
)
echo.
pause
