#!/usr/bin/env powershell
# Restart backend with new extraction code

Write-Host "Attempting to restart backend service..." -ForegroundColor Cyan

# Kill any existing uvicorn processes
$processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"}

if ($processes) {
    Write-Host "Stopping existing uvicorn processes..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Activate conda environment
Write-Host "Activating conda environment..." -ForegroundColor Cyan
$CondaHook = & "$env:CONDA\shell\condabin\conda-hook.ps1"
& $CondaHook

conda activate myenv

# Navigate to backend
cd c:\Users\pavan\apps-pavan\rfq-ai-system\backend

# Start uvicorn
Write-Host "Starting backend on port 8001..." -ForegroundColor Green
python -m uvicorn app.main:app --reload --port 8001

Write-Host "Backend is now running at http://localhost:8001" -ForegroundColor Green
