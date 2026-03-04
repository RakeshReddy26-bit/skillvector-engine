import hashlib
import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CACHE_DB = os.getenv("CACHE_DB_PATH", "data/analysis_cache.db")
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))


def _json_default(value):
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return str(value)


def get_cache_key(resume_text: str, job_text: str) -> str:
    import re

    def normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text)
        return text

    stable_resume = normalize(resume_text[:1000])
    stable_job = normalize(job_text)
    combined = stable_resume + stable_job
    return hashlib.sha256(combined.encode()).hexdigest()


def init_cache() -> None:
    directory = os.path.dirname(CACHE_DB)
    if directory:
        os.makedirs(directory, exist_ok=True)

    conn = sqlite3.connect(CACHE_DB)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_cache (
                cache_key TEXT PRIMARY KEY,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                hit_count INTEGER DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_cached_result(resume_text: str, job_text: str) -> Optional[dict]:
    conn = None
    try:
        init_cache()
        cache_key = get_cache_key(resume_text, job_text)
        conn = sqlite3.connect(CACHE_DB)

        cutoff = (datetime.now() - timedelta(hours=CACHE_TTL_HOURS)).isoformat()
        row = conn.execute(
            "SELECT result_json FROM analysis_cache WHERE cache_key = ? AND created_at > ?",
            (cache_key, cutoff),
        ).fetchone()

        if row:
            conn.execute(
                "UPDATE analysis_cache SET hit_count = hit_count + 1 WHERE cache_key = ?",
                (cache_key,),
            )
            conn.commit()
            result = json.loads(row[0])
            result["cached"] = True
            result["latency_ms"] = 0
            logger.info("Cache HIT for key %s...", cache_key[:8])
            return result

        logger.info("Cache MISS for key %s...", cache_key[:8])
        return None
    except Exception as exc:
        logger.warning("Cache read failed, proceeding without cache: %s", exc)
        return None
    finally:
        if conn:
            conn.close()


def save_cached_result(resume_text: str, job_text: str, result: dict) -> None:
    conn = None
    try:
        init_cache()
        cache_key = get_cache_key(resume_text, job_text)
        conn = sqlite3.connect(CACHE_DB)

        value = dict(result)
        value.pop("cached", None)
        value.pop("latency_ms", None)

        conn.execute(
            """
            INSERT OR REPLACE INTO analysis_cache (cache_key, result_json, created_at, hit_count)
            VALUES (?, ?, ?, COALESCE((SELECT hit_count FROM analysis_cache WHERE cache_key = ?), 0))
            """,
            (cache_key, json.dumps(value, default=_json_default), datetime.now().isoformat(), cache_key),
        )
        conn.commit()
    except Exception as exc:
        logger.warning("Cache write failed, continuing without cache persistence: %s", exc)
    finally:
        if conn:
            conn.close()
