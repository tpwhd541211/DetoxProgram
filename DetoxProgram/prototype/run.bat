@echo off
echo Starting Prototype Server...

cd ..\backend
call venv\Scripts\activate
cd ..\prototype

echo Opening Browser...
start http://127.0.0.1:8000

echo Starting Server...
python -m uvicorn app:app --reload --port 8000

pause
