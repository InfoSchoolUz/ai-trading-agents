@echo off
setlocal

cd /d %~dp0\..\..

if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate
pip install -r frontend\requirements.txt

streamlit run frontend\streamlit_app.py
