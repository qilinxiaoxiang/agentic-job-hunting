from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path


def fingerprint(company: str, role: str, source_url: str) -> str:
    normalized = "|".join(part.casefold().strip().rstrip("/") for part in (company, role, source_url))
    return hashlib.sha256(normalized.encode()).hexdigest()


class TargetLedger:
    def __init__(self, path: str | Path):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS targets(
               fingerprint TEXT PRIMARY KEY, company TEXT NOT NULL, role TEXT NOT NULL,
               source_url TEXT NOT NULL, state TEXT NOT NULL)"""
        )
        self.conn.commit()

    def add(self, *, company: str, role: str, source_url: str) -> bool:
        key = fingerprint(company, role, source_url)
        cursor = self.conn.execute(
            "INSERT OR IGNORE INTO targets VALUES (?,?,?,?,?)",
            (key, company.strip(), role.strip(), source_url.strip(), "discovered"),
        )
        self.conn.commit()
        return cursor.rowcount == 1

    def set_state(self, *, company: str, role: str, source_url: str, state: str) -> None:
        self.conn.execute(
            "UPDATE targets SET state=? WHERE fingerprint=?",
            (state, fingerprint(company, role, source_url)),
        )
        self.conn.commit()
