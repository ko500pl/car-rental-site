@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   RentUp Leasor -- Google-tan dakavshireba da angarishis shemowmeba
echo   (Firebase CLI-s ukve avtorizebuls iyenebs)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0rentup-setup.ps1" > "%~dp0rentup-setup.log" 2>&1
type "%~dp0rentup-setup.log"
echo.
echo   shedegi: rentup-setup.log
timeout /t 40
