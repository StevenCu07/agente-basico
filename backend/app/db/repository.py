from datetime import datetime, timezone
from sqlite3 import Connection
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def current_year_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def get_or_create_user(conn: Connection, user_token: str) -> int:
    row = conn.execute("SELECT id FROM users WHERE user_token = ?", (user_token,)).fetchone()
    if row:
        return int(row["id"])

    cursor = conn.execute(
        "INSERT INTO users (user_token, created_at) VALUES (?, ?)",
        (user_token, now_iso()),
    )
    return int(cursor.lastrowid)


def save_document(conn: Connection, user_id: int, title: str, content: str, embedding_json: str | None = None) -> int:
    cursor = conn.execute(
        """
        INSERT INTO documents (user_id, title, content, embedding_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, title, content, embedding_json, now_iso()),
    )
    return int(cursor.lastrowid)


def list_documents(conn: Connection, user_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, title, content, created_at FROM documents WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def record_interaction(
    conn: Connection,
    user_id: int,
    tool: str,
    input_chars: int,
    output_chars: int,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    estimated_cost: float,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO interactions
        (user_id, tool, input_chars, output_chars, prompt_tokens, completion_tokens, total_tokens, estimated_cost, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            tool,
            input_chars,
            output_chars,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            estimated_cost,
            now_iso(),
        ),
    )

    ym = current_year_month()
    existing = conn.execute(
        "SELECT id, total_tokens, total_cost, interaction_count FROM monthly_aggregates WHERE user_id = ? AND year_month = ?",
        (user_id, ym),
    ).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE monthly_aggregates
            SET total_tokens = ?, total_cost = ?, interaction_count = ?
            WHERE id = ?
            """,
            (
                int(existing["total_tokens"]) + total_tokens,
                float(existing["total_cost"]) + estimated_cost,
                int(existing["interaction_count"]) + 1,
                int(existing["id"]),
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO monthly_aggregates (user_id, year_month, total_tokens, total_cost, interaction_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, ym, total_tokens, estimated_cost, 1),
        )

    return int(cursor.lastrowid)


def get_user_metrics(conn: Connection, user_token: str) -> dict[str, Any] | None:
    user = conn.execute("SELECT id, user_token FROM users WHERE user_token = ?", (user_token,)).fetchone()
    if not user:
        return None

    ym = current_year_month()
    agg = conn.execute(
        "SELECT total_tokens, total_cost, interaction_count FROM monthly_aggregates WHERE user_id = ? AND year_month = ?",
        (int(user["id"]), ym),
    ).fetchone()

    if not agg:
        return {
            "user_token": user_token,
            "month": ym,
            "total_tokens": 0,
            "total_cost": 0.0,
            "interactions": 0,
        }

    return {
        "user_token": user_token,
        "month": ym,
        "total_tokens": int(agg["total_tokens"]),
        "total_cost": float(agg["total_cost"]),
        "interactions": int(agg["interaction_count"]),
    }


def get_global_metrics(conn: Connection) -> dict[str, Any]:
    ym = current_year_month()
    row = conn.execute(
        """
        SELECT COALESCE(SUM(total_tokens), 0) AS total_tokens,
               COALESCE(SUM(total_cost), 0) AS total_cost,
               COALESCE(SUM(interaction_count), 0) AS interactions,
               COUNT(*) AS active_users
        FROM monthly_aggregates
        WHERE year_month = ?
        """,
        (ym,),
    ).fetchone()

    return {
        "month": ym,
        "total_tokens": int(row["total_tokens"]),
        "total_cost": float(row["total_cost"]),
        "interactions": int(row["interactions"]),
        "active_users": int(row["active_users"]),
    }

