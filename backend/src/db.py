from __future__ import annotations

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "migrations"


def get_connection():
    """Open one short-lived connection; transaction lifetime is the context."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "app_db"),
        user=os.getenv("DB_USER", "app_user"),
        password=os.getenv("DB_PASSWORD", "app_password"),
        row_factory=dict_row,
    )


def init_db() -> None:
    """Apply ordered, idempotently recorded SQL migrations."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                name TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

    for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM schema_migrations WHERE name = %s",
                (migration.name,),
            )
            if cur.fetchone():
                continue

            sql = migration.read_text(encoding="utf-8")
            for statement in sql.split(";"):
                if statement.strip():
                    cur.execute(statement)
            cur.execute(
                "INSERT INTO schema_migrations (name) VALUES (%s)",
                (migration.name,),
            )
