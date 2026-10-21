"""Persistent state that makes runs repeatable: stable record IDs, OCR cache, manual resolution edits."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS record_ids (record_key TEXT PRIMARY KEY, record_id TEXT UNIQUE, first_seen TEXT);
CREATE TABLE IF NOT EXISTS ocr_cache (sha256 TEXT, languages TEXT, status TEXT, text TEXT,
                                      PRIMARY KEY (sha256, languages));
CREATE TABLE IF NOT EXISTS manual_updates (record_id TEXT PRIMARY KEY, resolution_status TEXT,
                                           assigned_to TEXT, resolution_notes TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS runs (run_at TEXT, summary TEXT);
"""


class StateStore:
    def __init__(self, path: Path, prefix: str = "GPS"):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.prefix = prefix

    def record_id(self, record_key: str) -> str:
        row = self.conn.execute("SELECT record_id FROM record_ids WHERE record_key=?", (record_key,)).fetchone()
        if row:
            return row[0]
        n = self.conn.execute("SELECT COUNT(*) FROM record_ids").fetchone()[0] + 1
        rid = f"{self.prefix}-{n:05d}"
        self.conn.execute("INSERT INTO record_ids VALUES (?,?,?)", (record_key, rid, datetime.now().isoformat()))
        return rid

    def first_seen(self, record_id: str) -> str | None:
        row = self.conn.execute("SELECT first_seen FROM record_ids WHERE record_id=?", (record_id,)).fetchone()
        return row[0] if row else None

    def get_ocr(self, sha: str, languages: str):
        row = self.conn.execute("SELECT status, text FROM ocr_cache WHERE sha256=? AND languages=?",
                                (sha, languages)).fetchone()
        return (row[0], row[1]) if row else None

    def put_ocr(self, sha: str, languages: str, status: str, text: str) -> None:
        self.conn.execute("INSERT OR REPLACE INTO ocr_cache VALUES (?,?,?,?)", (sha, languages, status, text))

    def manual_updates(self) -> dict[str, dict]:
        rows = self.conn.execute("SELECT record_id, resolution_status, assigned_to, resolution_notes FROM manual_updates")
        return {r[0]: {"Resolution Status": r[1], "Assigned To": r[2], "Resolution Notes": r[3]} for r in rows}

    def save_manual_update(self, record_id: str, status: str | None, assigned: str | None, notes: str | None) -> None:
        self.conn.execute("INSERT OR REPLACE INTO manual_updates VALUES (?,?,?,?,?)",
                          (record_id, status, assigned, notes, datetime.now().isoformat()))

    def log_run(self, summary: dict) -> None:
        self.conn.execute("INSERT INTO runs VALUES (?,?)", (datetime.now().isoformat(), json.dumps(summary, default=str)))

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()
