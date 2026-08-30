@echo off
chcp 65001 >nul
cd /d "%~dp0"
set LOG=%~dp0deploy-rules.log
echo ============================================================ > "%LOG%"
echo   Firestore rules deploy  --  %DATE% %TIME% >> "%LOG%"
echo ============================================================ >> "%LOG%"
echo.
echo Deploying firestore.rules to project rentup-ge...
echo.

where firebase >nul 2>&1
if errorlevel 1 (
  echo FIREBASE-CLI-NOT-FOUND >> "%LOG%"
  echo   Firebase CLI is not installed.
  echo   Install it with:  npm install -g firebase-tools
  goto done
)

echo CLI found >> "%LOG%"
call firebase deploy --only firestore:rules --project rentup-ge >> "%LOG%" 2>&1
set RC=%ERRORLEVEL%
echo EXITCODE=%RC% >> "%LOG%"

if %RC%==0 (
  echo   OK - rules published.
) else (
  echo   FAILED - exit code %RC%. See deploy-rules.log
)

:done
echo.
type "%LOG%"
echo.
timeout /t 25
