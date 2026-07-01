Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot/apps/api'; `$env:PYTHONPATH='$PSScriptRoot/apps/api'; python -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot/apps/web'; `$env:NEXT_PUBLIC_API_BASE_URL='http://localhost:8000/api/v1'; npm run dev"
