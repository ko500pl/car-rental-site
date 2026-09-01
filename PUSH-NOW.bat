@echo off
chcp 65001 >nul

rem ===========================================================
rem   RentUp  >>  GitHub (main)
rem   Live catalogue: every car sells, page or no page
rem ===========================================================
rem
rem This script deliberately does NOT use %~dp0. There are several
rem worktrees of this repository under C:\Projects\car-rental-site,
rem they all share one .git, and running an old copy of this file from
rem one of them is what reset the branch back to an already-pushed
rem commit last time. One fixed path, one answer.
set REPO=C:\Projects\car-rental-site\car-rental-site
set WANT=6d48f5b7a37fdad15e9f7f593daffe831e3314c6

cd /d "%REPO%" || (echo Cannot find %REPO% & timeout /t 20 & exit /b 1)

echo ============================================================
echo   RentUp  ^>^>  GitHub (main)
echo   Live catalogue: every car sells, page or no page
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

rem Refuse to push blind. The commit below was built on top of a
rem specific origin/main; if GitHub has moved since, forcing the branch
rem to it would try a non-fast-forward push and fail anyway - or, worse,
rem be "fixed" later with a force push that drops somebody's work.
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
  echo   it will rebuild the commit on the current origin/main - it
  echo   takes a minute and loses nothing.
  echo   ============================================================
  echo.
  timeout /t 30
  exit /b 1
)

echo This is one commit on top of origin/main:
echo.
git --no-pager show --stat --oneline %WANT%
echo.

rem NO "git add -A" HERE, ON PURPOSE - your local photo-audit edits
rem stay local. Only the six files above go up.
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
