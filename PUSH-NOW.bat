@echo off
chcp 65001 >nul

rem ===========================================================
rem   RentUp  >>  GitHub (main)
rem   Design pass: one voice across the app and the site
rem ===========================================================
rem
rem Fixed path on purpose. There are several worktrees of this
rem repository under C:\Projects\car-rental-site and they share one
rem .git, so running a copy of this file from one of them is how the
rem branch got reset to an already-pushed commit once before.
set REPO=C:\Projects\car-rental-site\car-rental-site
set WANT=44dabc99606f9e349eff212d0e0ff827b2a0a1e7

cd /d "%REPO%" || (echo Cannot find %REPO% & timeout /t 20 & exit /b 1)

echo ============================================================
echo   RentUp  ^>^>  GitHub (main)
echo   Design pass: one voice across the app and the site
echo   Repo: %REPO%
echo ============================================================
echo.

rem The Linux side cannot delete lock files, so clear them here first.
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\HEAD.lock" del /f /q ".git\HEAD.lock"
if exist ".git\refs\heads\main.lock" del /f /q ".git\refs\heads\main.lock"
if exist ".git\refs\heads\harden-static-rental-funnel.lock" del /f /q ".git\refs\heads\harden-static-rental-funnel.lock"

echo Fetching what is on GitHub right now...
git fetch origin
echo.

rem Refuse to push blind. This commit was built on a specific
rem origin/main; if GitHub has moved since, forcing the branch to it
rem would fail anyway, or be "fixed" later with a force push that drops
rem somebody else's work. Another agent has been committing to this
rem repository today, so this check is not theoretical.
for /f %%i in ('git rev-parse "%WANT%^"') do set PARENT=%%i
for /f %%i in ('git rev-parse origin/main') do set REMOTE=%%i

if not "%PARENT%"=="%REMOTE%" (
  echo   ============================================================
  echo   STOP - GitHub has moved on since this commit was prepared.
  echo.
  echo   commit is built on: %PARENT%
  echo   origin/main is now: %REMOTE%
  echo.
  echo   Nothing was changed and nothing was pushed. Tell Claude and
  echo   it will rebuild the commit on the current origin/main.
  echo   ============================================================
  echo.
  timeout /t 30
  exit /b 1
)

echo This is one commit on top of origin/main:
echo.
git --no-pager show --stat --oneline %WANT%
echo.

rem NO "git add -A" here, on purpose - your local edits stay local.
git update-ref refs/heads/harden-static-rental-funnel %WANT%
git branch -f main %WANT%

echo Pushing...
git push origin main
set RC=%ERRORLEVEL%
echo.

if %RC%==0 (
  echo   ============================================================
  echo   OK - uploaded. The quality gate runs automatically.
  echo.
  echo   To publish it, on GitHub:
  echo     Actions -^> "Quality Gate and Manual Deploy"
  echo     -^> Run workflow -^> deploy: true
  echo   ============================================================
) else (
  echo   ============================================================
  echo   FAILED - error code %RC%. Nothing was uploaded.
  echo   Send Claude the message above.
  echo   ============================================================
)
echo.
timeout /t 30
