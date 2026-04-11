# Start both backend and frontend servers
Write-Host "Starting RFQ AI System..." -ForegroundColor Green
Write-Host ""

# Start backend in a new window
Write-Host "Starting backend server on port 8001..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "cd 'c:\Users\pavan\apps-pavan\rfq-ai-system\backend'; python -m uvicorn app.main:app --port 8001; Read-Host 'Press Enter to close backend'"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "Starting frontend (Streamlit)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "cd 'c:\Users\pavan\apps-pavan\rfq-ai-system\frontend'; streamlit run app.py; Read-Host 'Press Enter to close frontend'"

Write-Host ""
Write-Host "Both servers should be starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8001" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Yellow
