# Realtime Network Expert (Local Windows App)

This is a local app you can run on Windows that:
- captures a full monitor screenshot in near-real-time,
- sends it to OpenAI for analysis,
- infers likely tool/vendor context (Cisco / Fortinet / Palo Alto / other),
- gives one immediate recommendation at a time,
- waits for you to press **NEXT** before moving to the next queued suggestion,
- remembers previous scenarios and attempts in SQLite so it can avoid repeating failed steps.

## Important note
This starter currently analyzes **screen visuals**. It does **not yet ingest live Teams audio directly**. You can still use it during Teams calls by sharing/placing troubleshooting output on screen. Audio/transcript integration can be added next.

## 1) Setup (Windows)

1. Install Python 3.11+.
2. Open PowerShell in this folder.
3. Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Edit `.env` and set `OPENAI_API_KEY`.

## 2) Run

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open <http://localhost:8000>.

## 3) Workflow

1. Click **Start Monitoring**.
2. The app analyzes frames every few seconds.
3. Execute the shown recommendation.
4. Enter result in the textbox.
5. Click **NEXT** to move to the next suggestion.
6. If queue is empty, wait for the next analysis cycle.

## Architecture

- `app/capture.py`: monitor screenshot capture (MSS).
- `app/agent.py`: OpenAI vision + JSON recommendation generation.
- `app/memory.py`: persistent scenario/attempt memory (SQLite).
- `app/main.py`: FastAPI server + monitor loop + NEXT control.
- `templates/index.html`: local UI.

## Security & privacy

- Treat this as sensitive: screenshots may contain secrets, internal IPs, and credentials.
- Use minimum required monitor and avoid showing unrelated sensitive data.
- Keep API keys in `.env` only.

## Next recommended enhancements

- Teams audio transcription (WASAPI loopback + Realtime API).
- Explicit vendor skill packs (Cisco/Fortinet/Palo Alto playbooks + command parsers).
- OCR pre-processing for dense console text.
- Better “attempt outcome” tagging (success/failed/partial) to improve reasoning.
