# PitchLens AI - Local Development Runner
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " ⚽ PitchLens AI - Premier League Broadcasting Copilot" -ForegroundColor Yellow
Write-Host " Inside the Game: Developer Hackathon (Microsoft)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$CurrentDir = Get-Location

# 1. Start Backend in a background process or new terminal
Write-Host "`n[1/2] Starting Python Backend on http://localhost:8000..." -ForegroundColor Cyan
$BackendProcess = Start-Process py -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory "$CurrentDir\backend" -PassThru

# Wait 2 seconds for backend initialization
Start-Sleep -Seconds 2

# 2. Start Frontend
Write-Host "[2/2] Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Cyan
Write-Host "`n🚀 Application running! Open http://localhost:5173 in your browser." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor Yellow

Set-Location "$CurrentDir\frontend"
npm run dev

# Cleanup when frontend exits
Stop-Process -Id $BackendProcess.Id -Force -ErrorAction SilentlyContinue
Set-Location $CurrentDir
