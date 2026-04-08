@echo off
setlocal

cd /d %~dp0\..\..

if not exist backend\.env copy backend\.env.example backend\.env

if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate
pip install -r backend\requirements.txt

uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
