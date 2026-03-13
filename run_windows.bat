@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
echo Fill OPENAI_API_KEY in .env, then run:
echo uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
