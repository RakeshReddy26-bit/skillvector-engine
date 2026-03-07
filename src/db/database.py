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
                password_hash TEXT,
                auth_provider TEXT NOT NULL DEFAULT 'email',
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

            -- Skill trend tracking: one row per skill per analysis
            CREATE TABLE IF NOT EXISTS skill_trend_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                match_score REAL NOT NULL,
                target_role TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_ste_skill
                ON skill_trend_events(skill_name);

            CREATE INDEX IF NOT EXISTS idx_ste_created
                ON skill_trend_events(created_at);

            -- Weekly aggregated snapshots for fast trend queries
            CREATE TABLE IF NOT EXISTS skill_trend_snapshots (
                id TEXT PRIMARY KEY,
                week_start TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                gap_frequency INTEGER NOT NULL DEFAULT 0,
                avg_match_score REAL NOT NULL DEFAULT 0,
                top_roles TEXT NOT NULL DEFAULT '[]',
                trend_direction TEXT NOT NULL DEFAULT 'stable',
                created_at TEXT DEFAULT (datetime('now')),
                UNIQUE(week_start, skill_name)
            );

            CREATE INDEX IF NOT EXISTS idx_sts_week
                ON skill_trend_snapshots(week_start);

            CREATE INDEX IF NOT EXISTS idx_sts_skill
                ON skill_trend_snapshots(skill_name);
        """)
        conn.commit()
        # v3 schema migration: add plan/stripe columns (idempotent)
        for alter_sql in [
            "ALTER TABLE users ADD COLUMN plan_tier TEXT NOT NULL DEFAULT 'free'",
            "ALTER TABLE users ADD COLUMN stripe_customer_id TEXT",
            "ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT",
            "ALTER TABLE users ADD COLUMN auth_provider TEXT NOT NULL DEFAULT 'email'",
        ]:
            try:
                conn.execute(alter_sql)
            except sqlite3.OperationalError:
                pass  # Column already exists
        conn.commit()
        logger.info("Database initialized at %s", DB_PATH)
    finally:
        conn.close()
