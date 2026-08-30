@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   Fleet Freak  ^>^>  GitHub (main)  -- pause-free
echo   Booking form: return location + "I need a driver"
echo ============================================================
echo.

rem The Linux side cannot delete lock files, so clear them here first.
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\HEAD.lock" del /f /q ".git\HEAD.lock"
if exist ".git\refs\heads\main.lock" del /f /q ".git\refs\heads\main.lock"
if exist ".git\refs\heads\harden-static-rental-funnel.lock" del /f /q ".git\refs\heads\harden-static-rental-funnel.lock"

rem The commit is ALREADY BUILT (b2f8694) - dropoff + with_driver on the booking
rem form in 6 languages, plus the matching firestore.rules field.
rem NO "git add -A" HERE, ON PURPOSE - your 200+ local edits stay local.

git update-ref refs/heads/harden-static-rental-funnel b2f869465ea596a532a9993355147270810df9e4
git branch -f main b2f869465ea596a532a9993355147270810df9e4

echo Commits waiting to go up:
echo.
git --no-pager log --oneline origin/main..main
echo.

echo Pushing...
git push -u origin main
set RC=%ERRORLEVEL%
echo.

if %RC%==0 (
  echo   ============================================================
  echo   OK - uploaded. Quality gate will re-run automatically.
  echo   ============================================================
) else (
  echo   ============================================================
  echo   FAILED - error code %RC%. Nothing was uploaded.
  echo   ============================================================
)
echo.
timeout /t 20
