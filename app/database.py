import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "data/csa_planner.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_ref TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                system_name TEXT NOT NULL,
                gamp_category TEXT NOT NULL,
                intended_use TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'planned',
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assurance_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL REFERENCES assessments(id),
                requirement_ref TEXT NOT NULL,
                function_name TEXT NOT NULL,
                csa_class TEXT NOT NULL,
                rationale TEXT NOT NULL,
                test_strategy TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL REFERENCES assessments(id),
                reviewer TEXT NOT NULL,
                decision TEXT NOT NULL,
                comment TEXT,
                reviewed_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                detail TEXT,
                created_at TEXT NOT NULL
            );
        """)
    conn.close()
