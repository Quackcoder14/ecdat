@echo off
echo ===================================================
echo Starting ECDAT Platform
echo ===================================================

echo [0/2] Checking and freeing ports 8000 and 3000 if occupied...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000, 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }" >nul 2>&1

timeout /t 1 /nobreak >nul

if not exist "%~dp0services\api\ecdat.db" (
    echo Seeding demo database...
    python "%~dp0scripts\seed.py"
)

echo [1/2] Starting FastAPI Backend on http://localhost:8000...
start "ECDAT Backend (Port 8000)" cmd /k "cd /d %~dp0services\api && python -m uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Next.js Frontend on http://localhost:3000...
start "ECDAT Frontend (Port 3000)" cmd /k "cd /d %~dp0apps\web && npm run dev"

echo.
echo ===================================================
echo ECDAT Platform Launched!
echo - Frontend URL: http://localhost:3000/login
echo - Backend URL:  http://localhost:8000/health
echo - Credentials:  admin@ecdat.demo / demo123
echo ===================================================
pause
