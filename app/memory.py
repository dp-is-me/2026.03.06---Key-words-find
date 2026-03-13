import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class SessionMemory:
    def __init__(self, db_path: str = "session_memory.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    frame_note TEXT NOT NULL,
                    suggestion_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL
                )
                """
            )

    def add_scenario(self, frame_note: str, suggestion: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO scenarios (created_at, frame_note, suggestion_json) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), frame_note, json.dumps(suggestion)),
            )

    def add_attempt(self, action: str, result: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO attempts (created_at, action, result) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), action, result),
            )

    def recent_context(self, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        with self._connect() as conn:
            scenarios = conn.execute(
                "SELECT created_at, frame_note, suggestion_json FROM scenarios ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            attempts = conn.execute(
                "SELECT created_at, action, result FROM attempts ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()

        return {
            "scenarios": [
                {
                    "created_at": row[0],
                    "frame_note": row[1],
                    "suggestion": json.loads(row[2]),
                }
                for row in scenarios
            ],
            "attempts": [
                {"created_at": row[0], "action": row[1], "result": row[2]}
                for row in attempts
            ],
        }
