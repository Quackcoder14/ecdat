# ECDAT Platform Launcher
$Root = $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting ECDAT Platform (FastAPI + Next.js)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Write-Host "`n[0/2] Checking and freeing ports 8000 & 3000 if occupied..." -ForegroundColor Gray
Get-NetTCPConnection -LocalPort 8000, 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "Stopping process $($_.OwningProcess) on port $($_.LocalPort)..." -ForegroundColor Yellow
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1

Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root/services/api'; python -m uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root/apps/web'; npm run dev"

Write-Host "`nServers launched in separate windows!" -ForegroundColor Cyan
Write-Host " - Frontend:    http://localhost:3000/login" -ForegroundColor Yellow
Write-Host " - Backend API: http://localhost:8000/health" -ForegroundColor Yellow
Write-Host " - Credentials: admin@ecdat.demo / demo123" -ForegroundColor White
Write-Host "===================================================" -ForegroundColor Cyan
