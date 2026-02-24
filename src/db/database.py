"""SQLite database management for SkillVector Engine."""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "skillvector.db"


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Initialize the database schema."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_text TEXT NOT NULL,
                job_text TEXT NOT NULL,
                match_score REAL NOT NULL,
                learning_priority TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_analyses_user
                ON analyses(user_id);

            CREATE INDEX IF NOT EXISTS idx_analyses_created
                ON analyses(created_at);

            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                user_id TEXT,
                is_positive INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
        # v3 schema migration: add plan/stripe columns (idempotent)
        for alter_sql in [
            "ALTER TABLE users ADD COLUMN plan_tier TEXT NOT NULL DEFAULT 'free'",
            "ALTER TABLE users ADD COLUMN stripe_customer_id TEXT",
            "ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT",
        ]:
            try:
                conn.execute(alter_sql)
            except sqlite3.OperationalError:
                pass  # Column already exists
        conn.commit()
        logger.info("Database initialized at %s", DB_PATH)
    finally:
        conn.close()
