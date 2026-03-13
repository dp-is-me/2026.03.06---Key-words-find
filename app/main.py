import os
import threading
import time
from collections import deque
from pathlib import Path
from typing import Deque, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .agent import NetworkExpertAgent
from .capture import ScreenCapture
from .memory import SessionMemory

load_dotenv()

app = FastAPI(title="Realtime Network Expert")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

memory = SessionMemory(db_path=os.getenv("MEMORY_DB", "session_memory.db"))
capture = ScreenCapture(monitor_index=int(os.getenv("MONITOR_INDEX", "1")))
agent = NetworkExpertAgent()

suggestion_queue: Deque[str] = deque()
current: Dict[str, str] = {
    "toolset": "Unknown",
    "summary": "Not started.",
    "recommended_action": "Click Start Monitoring.",
    "confidence": "low",
}

running = False
worker: Optional[threading.Thread] = None
lock = threading.Lock()


def monitor_loop() -> None:
    global current
    interval = float(os.getenv("ANALYZE_INTERVAL_SEC", "4"))

    while running:
        frame = capture.grab_frame_base64()
        if not frame:
            time.sleep(interval)
            continue

        context = memory.recent_context(limit=12)
        try:
            suggestion = agent.analyze_frame(frame, context)
        except Exception as exc:  # noqa: BLE001
            suggestion = {
                "toolset": "Unknown",
                "summary": f"Analysis error: {exc}",
                "recommended_action": "Check API key/model and restart monitoring.",
                "follow_up_actions": [],
                "confidence": "low",
            }

        with lock:
            current = {
                "toolset": suggestion.get("toolset", "Unknown"),
                "summary": suggestion.get("summary", ""),
                "recommended_action": suggestion.get("recommended_action", ""),
                "confidence": suggestion.get("confidence", "low"),
            }
            suggestion_queue.clear()
            for step in suggestion.get("follow_up_actions", []):
                suggestion_queue.append(step)

        memory.add_scenario("frame analyzed", suggestion)
        time.sleep(interval)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/start")
def start_monitoring():
    global running, worker
    if running:
        return JSONResponse({"status": "already_running"})
    running = True
    worker = threading.Thread(target=monitor_loop, daemon=True)
    worker.start()
    return JSONResponse({"status": "started"})


@app.post("/stop")
def stop_monitoring():
    global running
    running = False
    return JSONResponse({"status": "stopped"})


@app.get("/state")
def state():
    with lock:
        return JSONResponse({
            "running": running,
            "current": current,
            "queued_actions": list(suggestion_queue),
        })


@app.post("/next")
def next_suggestion(result_note: str = Form("not provided")):
    with lock:
        memory.add_attempt(current.get("recommended_action", ""), result_note)
        if suggestion_queue:
            current["recommended_action"] = suggestion_queue.popleft()
        else:
            current["recommended_action"] = "No queued actions. Wait for next analysis cycle."

        return JSONResponse({"current": current, "queued_actions": list(suggestion_queue)})
