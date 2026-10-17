@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================================
echo   RentUp AI  ^>^>  Cloudflare Worker deploy
echo ==========================================================
echo.
echo [1/3] Cloudflare login - browser will open, press Allow...
call npx --yes wrangler@4 login
echo.
echo [2/3] Deploy (first time without the key)...
call npx --yes wrangler@4 deploy
echo.
echo [3/3] Paste your Anthropic API key and press Enter (it is not shown)...
call npx --yes wrangler@4 secret put ANTHROPIC_API_KEY
echo.
echo ==========================================================
echo   Done. Copy the https://rentup-ai....workers.dev address
echo   printed above into content/settings/site.yml
echo   (ai_assistant: endpoint) - or send it to Claude.
echo ==========================================================
pause
