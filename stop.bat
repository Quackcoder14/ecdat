@echo off
echo ===================================================
echo Stopping ECDAT Platform (Ports 8000 and 3000)
echo ===================================================
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000, 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Write-Host 'Stopping PID ' $_.OwningProcess ' on port ' $_.LocalPort; Stop-Process -Id $_.OwningProcess -Force }"
echo.
echo Servers stopped. Ports 8000 and 3000 are now free.
pause
